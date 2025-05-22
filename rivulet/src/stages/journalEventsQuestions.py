import json
import os
from framework.pipeline_stage import PipelineStage
from configuration.appConfigProvider import AppConfigProvider
from llms.ollamaService import OllamaService
from logs.logs import get_fabric_logger
from  knowledge.config_util import ConfigUtil

class JournalEventQuestions(PipelineStage):
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("OLLAMA")
        host_address = [config for config in configs if config.key == "HOST"][0].value
        model_name = [config for config in configs if config.key == "MODEL"][0].value
        self.ollamaService = OllamaService(model_name,host_address)
        self.logger = get_fabric_logger(__name__)
        self.configuration = ConfigUtil.get_knowledge_config()
        
    def process(self, data: any) -> any:
        questions = []
        for event in data:
            prompt = f"You are an intelligent assistant trained to generate meaningful and context-aware 3 random short question based on provided context. Context{str(event)} Questions:"
            question = self.ollamaService.ollama_client.generate(model=self.ollamaService.model_name,prompt=prompt)
            sample =  question.response
            questions.append({**event, "similarQuestion": question.response})

            question_lines = [line.strip() for line in sample.split('\n') if line.strip()]
            filtered_questions = [q for q in question_lines if '?' in q]
            
            cleaned_questions = [q.split(":", 1)[-1].strip().lstrip("0123456789. ") if "Question" in q else q.strip().lstrip("0123456789. ") for q in filtered_questions[:3]]
            questions[-1]["similarQuestion"] = cleaned_questions
            for ques in cleaned_questions:
                print(f"{ques}")
            
            root_path = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
            
            root_path = root_path.replace("\\rivulet", "\\configurations\\knowledge_db")
            config_path = os.path.join(root_path, "knowledge_config.json")
            
            with open(config_path, 'r') as f:
                config = json.load(f)

            if "questions" not in config[1]:
                config[1]["questions"] = []
            config[1]["questions"].extend(cleaned_questions)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)

        self.logger.info("Questions \n: %s", str(questions))
        return questions