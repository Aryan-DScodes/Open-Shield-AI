import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app, Counter, Histogram

from app.api.routes import router, redis_client, semantic_cache
from app.services.upstream_proxy import upstream_client
from app.core.config import settings

# 1. Define Prometheus Metrics
REQUEST_COUNT = Counter(
    "gateway_requests_total",
    "Total HTTP requests handled by the gateway",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "gateway_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"]
)

# 2. Define App Lifespan (Startup & Shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Redis Vector Search Index automatically
    await semantic_cache.init_index()
    yield
    # Shutdown: Graceful connection cleanup
    await upstream_client.close()
    await redis_client.aclose()

# 3. Initialize FastAPI App
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Enterprise GenAI Gateway with Real-Time Guardrails & Semantic Cache",
    lifespan=lifespan
)

# 4. Attach CORS Middleware (Allows Next.js/v0 dashboard calls)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Metrics Tracking Middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time
    
    endpoint = request.url.path
    if endpoint != "/metrics":
        REQUEST_COUNT.labels(
            method=request.method, 
            endpoint=endpoint, 
            status=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
        
    return response

# 6. Mount Prometheus & Core Routes
app.mount("/metrics", make_asgi_app())
app.include_router(router)