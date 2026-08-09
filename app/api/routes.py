import redis.asyncio as redis
from fastapi import APIRouter, Header, HTTPException
from typing import Optional

from app.models.schemas import ProxyRequest, ProxyResponse
from app.middleware.rate_limiter import RateLimiter
from app.middleware.semantic_cache import SemanticCache
from app.middleware.pii_redactor import VisualPIIRedactor
from app.services.upstream_proxy import upstream_client
from app.core.config import settings

router = APIRouter()

# Instantiate shared dependencies
redis_client = redis.from_url(settings.redis_url)
rate_limiter = RateLimiter(redis_client)
semantic_cache = SemanticCache(redis_client, threshold=settings.semantic_cache_threshold)
pii_redactor = VisualPIIRedactor()

@router.post(
    "/v1/chat/completions",
    response_model=ProxyResponse,
    summary="Proxy Endpoint with Guardrails & Cache"
)
async def chat_completions(
    request: ProxyRequest,
    authorization: Optional[str] = Header(None)
):
    # Step 1: Enforce Rate Limiting
    await rate_limiter.check_rate_limit(
        user_id=request.user_id,
        limit=settings.rate_limit_requests,
        window_sec=settings.rate_limit_window_sec
    )

    # Step 2: Sanitize Payload (Visual PII Redaction)
    raw_messages = [msg.model_dump() for msg in request.messages]
    sanitized_messages, pii_redacted = await pii_redactor.sanitize_payload(raw_messages)

    # Extract primary text prompt for caching key
    latest_prompt = str(sanitized_messages[-1]["content"]) if sanitized_messages else ""

    # Step 3: Check Semantic Cache
    cached_data = await semantic_cache.check_cache(latest_prompt)
    if cached_data:
        cached_data["x_cache_hit"] = True
        cached_data["x_pii_redacted"] = pii_redacted
        return ProxyResponse(**cached_data)

    # Step 4: Forward to Upstream API (Cache Miss)
    payload = request.model_dump()
    payload["messages"] = sanitized_messages
    
    # Remove user_id so Google's strict API schema validator doesn't reject it
    payload.pop("user_id", None)

    upstream_response = await upstream_client.forward_request(payload, api_key=authorization)

    # Step 5: Save Response to Cache
    await semantic_cache.store_cache(latest_prompt, upstream_response)

    # Step 6: Return Response with Gateway Headers
    upstream_response["x_cache_hit"] = False
    upstream_response["x_pii_redacted"] = pii_redacted
    return ProxyResponse(**upstream_response)