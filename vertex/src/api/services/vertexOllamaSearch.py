from logs.logs import get_fabric_logger
from configuration.appConfigProvider import AppConfigProvider
import os
from llms.ollamaService import OllamaService
from database.elasticService import ElasticService
import json
import uuid
from enums.chat_enum import ChatHistoryType
from knowledge.config_util import ConfigUtil
from chatHistoryFactory.chat import ChatHistoryFactory
from opensearchpy import OpenSearch


class OllamaSearch:
    def __init__(self):
        self.config = ConfigUtil.get_knowledge_config()
        self.appConfigProvider = AppConfigProvider()
        configs = self.appConfigProvider.get_config_by_category("OLLAMA")
        host_address = [config for config in configs if config.key == "HOST"][0].value
        self.model_name = [config for config in configs if config.key == "MODEL"][0].value
        self.ollamaService = OllamaService(self.model_name, host_address)

        nebula_home = os.getenv("NEBULA_HOME")
        self.context_path = os.path.join(nebula_home, "nebula_db")

        es_config = self.appConfigProvider.get_config_by_category("ELASTIC")
        self.es_host = [config for config in es_config if config.key == "elastic.hosts"][0].value
        self.logger = get_fabric_logger(__name__)

        self.chat_log = get_fabric_logger("Chat_history", "chat_log.log")

    def search_ElasticSearch(self, entityid, ids, old_guid= None):
        self.logger.info(
            f"Searching ElasticSearch for entityid: {entityid} and ids: {ids}"
        )
        qry = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"entityId": entityid}},
                        {"terms": {"entity.ID": ids}},
                    ]
                }
            }
        }

        es = ElasticService([self.es_host])
        results = es.search("nebulastore", qry)
        self.logger.info((results))
        if results and not old_guid:
            guid = str(uuid.uuid4())
            file_path = os.path.join(self.context_path, f"{guid}.json")
            with open(file_path, "w") as f:
                json.dump(results, f)
            return [{"guid": guid}]
        elif old_guid is not None:
            file_path = os.path.join(self.context_path, f"{old_guid}.json")
            with open(file_path, "r") as f:
                existing_data = json.load(f)
            existing_data.extend(results)
            with open(file_path, "w") as f:
                json.dump(existing_data, f)
            return [{"guid": old_guid}]        
        return results


    def search_Ollama(self, guid, query, session_id : str = None, max_history: int = 10):
        self.logger.info(f"Searching Ollama for entities: {guid} and query: {query}")
        file_path = os.path.join(self.context_path, f"{guid}.json")

        chat_config = self.appConfigProvider.get_config_by_category("CHAT_HISTORY")
        history_type = [config for config in chat_config if config.key == "HISTORY_TYPE"][0].value

        with open(file_path, "r") as f:
            entities = json.load(f)
        data = json.dumps(entities)

        valid_history_types = [t.value for t in ChatHistoryType]
        if history_type.lower() not in valid_history_types:
            raise ValueError(f"Invalid history type: {history_type}. Expected one of {valid_history_types}")
        history_type = ChatHistoryType(history_type.lower())

        if session_id is None:
            session_id = str(uuid.uuid4())

        chat_history = ChatHistoryFactory.create_chat_history(history_type, session_id)
        chat_history.add_message("user", query)

        prompt = self.config[2]["ollama_prompt"] + f" Query: {query} Context: {data} Response: "
        messages = [
            # {"role": "user", "content": query},
            # {"role": "user", "content": data},
            {"role": "system", "content": prompt},
        ]
        
        response = self.ollamaService.ollama_client.chat(
            model=self.model_name, messages=messages
        )
        chat_history.add_message("assistant", response["message"]["content"])
        chat_history.get_messages()
        
        self.logger.info(f"Adding response to chat_history \n: {response['message']['content']}\n")
    
        return {
            "session_id": session_id,
            "response": response["message"]["content"]
            }
    
    def get_session_chat(self, session_id):
        chat_config = self.appConfigProvider.get_config_by_category("CHAT_HISTORY")
        history_type = [config for config in chat_config if config.key == "HISTORY_TYPE"][0].value
        valid_history_types = [t.value for t in ChatHistoryType]
        if history_type.lower() not in valid_history_types:
            raise ValueError(f"Invalid history type: {history_type}. Expected one of {valid_history_types}")
        history_type = ChatHistoryType(history_type.lower())
        chat_history = ChatHistoryFactory.create_chat_history(history_type, session_id)
        messages = chat_history.get_messages()
        return messages