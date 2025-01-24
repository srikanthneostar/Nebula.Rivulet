from langchain.schema import Document
from embedings.chromaService import ChromaService
from framework.pipeline_stage import PipelineStage
from configuration.appConfigProvider import AppConfigProvider
from logs.logs import get_fabric_logger

class JournalEventEmbedding(PipelineStage):
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("CHROMADB")
        model = [config for config in configs if config.key == "CHROMA_MODEL"][0].value
        self.chromaService = ChromaService(model, "journalevents")
        self.logger = get_fabric_logger(__name__)
        
    def process(self, data: any) -> any:
        for events in data:
            documents = [
                Document(page_content=str(event), metadata={}) for event in events
            ]
            self.chromaService.add_documents(documents)
        self.logger.info("Embedding done", data)
        return data
