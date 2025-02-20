from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from services.llm_service import LLMService
import json

class QueryRouter:
    def __init__(self):
        self.llm_service = LLMService()
        self.template = """
        Analyze the user's query and choose the best response method:
        Options:
        - vector: VitaDAO research papers, tokenomics docs, internal knowledge
        - search_focused: Recent updates, specific site content (use site:vitadao.com)
        - search_general: Market trends, non-VitaDAO specific info
        - llm: General knowledge, conceptual questions
        
        Query: {query}
        
        Respond ONLY with JSON: {{"action": "...", "params": {{...}}}}
        """
        
    async def route_query(self, query: str) -> dict:
        try:
            prompt = PromptTemplate(template=self.template, input_variables=["query"])
            chain = LLMChain(llm=self.llm_service.client, prompt=prompt)
            response = await chain.arun(query=query)
            return json.loads(response.strip())
        except Exception as e:
            return {"action": "llm", "params": {}} 