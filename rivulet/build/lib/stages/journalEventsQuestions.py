from framework.pipeline_stage import PipelineStage
from configuration.appConfigProvider import AppConfigProvider
from llms.ollamaService import OllamaService
from logs.logs import get_fabric_logger
from knowledge.config_util import ConfigUtil
from database.mongoService import MongoService


class JournalEventQuestions(PipelineStage):
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        host_address = appConfigProvider.get_config('HOST').value
        model_name = appConfigProvider.get_config('MODEL').value
        self.ollamaService = OllamaService(model_name, host_address)
        self.mongoService = MongoService(appConfigProvider.get_config('mongodb.hosts').value)
        self.db = self.mongoService.client["nebula"]
        self.ques = self.db["questions"]
        self.logger = get_fabric_logger(__name__)
        self.configuration = ConfigUtil.get_knowledge_config(self)

    def process(self, data: any) -> any:
        questions = []
        for event in data:
            prompt = f"You are an intelligent assistant trained to generate meaningful and context-aware 3 random short question based on provided context. Context{str(event)} Questions:"
            question = self.ollamaService.ollama_client.generate(
                model=self.ollamaService.model_name, prompt=prompt
            )
            sample = question.response
            questions.append({**event, "similarQuestion": question.response})

            question_lines = [
                line.strip() for line in sample.split("\n") if line.strip()
            ]
            filtered_questions = [q for q in question_lines if "?" in q]

            cleaned_questions = [
                (
                    q.split(":", 1)[-1].strip().lstrip("0123456789. ")
                    if "Question" in q
                    else q.strip().lstrip("0123456789. ")
                )
                for q in filtered_questions[:3]
            ]
            questions[-1]["similarQuestion"] = cleaned_questions
            for ques in cleaned_questions:
                print(f"{ques}")

            docs = [{"question": q} for q in cleaned_questions]

            if docs:
                self.ques.insert_many(docs)

        self.logger.info("Questions \n:", str(questions))
        return questions
