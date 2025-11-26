from framework.pipeline_stage import PipelineStage
from configuration.appConfigProvider import AppConfigProvider
from llms.ollamaService import OllamaService
from logs.logs import get_fabric_logger

class JournalEventsQAstage(PipelineStage):
    def __init__(self,config:any):
        self.Configuraiton = config
        appConfigProvider = AppConfigProvider()
        host_address = appConfigProvider.get_config('HOST').value
        model_name = appConfigProvider.get_config('MODEL').value
        self.ollamaService = OllamaService(model_name,host_address)
        self.logger = get_fabric_logger(__name__)

    def process(self, data: any) -> any:
        questions = self.Configuraiton["questions"]
        prompt = self.Configuraiton["prompt"]
        responses = []
        for question in questions:
            response = self.ollamaService.query_model(prompt=prompt,query=question, data=data)
            responses.append({"question": question, "response": response})
            self.logger.info("Response \n:", response)
        return {
            "data" : data,
            "response" : responses
        }