from embedings.faissService import FaissService
from configuration.appConfigProvider import AppConfigProvider
from configuration.envConfig import EnvConfig
from logs.logs import get_fabric_logger
import os


class FaissSearch:
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("CHROMADB")
        model = [config for config in configs if config.key == "CHROMA_MODEL"][0].value
        config = EnvConfig()
        rivulet_home = config.get_env_variable()
        db_path = os.path.join(rivulet_home, "rivulet_db")
        self.faissService = FaissService(model, collection_name="journalevents", db_path=db_path)
        self.logger = get_fabric_logger(__name__)

    def search_results(self,query: str, k: int = 2):
        results = self.faissService.similarity_search(query, k)
        return results