import requests
import os
import logging
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()
logger = logging.getLogger(__name__)

def get_client_status_from_web(query: str, site_filter: str = None) -> str:
    """Enhanced web search with site filtering and better result parsing"""
    try:
        # Build search query with optional site filter
        search_query = f'site:{site_filter} {query}' if site_filter else query
        encoded_query = quote_plus(search_query)
        
        params = {
            'q': encoded_query,
            'api_key': os.getenv('SERPAPI_API_KEY'),
            'location': 'United States',
            'hl': 'en',
            'gl': 'us',
            'num': 5  # Get more results for better context
        }

        search_url = "https://api.serpapi.com/search"
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        logger.debug(f"Search API response: {data}")

        # Extract and combine relevant snippets
        if 'organic_results' not in data:
            return "No relevant information found."
            
        snippets = [
            f"Source: {result.get('source', 'Unknown')}\n"
            f"Content: {result['snippet']}\n"
            for result in data['organic_results'][:3]  # Use top 3 results
            if 'snippet' in result
        ]

        return "\n\n".join(snippets) if snippets else "No actionable insights found."

    except requests.exceptions.RequestException as e:
        logger.error(f"Search API error: {str(e)}")
        return "Error retrieving web results. Please try again later."
    except Exception as e:
        logger.error(f"Unexpected search error: {str(e)}", exc_info=True)
        return "Failed to process search results."