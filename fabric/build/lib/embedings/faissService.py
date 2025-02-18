import os
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List
from langchain_core.documents import Document
from logs.logs import get_fabric_logger
import shutil
import os

class FaissService:
    def __init__(self, model_name: str, collection_name: str, db_path: str = "./nebula_db"):
        self.sentence_Transformer = SentenceTransformerEmbeddings(model_name=model_name)
        self.db_path = db_path
        self.collection_name = collection_name
        self.logger = get_fabric_logger(__name__)

    def add_documents(self, documents: List[Document], ids=None, persist_path: str = None) -> FAISS:
        try:
            if os.path.exists(self.db_path):
                shutil.rmtree(self.db_path)
            self.logger.info("Loading FAISS database")
            db = FAISS.load_local(
                folder_path=self.db_path,
                embeddings=self.sentence_Transformer,
                index_name=self.collection_name,
                allow_dangerous_deserialization=True
            )

        except:
            self.logger.info(f"Error loading FAISS database")
            self.logger.info("Creating new FAISS database")
            texts = [doc.page_content for doc in documents]
            faiss_db = FAISS.from_texts(
                texts=texts,
                embedding=self.sentence_Transformer,
            )
            return faiss_db.save_local(persist_path,index_name=self.collection_name)

    def similarity_search(self, query: str, k: int = 2) -> List[Document]:
        try:
            db = FAISS.load_local(
                folder_path=self.db_path,
                embeddings=self.sentence_Transformer,
                index_name=self.collection_name,
                allow_dangerous_deserialization=True
            )
            return db.similarity_search(
                query=query,
                k=k
            )
        except Exception as e:
            self.logger.error(f"Error during similarity search: {str(e)}")
            return []