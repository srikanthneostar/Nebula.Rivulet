import json
import os
from langchain_core.documents import Document

# from embedings.faissService import FaissService
from embedings.chromaService import ChromaService
from framework.pipeline_stage import PipelineStage
from configuration.appConfigProvider import AppConfigProvider
from configuration.envConfig import EnvConfig
from logs.logs import get_fabric_logger


class JournalEventEmbedding(PipelineStage):
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("CHROMADB")
        model = [config for config in configs if config.key == "CHROMA_MODEL"][0].value
        config = EnvConfig()
        rivulet_home = config.get_env_variable()
        db_path = str(os.path.join(rivulet_home, "rivulet_db"))
        # self.faissService = FaissService(model, collection_name="journalevents", db_path=self.db_path)
        self.chromaService = ChromaService(
            model, collection_name="journalevents", db_path=db_path
        )
        self.logger = get_fabric_logger(__name__)

    def process(self, data: any) -> any:
        documents = []
        for event in data:
            self.logger.info(f"Embedding event \n: {event}")
            doc = Document(page_content=json.dumps(event, default=str))
            documents.append(doc)
        entityid = [str(event.get("_id")) for event in data]

        self.logger.info(f"Embedding documents \n: {documents}")
        self.chromaService.add_documents(documents=documents, entityid=entityid)
        self.logger.info(f"Embedded and stored {len(documents)} documents")
        return data
