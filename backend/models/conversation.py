from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    sender: str
    text: str
    timestamp: Optional[str] = None

class Conversation(BaseModel):
    conversation_id: str
    user_id: str
    messages: List[Message]
    deleted: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "14:32 17/02/2025",
                "user_id": "user123",
                "messages": [
                    {"sender": "user", "text": "Hi, how are you?", "timestamp": "2025-02-17T14:32:01"},
                    {"sender": "bot", "text": "I'm good, thanks for asking!", "timestamp": "2025-02-17T14:32:05"}
                ],
                "deleted": False
            }
        } 