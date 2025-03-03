from abc import ABC
import os
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from typing import List
from langchain_core.documents import Document


class ChromaService(ABC):
    def __init__(self, model_name: str, collection_name: str, db_path: str):
        self.sentence_Transformer = SentenceTransformerEmbeddings(model_name=model_name)
        self.db_path = db_path
        self.collection_name = collection_name
        self.chroma_db = None

    def initialize_chroma(self):
        """Initialize Chroma only when needed."""
        if self.chroma_db is None:
            if os.path.exists(self.db_path):
                print(f"Loading existing vectorstore from {self.db_path}")
                self.chroma_db = Chroma(
                    collection_name=self.collection_name,
                    persist_directory=self.db_path,
                    embedding_function=self.sentence_Transformer,
                    client=chromadb.PersistentClient(
                        path=self.db_path,
                        settings=Settings(anonymized_telemetry=False)
                    )
                )
            else:
                print("Database does not exist. Creating a new vectorstore...")
                os.makedirs(self.db_path, exist_ok=True)  # Ensure directory exists
                self.chroma_db = Chroma(
                    collection_name=self.collection_name,
                    persist_directory=self.db_path,
                    embedding_function=self.sentence_Transformer,
                    client=chromadb.PersistentClient(
                        path=self.db_path,
                        settings=Settings(anonymized_telemetry=False)
                    )
                )

    def add_documents(self, documents: List[Document], entityid=None) -> None:
        self.initialize_chroma()  # Ensure Chroma is initialized

        if entityid:
            ids = [str(id) for id in entityid]
        else:
            ids = None

        self.chroma_db.add_documents(documents=documents, ids=ids)
        print(f"Documents added successfully to {self.db_path}")

    def similarity_search(self, query: str, k: int = 10) -> List[Document]:
        self.initialize_chroma()  # Ensure Chroma is initialized
        return self.chroma_db.similarity_search(query=query, k=k)

    def delete_collection(self, ids):
        self.initialize_chroma()  # Ensure Chroma is initialized
        return self.chroma_db.delete(ids=ids)
