from framework.pipeline_stage import PipelineStage
from configuration.appConfigProvider import AppConfigProvider
from llms.ollamaService import OllamaService


class JournalEventQuestions(PipelineStage):
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("OLLAMA")
        host_address = [config for config in configs if config.key == "HOST"][0].value
        model_name = [config for config in configs if config.key == "MODEL"][0].value
        self.ollamaService = OllamaService(model_name,host_address)

    def process(self, data: any) -> any:
        questions = []
        for event in data:
            prompt = f"Please generate 3 random questions for the following event: {event}"
            question = self.ollamaService.ollama_client.generate(prompt)
            questions.append({**event, "similarQuestion": question})
        return questions