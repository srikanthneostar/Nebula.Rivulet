from framework.pipeline_stage import PipelineStage
from configuration.appConfigProvider import AppConfigProvider
from llms.ollamaService import OllamaService
from logs.logs import get_fabric_logger

class JournalEventSummary(PipelineStage):
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        host_address = appConfigProvider.get_config('HOST').value
        model_name = appConfigProvider.get_config('MODEL').value
        self.ollamaService = OllamaService(model_name,host_address)
        self.logger = get_fabric_logger(__name__)

    def process(self, data: any) -> any:
        # self.logger.info("Journal Event data \n: %s", data)
        summaries = []
        for events in data:
            prompt = f"You are an intelligent assistant trained to generate meaningful and context-aware Summary. First, summarize the following content concisely. Content :{str(events)} Summary:"
            summary = self.ollamaService.ollama_client.generate(model=self.ollamaService.model_name, prompt=prompt)
            # sample =  summary.response
            # self.logger.info("Journal Event Summary \n: %s", sample)
            summaries.append({**events, "summary":  summary.response})
        self.logger.info("Journal Event Summary \n:", summaries)
        return summaries