from logs.logs import get_fabric_logger
from configuration.appConfigProvider import AppConfigProvider
import os
from llms.ollamaService import OllamaService
from database.elasticService import ElasticService
import json
import uuid
from knowledge.config_util import ConfigUtil
# from rivulet.src.knowledge.config_util import ConfigUtil

class OllamaSearch:
    def __init__(self):
        self.config = ConfigUtil.get_knowledge_config()
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("OLLAMA")
        host_address = [config for config in configs if config.key == "HOST"][0].value
        self.model_name = [config for config in configs if config.key == "MODEL"][0].value
        self.ollamaService = OllamaService(self.model_name, host_address)

        nebula_home = os.getenv("NEBULA_HOME")
        self.context_path = os.path.join(nebula_home, "nebula_db")

        es_config = appConfigProvider.get_config_by_category("ELASTIC")
        self.es_host = [config for config in es_config if config.key == "elastic.hosts"][0].value
        self.logger = get_fabric_logger(__name__)
    
    def search_ElasticSearch(self, entityid, ids):
        self.logger.info(f"Searching ElasticSearch for entityid: {entityid} and ids: {ids}")
        qry = {
            "query": {
                "bool": {
                "must": [
                    {
                    "match": {
                        "entityId": entityid
                    }
                    },
                    {
                    "terms": {
                        "entity.ID": ids
                    }
                    }
                ]
                }
            }
        }
    
        es = ElasticService([self.es_host])
        results = es.search("nebulastore",qry)
        self.logger.info((results))
        if results:
            guid = str(uuid.uuid4())
            file_path = os.path.join(self.context_path, f"{guid}.json")
            with open(file_path, 'w') as f:
                json.dump(results, f)
            return [{"guid": guid}]
        return results
    
    def search_Ollama(self, guid, query):
        self.logger.info(f"Searching Ollama for entities: {guid} and query: {query}")
        file_path = os.path.join(self.context_path, f"{guid}.json")
        with open(file_path, 'r') as f:
            entities = json.load(f)
        prompt = self.config[2]['ollama_prompt']
        prompt = f"{prompt} Here is the context: Context:{entities} Question: {query} Answer:"
        self.logger.info(f"Prompt: {prompt}")
        response = self.ollamaService.ollama_client.generate(model=self.model_name,prompt=prompt)
        return {
            "response" : response.response
            }



