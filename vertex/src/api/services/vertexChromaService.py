from embedings.chromaService import ChromaService
from logs.logs import get_fabric_logger
from configuration.appConfigProvider import AppConfigProvider
import os

class ChromaSearch:
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("CHROMADB")
        model = [config for config in configs if config.key == "CHROMA_MODEL"][0].value
        nebula_home = os.getenv("NEBULA_HOME")
        db_path = os.path.join(nebula_home, "nebula_db")
        self.chromaService = ChromaService(model, collection_name="journalevents",db_path=db_path)
        self.logger = get_fabric_logger(__name__)
        
    def search_results(self,query: str, k: int = 2):
        results = self.chromaService.similaritysearch(query, k)
        return results
