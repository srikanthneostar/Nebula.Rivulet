import json
import os
from pathlib import Path
from langchain.schema import Document
# from embedings.faissService import FaissService
from embedings.chromaService import  ChromaService
from langchain_text_splitters import RecursiveCharacterTextSplitter
from framework.pipeline_stage import PipelineStage
from configuration.appConfigProvider import AppConfigProvider
from logs.logs import get_fabric_logger

class JournalEventEmbedding(PipelineStage):
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("CHROMADB")
        model = [config for config in configs if config.key == "CHROMA_MODEL"][0].value
        nebula_home = os.getenv("NEBULA_HOME")
        self.db_path = os.path.join(nebula_home, "nebula_db")
        # self.faissService = FaissService(model, collection_name="journalevents", db_path=self.db_path)
        self.chromaService = ChromaService(model, collection_name="journalevents", db_path=self.db_path)
        self.logger = get_fabric_logger(__name__)
        
    def process(self, data: any) -> any:
        documents = []
        for event in data:
            doc = Document(
                page_content=json.dumps(event)
            )
            documents.append(doc)

        self.logger.info(f"Embedding documents \n: {documents}")
        self.chromaService.add_documents(
            documents=documents
        )
        self.logger.info(f"Embedded and stored {len(documents)} documents to {self.db_path}")
        return data