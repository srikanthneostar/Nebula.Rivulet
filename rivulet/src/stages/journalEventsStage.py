from framework.pipeline_stage import PipelineStage
from configuration.appConfigProvider import AppConfigProvider
from llms.ollamaService import OllamaService

class JournalEventsQAstage(PipelineStage):
    def __init__(self,config:any):
        self.Configuraiton = config
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("OLLAMA")
        host_address = [config for config in configs if config.key == "HOST"][0].value
        model_name = [config for config in configs if config.key == "MODEL"][0].value
        self.ollamaService = OllamaService(model_name,host_address)

    def process(self, data: any) -> any:
        questions = self.Configuraiton["questions"]
        prompt = self.Configuraiton["prompt"]
        responses = []
        for question in questions:
            response = self.ollamaService.query_model(prompt=prompt,query=question, data=data)
            responses.append({"question": question, "response": response})
            
        return {
            "data" : data,
            "response" : responses
        }