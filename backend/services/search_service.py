import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_client_status_from_web(query: str) -> str:
    search_url = f"https://api.serpapi.com/search?q={query}&api_key={os.getenv('SERPAPI_API_KEY')}"
    response = requests.get(search_url).json()
    return response['organic_results'][0]['snippet'] if response['organic_results'] else "Client status not found."