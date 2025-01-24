import json
from typing import List, Dict, Any
from ollama import Client

class OllamaService:
    def __init__(self, model_name: str, host_address: str):
        self.model_name = model_name
        self.ollama_client = Client(host=host_address)

    def query_model(self, prompt: str, query: str, data: Any, system_context : Any = None) -> Dict[str, Any]:
        if not isinstance(data, str):
            try:
                data = json.dumps(data)
            except (TypeError, ValueError):
                raise ValueError("Data provided is not serializable to a string")
        if system_context is not None:
            payload = system_context
        else:
            payload = [
                    {"role": "system", "content": prompt},
                    {"role": "system", "content": data},
                    {"role": "user", "content": query}
                ]
        response = self.ollama_client.chat(model=self.model_name, messages=payload)
        return response