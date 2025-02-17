import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

load_dotenv()

# Initialize Chroma client with persistence
client = chromadb.Client(chromadb.Settings(
    persist_directory="./data/chroma_db"
))

local_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"  # Lightweight model
)
default_ef = local_ef

# Create or get collection 
collection = client.get_or_create_collection(
    name="company-policy-documents",
    embedding_function=default_ef
)

def add_documents(documents: list[str], ids: list[str], metadatas: list[dict] = None):
    """Add documents to the vector database"""
    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )

def retrieve_from_vector_db(query: str) -> str:
    """Query the vector database"""
    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    
    if results and results['documents'] and results['documents'][0]:
        return results['documents'][0][0]
    return "No relevant information found."

def initialize_db():
    """Initialize the database with example documents"""
    # Only initialize if collection is empty
    if collection.count() == 0:
        example_docs = [
            "Our company's work from home policy allows employees to work remotely two days per week.",
            "The annual leave policy provides 20 days of paid vacation per year.",
            "Our healthcare benefits include dental and vision coverage for all full-time employees."
        ]
        
        example_ids = ["policy1", "policy2", "policy3"]
        
        example_metadata = [
            {"type": "work_policy", "department": "HR"},
            {"type": "leave_policy", "department": "HR"},
            {"type": "benefits", "department": "HR"}
        ]
        
        add_documents(example_docs, example_ids, example_metadata)