from logs.logs import get_fabric_logger
from configuration.appConfigProvider import AppConfigProvider
from configuration.envConfig import EnvConfig
import os
from llms.ollamaService import OllamaService
import json
import uuid
from datetime import datetime
from bson import ObjectId
from knowledge.config_util import ConfigUtil
from database.mongoService import MongoService


class OllamaSearch:
    def __init__(self):
        self.appConfigProvider = AppConfigProvider()
        configs = self.appConfigProvider.get_config_by_category("OLLAMA")
        self.host_address = next(c.value for c in configs if c.key == "OLLAMA_URL")
        self.model_name = next(c.value for c in configs if c.key == "OLLAMA_MODEL")
        self.ollamaService = OllamaService(self.model_name, self.host_address)
        config_util = ConfigUtil()
        self.config = config_util.get_knowledge_config()
        config = EnvConfig()
        rivulet_home = config.get_env_variable()
        self.context_path = os.path.join(rivulet_home, "context_db")
        os.makedirs(self.context_path, exist_ok=True)

        es_config = self.appConfigProvider.get_config_by_category("MONGODB")
        self.mongodb_host = [
            config for config in es_config if config.key == "mongodb.hosts"
        ][0].value
        self.mongodb_dbname = [
            config for config in es_config if config.key == "mongodb.dbname"
        ][0].value

        self.mongoclient = MongoService(self.mongodb_host)
        self.logger = get_fabric_logger(__name__, "chat_log.log")

    @staticmethod
    def json_serializer(obj):
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return str(obj)  # fallback for other non-serializable types

    def search_MongoDB(self, entityid, ids, old_guid=None):
        self.logger.info(
            f"Searching MongoDB for entityid: {entityid} and ids: {ids}, Host: {self.mongodb_host}"
        )
        results = self.mongoclient.search_by_id(self.mongodb_dbname, entityid, ids)
        self.logger.info(results)
        if results and not old_guid:
            guid = str(uuid.uuid4())
            file_path = os.path.join(self.context_path, f"{guid}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    results,
                    f,
                    indent=4,
                    ensure_ascii=False,
                    default=self.json_serializer,
                )
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

    def search_Ollama(self, guid, query, max_history: int = 10):
        self.logger.info(f"Searching Ollama for entities: {guid} and query: {query}")
        file_path = os.path.join(self.context_path, f"{guid}.json")

        # chat_config = self.appConfigProvider.get_config_by_category("CHAT_HISTORY")
        # history_type = [
        #     config for config in chat_config if config.key == "HISTORY_TYPE"
        # ][0].value

        with open(file_path, "r") as f:
            entities = json.load(f)
        data = json.dumps(entities)

        # valid_history_types = [t.value for t in ChatHistoryType]
        # if history_type.lower() not in valid_history_types:
        #     raise ValueError(
        #         f"Invalid history type: {history_type}. Expected one of {valid_history_types}"
        #     )
        # history_type = ChatHistoryType(history_type.lower())

        # if session_id is None:
        #     session_id = str(uuid.uuid4())
        # self.logger.info(f"Session ID: {session_id}")
        # chat_history = ChatHistoryFactory.create_chat_history(history_type, session_id)
        # chat_history.add_message("user", query)

        prompt = (
            self.config[2]["ollama_prompt"]
            + f" Query: {query} Context: {data} Response: "
        )
        messages = [
            # {"role": "user", "content": query},
            # {"role": "user", "content": data},
            {"role": "system", "content": prompt},
        ]

        response = self.ollamaService.ollama_client.chat(
            model=self.model_name, messages=messages
        )
        # chat_history.add_message("assistant", response["message"]["content"])
        # chat_history.get_messages()

        # self.logger.info(
        #     f"Adding response to chat_history \n: {response['message']['content']}\n"
        # )
        
        self.logger.info(f"Ollama Response: {response["message"]["content"]}")
        return {"response": response["message"]["content"]}

    # def get_session_chat(self, session_id):
    #     chat_config = self.appConfigProvider.get_config_by_category("CHAT_HISTORY")
    #     history_type = [
    #         config for config in chat_config if config.key == "HISTORY_TYPE"
    #     ][0].value
    #     valid_history_types = [t.value for t in ChatHistoryType]
    #     if history_type.lower() not in valid_history_types:
    #         raise ValueError(
    #             f"Invalid history type: {history_type}. Expected one of {valid_history_types}"
    #         )
    #     # history_type = ChatHistoryType(history_type.lower())
    #     # chat_history = ChatHistoryFactory.create_chat_history(history_type, session_id)
    #     # messages = chat_history.get_messages()
    #     return messages

    def update_ollama_url(self, url: str):
        self.logger.info(f"Updating Ollama URL to: {url}")

        # Get existing config first
        existing_config = self.appConfigProvider.get_config("OLLAMA_URL")
        
        # Update with new values
        existing_config.value = url
        
        updated = self.appConfigProvider.update_config(existing_config)

        if not updated:
            raise Exception("Failed to update Ollama URL")

        # Reinitialize OllamaService with new URL
        self.ollamaService = OllamaService(self.model_name, url)

        return {
            "message": "Ollama URL updated successfully",
            "url": url
        }
        

    def update_model(self, model_name: str):
        self.logger.info(f"Updating Ollama model to: {model_name}")

        # Get existing config first
        existing_config = self.appConfigProvider.get_config("OLLAMA_MODEL")
        
        # Update with new values
        existing_config.value = model_name
        
        updated = self.appConfigProvider.update_config(existing_config)

        if not updated:
            raise Exception("Failed to update Ollama model")

        # Reinitialize OllamaService with new model
        self.ollamaService = OllamaService(model_name, self.host_address)

        return {
            "message": "Ollama model updated successfully",
            "model": model_name
        }
