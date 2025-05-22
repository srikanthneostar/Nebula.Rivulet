import json
import os

class ConfigUtil:
    def __init__(self):
        pass

    def get_knowledge_config() -> dict:
        rivulet_home = os.getenv("RIVULET_HOME")
        context_path = os.path.join(rivulet_home, "knowledge_db")
        os.makedirs(context_path, exist_ok=True)

        config_path = os.path.join(context_path, "knowledge_config.json")

        # # Create the file if it doesn't exist
        # if not os.path.exists(config_path):
        #     default_config = {
        #         "questions": []
        #     }
        #     with open(config_path, 'w') as f:
        #         json.dump(default_config, f, indent=4)

        # Load and return the config
        with open(config_path, 'r') as f:
            return json.load(f)
