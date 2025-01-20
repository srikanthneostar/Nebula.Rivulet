from typing import List, Dict, Any
# import chromadb
# from chromadb.config import Settings
from ollama import Client

class OllamaService:
    def __init__(self, model_name : str, host_address: str):
        self.model_name = model_name
        self.ollama_client = Client(host=host_address)
    #     self.chroma_client = chromadb.Client(
    #         Settings(
    #             persist_directory="nebula", 
    #             chroma_db_impl="duckdb+parquet"
    #         )
    #     )
    
    # def query_chroma(self, query: str, collection_name: str, top_k: int = 5) -> List[str]:
    #     collection = self.chroma_client.get_collection(collection_name)
    #     results = collection.query(query_texts=[query], n_results=top_k)
    #     return results['documents'][0]

    def query_model(self, query: str, data : str):
        payload = {
            "model": self.model_name,
            "query": query,
            "data": data
        }
        response = self.ollama_client.chat(payload)
        return response