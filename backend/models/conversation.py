from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
import uuid

class Message(BaseModel):
    content: str
    sender: str  # "user" or "assistant"
    timestamp: datetime = Field(default_factory=datetime.now)

class Conversation(BaseModel):
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    messages: List[Message] = []
    deleted: bool = False

class Config:
    json_schema_extra = {
        "example": {
            "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "user123",
            "messages": [
                {"sender": "user", "content": "Hi, how are you?", "timestamp": "2025-02-17T14:32:01"},
                {"sender": "bot", "content": "I'm good, thanks for asking!", "timestamp": "2025-02-17T14:32:05"}
            ],
            "deleted": False
        }
    } 