import os

import pymongo
from dotenv import load_dotenv
from langchain_core.documents import Document

from EmbeddingService import EmbeddingService
from langchain_community.vectorstores import AzureCosmosDBVectorSearch
from langchain_openai import AzureOpenAIEmbeddings

from databaseservice.databaseService import DatabaseService, database_service

load_dotenv()


class UserRepositoryService:
    """
    AzureDatabaseService is a service that interacts with Azure CosmosDB Vector store.

    Args:
        mongo_connection_string (str): MongoDB Connection String. Example: mongodb+srv://<username>:<password>@<resource>.mongocluster.cosmos.azure.com/<...>. Required.
        database_name (str): MongoDB Database Name. Required.
        chunk_collection_name (str): Collection Name to store chunks. Default: "chunk".
        embedding_collection_name (str): Collection Name to store embeddings and other metadata. Default: "transcript".
        video_collection_name (str): Collection Name to store video information. Default: "video".
        embedding_model (str): Embedding Model. Default: "all-MiniLM-L6-v2".
    """

    def __init__(
            self,
            user_collection_name: str = "user",
    ):
        db = database_service.get_db()
        self.user_collection_name = db[user_collection_name]

    def get_user(self, username: str):
        return self.user_collection_name.find_one({"username": username})