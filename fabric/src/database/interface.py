from abc import ABC, abstractmethod


class SqlConnectorInterface(ABC):

    @abstractmethod
    def get_config_values(self, sql_category, keyname):
        pass

    @abstractmethod
    def get_dbhost(self):
        pass

    @abstractmethod
    def execute_Sql(self, sql_query, params=...):
        pass