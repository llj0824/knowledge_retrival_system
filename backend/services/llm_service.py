import os
from dotenv import load_dotenv
import logging
from fastapi import Depends
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    # Model constants
    GPT_4o = "chatgpt-4o-latest";
    GPT_o3_mini = "o3-mini";
    GPT_4o_mini = "gpt-4o-mini"
      
    def __init__(self):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        
    def call_openai(self, messages: list,  # Make messages required
                         model: str = GPT_4o, max_tokens: int = 10000, 
                         temperature: float = 0.1, reasoning_effort: str = 'high') -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                # reasoning_effort=reasoning_effort
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"Error processing request: {str(e)}"
          
    def get_llm_response(self,
        query: str,
        history: list = []
    ) -> str:
        """Get response using injected service instance"""
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant"},
                *[{"role": "user", "content": msg} for msg in history],
                {"role": "user", "content": query}
            ]
            
            response = self.call_openai(messages=messages)
            logger.info(f"LLM Raw Response: {response}")
            return response
        except Exception as e:
            logger.error(f"LLM Error: {str(e)}", exc_info=True)
            return f"Error processing request: {str(e)}"