from database.mongoService import MongoService
from configuration.appConfigProvider import AppConfigProvider


class SearchService:
    def __init__(self):
        self.app_config_provider = AppConfigProvider()
        self.mongo_service = MongoService(
            self.app_config_provider.get_config('mongodb.hosts').value)

    def get_questions(self):
        questions_docs = self.mongo_service.client["nebula"]["questions"].find({})
        questions = [doc.get("question") for doc in questions_docs if doc.get("question")]
        return questions