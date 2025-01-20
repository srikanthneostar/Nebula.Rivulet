from database.elasticService import ElasticService
from configuration.appConfigProvider import AppConfigProvider


class SearchService:
    def __init__(self):
        self.app_config_provider = AppConfigProvider()
        self.elastic_service = ElasticService(
            self.app_config_provider.get_config('elastic.hosts').value)
