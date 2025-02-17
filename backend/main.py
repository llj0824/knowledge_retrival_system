from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.llm_service import get_llm_response
from services.vector_db_service import retrieve_from_vector_db, initialize_db
from services.search_service import get_client_status_from_web

app = FastAPI()

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
    """Initialize the vector database with example documents"""
    initialize_db()

@app.post("/chat")
async def chat(request: ChatRequest):
    query = request.query
    
    # Decision logic based on query type
    if "policy" in query.lower():
        response = retrieve_from_vector_db(query)
    elif "client status" in query.lower():
        response = get_client_status_from_web(query)
    else:
        response = get_llm_response(query)
    
    return {"answer": response}