from framework.pipeline_stage import PipelineStage
from configuration.appConfigProvider import AppConfigProvider
from llms.ollamaService import OllamaService
from logs.logs import get_fabric_logger

class JournalEventQuestions(PipelineStage):
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("OLLAMA")
        host_address = [config for config in configs if config.key == "HOST"][0].value
        model_name = [config for config in configs if config.key == "MODEL"][0].value
        self.ollamaService = OllamaService(model_name,host_address)
        self.logger = get_fabric_logger(__name__)

    def process(self, data: any) -> any:
        questions = []
        for event in data:
            prompt = "Please generate 3 random questions for the following event: {}".format(str(event))
            question = self.ollamaService.ollama_client.generate(model=self.ollamaService.model_name,prompt=prompt)
            sample =  question.response
            questions.append({**event, "similarQuestion": question.response})
        self.logger.info("Questions \n: %s", str(questions))
        return questions