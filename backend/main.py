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
from database.mongodb import MongoDB  # Add this import



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

@app.on_event("startup")
async def startup_event():
    """Initialize databases"""
    logger.info("Initializing databases")
    await MongoDB.connect_db()
    initialize_db()  # Existing vector DB initialization
    logger.info("Database initialization complete")

@app.post("/conversations")
async def create_conversation(conversation: Conversation):
    logger.info(f"Creating conversation {conversation.conversation_id} for user {conversation.user_id}")
    try:
        for msg in conversation.messages:
            if not msg.timestamp:
                msg.timestamp = datetime.now().isoformat()
        
        # Updated to use MongoDB class
        result = await MongoDB.create_conversation(conversation.dict())
        logger.debug(f"Conversation stored with id: {result['_id']}")
        return conversation
    except Exception as e:
        logger.error(f"Conversation creation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations")
async def get_conversations(user_id: str) -> List[Conversation]:
    logger.info(f"Fetching conversations for user {user_id}")
    try:
        # Updated to use MongoDB class
        conversations = await MongoDB.get_conversations(user_id)
        return [Conversation(**doc) for doc in conversations]
    except Exception as e:
        logger.error(f"Conversation fetch failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    logger.info(f"Deleting conversation {conversation_id}")
    try:
        # Updated to use MongoDB class
        success = await MongoDB.soft_delete_conversation(conversation_id)
        if not success:
            logger.warning(f"Conversation {conversation_id} not found")
            raise HTTPException(status_code=404, detail="Conversation not found")
            
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