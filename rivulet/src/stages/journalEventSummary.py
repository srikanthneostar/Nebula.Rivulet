from framework.pipeline_stage import PipelineStage
from configuration.appConfigProvider import AppConfigProvider
from llms.ollamaService import OllamaService

from ollama import Client

class JournalEventSummary(PipelineStage):
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("OLLAMA")
        host_address = [config for config in configs if config.key == "HOST"][0].value
        model_name = [config for config in configs if config.key == "MODEL"][0].value
        self.ollamaService = OllamaService(model_name,host_address)

    def process(self, data: any) -> any:
        summaries = []
        for event in data:
            prompt = f"Please provide a concise summary of the following event: {event}"
            summary = self.ollamaService.ollama_client.generate(prompt)
            summaries.append(summary)
        return summaries
