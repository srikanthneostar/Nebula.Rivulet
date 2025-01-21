from embedings.chromaService import ChromaService
from framework.pipeline_stage import PipelineStage
from configuration.appConfigProvider import AppConfigProvider

class JournalEventEmbedding(PipelineStage):
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("CHROMADB")
        model = [config for config in configs if config.key == "CHROMA_MODEL"][0].value
        self.chromaService = ChromaService(model, "journalevents")
        
    def process(self, data: any) -> any:
        for events in data:
            self.chromaService.add_documents(events)
        return data
