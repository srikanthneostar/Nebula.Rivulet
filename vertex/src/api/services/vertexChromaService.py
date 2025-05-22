from embedings.chromaService import ChromaService
from logs.logs import get_fabric_logger
from configuration.appConfigProvider import AppConfigProvider
import os
from llms.ollamaService import OllamaService

class ChromaSearch:
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("CHROMADB")
        model = [config for config in configs if config.key == "CHROMA_MODEL"][0].value
        rivulet_home = os.getenv("RIVULET_HOME")
        db_path = os.path.join(rivulet_home, "rivulet_db")
        self.chromaService = ChromaService(model, collection_name="journalevents",db_path=db_path)
        self.logger = get_fabric_logger(__name__)
        
    def get_OllamaService(self):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("OLLAMA")
        host_address = [config for config in configs if config.key == "HOST"][0].value
        model_name = [config for config in configs if config.key == "MODEL"][0].value
        ollamaService = OllamaService(model_name,host_address)
        return (ollamaService,model_name)
    
    def search_results(self, query: str, k: int = 10, llmsearch : bool = False):
        results = self.chromaService.similarity_search(query, k)
        self.logger.info(results)
        if llmsearch == True:
            service = self.get_OllamaService()
            model_name = str(service[1])
            context = "\n".join([str(result) for result in results])
            prompt = f"Based on the following context:\n{context}\n\nQuestion: {query}\nAnswer:"
            response = service[0].ollama_client.generate(model=model_name, prompt=prompt)
            results.append({"query_response": response.response})
        return results

    def delete_collection(self, ids):
        for id in ids:
            self.logger.info(f"Deleting {id}")
            self.chromaService.delete_collection(ids=str(id))