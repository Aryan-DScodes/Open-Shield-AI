from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class ChatMessage(BaseModel):
    role: str = Field(..., example="user")
    content: str | List[Dict[str, Any]] = Field(..., description="Accepts Text or Multimodal JSON")

class ProxyRequest(BaseModel):
    model: str = Field(..., example="gpt-4o")
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    user_id: str = Field(..., description="Unique identifier for Redis rate limiting")

class Choice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ProxyResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Dict[str, int]
    x_cache_hit: bool = Field(False, description="True if served from Redis Semantic Cache")
    x_pii_redacted: bool = Field(False, description="True if visual/text PII was masked")