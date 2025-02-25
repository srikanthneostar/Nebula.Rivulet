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

        # Ensure ChromaDB is initialized with persistence
        self.chroma_db = Chroma(
            collection_name=self.collection_name,
            persist_directory=self.db_path,  # Ensure persistence is enabled  
            embedding_function=self.sentence_Transformer,
            client=chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False
                ))
        )

    def add_documents(self, documents: List[Document], entityid = None) -> None:
        if os.path.exists(self.db_path):
            print(f"Appending to existing vectorstore at {self.db_path}")
            # self.chroma_db.get()
            # self.chroma_db.__ensure_collection(name=self.collection_name)
            self.chroma_db.add_documents(documents=documents, ids=[str(id) for id in entityid] if entityid else None)
        else:
            print("Creating new vectorstore")
            print(f"Creating embeddings. May take some minutes...")
            collection = self.chroma_db.__ensure_collection(name=self.collection_name)
            self.chroma_db = Chroma.from_documents(
                documents=documents,
                embedding_function=self.sentence_Transformer,
                ids=entityid,
                persist_directory=self.db_path,
                collection_name=collection,
                client=chromadb.PersistentClient(
                    path=self.db_path,
                    settings=Settings(
                        anonymized_telemetry=False
                    ))
                )
        # self.chroma_db.persist()

    def similarity_search(self, query: str, k: int = 10) -> List[Document]:
        return self.chroma_db.similarity_search(query=query, k=k,)

    def delete_collection(self, ids):
        return self.chroma_db.delete(ids=ids)