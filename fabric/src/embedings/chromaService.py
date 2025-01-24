from abc import ABC

import chromadb
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from typing import List
from langchain_core.documents import Document


class ChromaService(ABC):
    def __init__(self, model_name: str, collection_name: str, db_name: str = "nebula"):
        self.sentence_Transformer = SentenceTransformerEmbeddings(model_name=model_name)

        self.chroma_Db = chromadb.PersistentClient(path="./nebula_db")
        self.collection = self.chroma_Db.get_or_create_collection(
            name=collection_name
        )
        self.langchain_chroma_db = Chroma(
            client=self.chroma_Db,
            collection_name=collection_name,
            embedding_function=self.sentence_Transformer,
        )

    def add_documents(self, documents: List[Document], ids=None, persist_path: str = None) -> Chroma:
        return self.langchain_chroma_db.from_documents(
            documents=documents,
            embedding=self.sentence_Transformer,
            ids=ids,
            persist_directory=persist_path,
        )

