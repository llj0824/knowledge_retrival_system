import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.llm_service import LLMService
from services.vector_db_service import retrieve_from_vector_db, initialize_db
from services.search_service import get_client_status_from_web
from models.conversation import Conversation, Message
from datetime import datetime
from typing import List



# Disable tokenizers parallelism to prevent deadlocks when forking processes
# This is needed because the Hugging Face tokenizers library uses parallelism
# which can cause issues with FastAPI's process management
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()
llm_service = LLMService()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

# In-memory storage for demonstration (replace with database in production)
conversations_db: dict[str, Conversation] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the vector database with example documents"""
    logger.info("Initializing vector database")
    initialize_db()
    logger.info("Vector database initialization complete")

@app.post("/conversations")
async def create_conversation(conversation: Conversation):
    logger.info(f"Creating conversation {conversation.conversation_id} for user {conversation.user_id}")
    try:
        # Add timestamps to messages if not present
        for msg in conversation.messages:
            if not msg.timestamp:
                msg.timestamp = datetime.now().isoformat()
        
        conversations_db[conversation.conversation_id] = conversation
        logger.debug(f"Conversation stored: {conversation.conversation_id}")
        return conversation
    except Exception as e:
        logger.error(f"Conversation creation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations")
async def get_conversations(user_id: str) -> List[Conversation]:
    logger.info(f"Fetching conversations for user {user_id}")
    try:
        user_conversations = [
            conv for conv in conversations_db.values() 
            if conv.user_id == user_id and not conv.deleted
        ]
        logger.debug(f"Found {len(user_conversations)} conversations for user {user_id}")
        return user_conversations
    except Exception as e:
        logger.error(f"Conversation fetch failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    logger.info(f"Deleting conversation {conversation_id}")
    try:
        if conversation_id not in conversations_db:
            logger.warning(f"Conversation {conversation_id} not found")
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        # Soft delete the conversation
        conversations_db[conversation_id].deleted = True
        logger.debug(f"Successfully deleted conversation {conversation_id}")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversation deletion failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(
    request: ChatRequest
):
    logger.info(f"Received chat request: {request.query}")
    
    query = request.query
    
    try:
        if "policy" in query.lower():
            logger.debug("Routing to vector DB lookup")
            response = retrieve_from_vector_db(query)
        elif "client status" in query.lower():
            logger.debug("Routing to web search")
            response = get_client_status_from_web(query)
        else:
            logger.debug("Routing to LLM")
            response = llm_service.get_llm_response(query=query)
            
        logger.info(f"Chat response generated: {response[:100]}...")  # Truncate long responses
        return {"answer": response}
        
    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}", exc_info=True)
        return {"answer": "Error processing request"}