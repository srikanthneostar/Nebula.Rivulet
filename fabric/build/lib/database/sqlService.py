from types import EllipsisType
import pyodbc
import pandas as pd
from sqlalchemy import create_engine
from database.interface import SqlConnectorInterface
from configuration.appConfigProvider import AppConfigProvider


class SqlConnector(SqlConnectorInterface):
    def __init__(self):
        dataProvider = AppConfigProvider()
        sql_category = dataProvider.get_config_by_category("DataSource")
        self.username = self.get_config_values(
            sql_category=sql_category, keyname="USERNAME"
        )
        self.password = self.get_config_values(
            sql_category=sql_category, keyname="PASSWORD"
        )
        self.url = self.get_config_values(
            sql_category=sql_category, keyname="DATABASEURI"
        )

    def get_config_values(self, sql_category, keyname):
        filtered_list = list(filter(lambda x: x.key == keyname, sql_category))
        if filtered_list:
            return filtered_list[0].value
        else:
            return ""

    def get_dbhost(self):
        url = self.url

        def host_address(s):
            return s.split("//")[1].split(";")[0]

        def database_name(s):
            return s.split("=")[1].split(";")[0]

        host = host_address(url)
        database = database_name(url)
        return database, host

    def execute_Sql(self, sqlQuery, parameters: EllipsisType = None):
        database, host = self.get_dbhost()
        df: pd.DataFrame = None
        try:
            # Example: mssql+pyodbc://username:password@host/database?driver=SQL+Server
            connection_string = f"mssql+pyodbc://{self.username}:{self.password}@{host}/{database}?driver=SQL+Server"
            engine = create_engine(connection_string)

            if parameters:
                df = pd.read_sql(sqlQuery, engine, params=parameters)
            else:
                df = pd.read_sql(sqlQuery, engine)

            engine.dispose()
            return df
        except Exception as e:
            raise e
