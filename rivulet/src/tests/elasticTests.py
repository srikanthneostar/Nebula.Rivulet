from services.searchService import SearchService
from  logs.logs import get_fabric_logger

logger = get_fabric_logger(__name__,"C:/Temp/test.log")

def get_knowledge_config() -> dict:
    import json

    config_path = "C:/nebula.rivulet/rivulet/src/knowledge/knowledge_config.json"

    with open(config_path, 'r') as f:
        return json.load(f)


def test_search_service() -> None:
    search_service = SearchService()
    knowledge_config = get_knowledge_config()
    # print(knowledge_config)
    # query = {
    #    "query": {
    #        "match_all": {}
    #    }
    # }
    query = {"query": knowledge_config[0]['query']}
    questions = knowledge_config[0]['questions']
    print(questions)
    results = search_service.elastic_service.search("nebulastore", query, 1)
    assert len(results) > 0
    for result in results:
        logger.info(result)


if __name__ == "__main__":
    test_search_service()
