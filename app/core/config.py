from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    api_title: str = "Open Shield API Gateway"
    api_version: str = "1.0.0"
    
    # Redis Configuration
    redis_url: str = Field("redis://localhost:6379/0", description="Redis connection string")
    
    # Upstream APIs
    upstream_llm_api_url: str = Field("https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", description="Upstream API base URL")
    upstream_api_key: str = Field(..., description="API key for upstream provider")
    
    # Middleware Thresholds
    rate_limit_requests: int = Field(100, description="Requests allowed per window")
    rate_limit_window_sec: int = Field(60, description="Rate limit sliding window in seconds")
    semantic_cache_threshold: float = Field(0.92, description="Cosine similarity threshold for cache hit")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()