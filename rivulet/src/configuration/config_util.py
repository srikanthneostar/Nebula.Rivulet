class ConfigUtil:
    def __init__(self):
        pass

    def get_knowledge_config() -> dict:
        import json

        config_path = "../configuration/knowledge_config.json"

        with open(config_path, 'r') as f:
            return json.load(f)
