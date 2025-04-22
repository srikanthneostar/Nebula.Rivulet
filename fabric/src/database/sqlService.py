from types import EllipsisType
import pyodbc
import pandas as pd

from database.interface import SqlConnectorInterface
from configuration.appConfigProvider import AppConfigProvider


class SqlConnector(SqlConnectorInterface):
    def __init__(self):
        dataProvider = AppConfigProvider()
        sql_category = dataProvider.get_config_by_category("DataSource")
        self.username = self.get_config_values(
            sql_category=sql_category, keyname='USERNAME')
        self.password = self.get_config_values(
            sql_category=sql_category, keyname='PASSWORD')
        self.url = self.get_config_values(
            sql_category=sql_category, keyname='DATABASEURI')

    def get_config_values(self, sql_category, keyname):
        filtered_list = list(filter(lambda x: x.key == keyname, sql_category))
        if filtered_list:
            return filtered_list[0].value
        else:
            return ''

    def get_dbhost(self):
        url = self.url
        def host_address(s): return s.split("//")[1].split(";")[0]
        def database_name(s): return s.split("=")[1].split(";")[0]
        host = host_address(url)
        database = database_name(url)
        return database, host

    def execute_Sql(self, sqlQuery, parameters: EllipsisType = None):
        database, host = self.get_dbhost()
        df: pd.DataFrame = None
        try:
            connect = pyodbc.connect(Driver='SQL Server', host=host,
                                     database=database, user=self.username,
                                     password=self.password)
            if (parameters != None):
                df = pd.read_sql(sqlQuery, connect, params=parameters)
            else:
                df = pd.read_sql(sqlQuery, connect)
            connect.close()
            return df
        except pyodbc.Error as e:
            raise e
