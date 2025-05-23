import os

class EnvConfig:

    def __init__(self):
        pass

    def get_env_variable(self):
        value = os.environ.get("NEBULA_RIVULET_HOME")
        if not value:
            raise EnvironmentError("Environment variable is not defined")
        return value

