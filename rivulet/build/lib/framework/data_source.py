
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generic, TypeVar
T = TypeVar('T')  # Type variable for the client
D = TypeVar('D')  # Type variable for the data

class DataSource(Generic[T, D]):
    """
    Generic base class for data sources.
    T: Type of the client
    D: Type of the data returned
    """
    def __init__(self, client: T):
        self.client = client

    @abstractmethod
    def get_data(self, query: any) -> List[Dict]:
        """Fetch data using the provided query"""
        pass