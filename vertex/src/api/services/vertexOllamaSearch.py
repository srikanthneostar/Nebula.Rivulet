from logs.logs import get_fabric_logger
from configuration.appConfigProvider import AppConfigProvider
import os
from llms.ollamaService import OllamaService
from database.elasticService import ElasticService
import json
import uuid
from knowledge.config_util import ConfigUtil
# from rivulet.src.knowledge.config_util import ConfigUtil

chat_history: list[dict] = list()

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
        self.chat_log = get_fabric_logger("Chat_history","chat_log.log")
    
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
        global chat_history

        with open(file_path, 'r') as f:
            entities = json.load(f)
        
        data = json.dumps(entities)

        prompt = self.config[2]['ollama_prompt']
        # prompt = f"{prompt} Here is the context: Context:{data} Question: {query} Answer:"

        messages = [
            {"role": "user", "content": query},
            {"role": "user","content": data},
            {"role": "system", "content": prompt}
        ]

        response = self.ollamaService.ollama_client.chat(model=self.model_name,messages=messages)

        if len(chat_history) == 0:
            chat_history = [{"role": "assistant", "content": response['message']['content']}]
        else:
            chat_history.append({"role": "assistant", "content": response['message']['content']})

        self.logger.info(f"Adding response to chat_history \n: {response['message']['content']}, length: {len(chat_history)}\n")
        self.chat_log.info(f"chat_history \n: {chat_history}")

        return response['message']['content']    
    
    def llm_chat_history(self,message):
        try:
            self.logger.info("chat_history called")
            if len(self.chat_history) == 0:
                self.chat_history = [
                    {"role": "system","content": message},
                    {"role": "system", "content": "You are a helpful assistant. You will be provided with some text. Please summarize the text with less then 20 words."},
                ]
            else:
                self.chat_history.append({"role": "user", "content": message})
                self.logger.info(f"chat_history: {self.chat_history}")

            response = self.ollamaService.ollama_client.chat(self.model_name, messages=self.chat_history)
            self.chat_history.append(response["message"])

            return response["message"]["content"]

        except Exception as e:
            self.logger.error(f"Error in chat_history: {e}")
            raise e



