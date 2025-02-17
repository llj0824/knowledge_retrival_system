import os
import aiohttp
from dotenv import load_dotenv
import logging
from fastapi import Depends

# Add this at module level
_llm_service_instance = None
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    # Model constants
    GPT_4o = "chatgpt-4o-latest";
    GPT_o3_mini = "o3-mini";
    GPT_4o_mini = "gpt-4o-mini"
      
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.endpoint = "https://api.openai.com/v1/chat/completions"
        
        # System roles/prompts can be defined here as class attributes
        self.system_role = "You are a helpful assistant."
        
        # One-time initialization logic here
        logger.info("Initializing LLMService")
    
    async def call_openai(self, prompt: str, system_role: str = None, 
                         model: str = GPT_4o, max_tokens: int = 10000, 
                         temperature: float = 0.1) -> str:
        if not self.api_key:
            raise ValueError("OpenAI API key is not set")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Check if it's a reasoning model (starts with 'o')
        is_reasoning_model = model.startswith('o')
        
        if is_reasoning_model:
            # Reasoning models don't support system messages, so combine them
            combined_prompt = f"{prompt}\n\n{system_role}\n" if system_role else prompt
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": combined_prompt}
                ],
                "reasoning_effort": "high"  # Only parameter supported by o-series
            }
        else:
            # Standard payload for non-reasoning models
            messages = []
            if system_role:
                messages.append({"role": "system", "content": system_role})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_completion_tokens": max_tokens
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.endpoint, json=payload, headers=headers) as response:
                if not response.ok:
                    error_data = await response.json()
                    raise ValueError(f"OpenAI API error: {response.status} - {error_data}")
                    
                data = await response.json()
                return data["choices"][0]["message"]["content"].strip()

# FastAPI dependency
async def get_llm_service() -> LLMService:
    """Dependency that returns a single LLMService instance"""
    return LLMService()

async def get_llm_response(
    query: str,
    llm_service: LLMService = Depends(get_llm_service)
) -> str:
    """Get response using injected service instance"""
    logger.info(f"LLM Query: {query[:50]}...")  # Log first 50 chars to avoid sensitive data
    try:
        response = await llm_service.call_openai(query)
        logger.debug(f"LLM Raw Response: {response}")
        return response
    except Exception as e:
        logger.error(f"LLM Error: {str(e)}", exc_info=True)
        return f"Error processing request: {str(e)}"