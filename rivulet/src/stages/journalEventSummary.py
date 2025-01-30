from framework.pipeline_stage import PipelineStage
from configuration.appConfigProvider import AppConfigProvider
from llms.ollamaService import OllamaService
from logs.logs import get_fabric_logger
class JournalEventSummary(PipelineStage):
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("OLLAMA")
        host_address = [config for config in configs if config.key == "HOST"][0].value
        model_name = [config for config in configs if config.key == "MODEL"][0].value
        self.ollamaService = OllamaService(model_name,host_address)
        self.logger = get_fabric_logger(__name__)

    def process(self, data: any) -> any:
        self.logger.info("Journal Event Summary: %s", data)
        summaries = []
        for events in data['data']:
            prompt = "You are an intelligent assistant trained to generate meaningful and context-aware Summary. First, summarize the following content concisely: " + str(events)
            summary = self.ollamaService.ollama_client.generate(model=self.ollamaService.model_name, prompt=prompt)
            summaries.append({**events, "summary": summary})
        self.logger.info("Journal Event Summary: %s", summaries)
        return summaries