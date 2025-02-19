from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional, List, Dict, Any

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_db(cls):
        cls.client = AsyncIOMotorClient("mongodb://localhost:27017/")
        cls.db = cls.client.chat_db  # Changed from chatbot to match your DB name
        
    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    def get_db(cls):
        return cls.db

    # New CRUD operations for conversations
    @classmethod
    async def create_conversation(cls, conversation: Dict[str, Any]) -> Dict[str, Any]:
        result = await cls.db.conversations.insert_one(conversation)
        return {**conversation, "_id": str(result.inserted_id)}

    @classmethod
    async def get_conversations(cls, user_id: str) -> List[Dict[str, Any]]:
        cursor = cls.db.conversations.find({
            "user_id": user_id,
            "deleted": False
        })
        return [doc async for doc in cursor]

    @classmethod
    async def soft_delete_conversation(cls, conversation_id: str) -> bool:
        result = await cls.db.conversations.update_one(
            {"conversation_id": conversation_id},
            {"$set": {"deleted": True}}
        )
        return result.matched_count > 0