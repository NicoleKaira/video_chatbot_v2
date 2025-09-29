import logging
import os
from datetime import datetime
from typing import Dict, Any

import pymongo
from bson import ObjectId
from dotenv import load_dotenv
from langchain_community.vectorstores.azure_cosmos_db import CosmosDBSimilarityType, CosmosDBVectorSearchType
from langchain_core.documents import Document
from sqlalchemy.testing.suite.test_reflection import metadata

from EmbeddingService import EmbeddingService
from databaseservice.databaseService import DatabaseService, database_service
from loggingConfig import logger
from utils import convert_seconds_to_mm_ss
from langchain_community.vectorstores import AzureCosmosDBVectorSearch
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv()

class ChatDatabaseService:
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
            video_collection_name: str = "video",
            prompt_content_index: str = "prompt_content_index",
            prompt_collection_clean_name: str = "prompt_content_clean"
    ):
        db = database_service.get_db()
        self.video_collection = db[video_collection_name]
        self.embedding_function = EmbeddingService()
        self.prompt_content_index_collection = db[prompt_content_index]
        self.prompt_content_index_collection.create_index("metadata.video_id")
        self.prompt_content_index_collection.create_index([("textContent", "text")], name="prompt_text_index")
        self.prompt_content_clean_index_collection = db[prompt_collection_clean_name]
        self.prompt_content_clean_index_collection.create_index("metadata.video_id")
        self.prompt_content_clean_index_collection.create_index([("textContent", "text")], name="prompt_text_index")

        self.azure_openai_embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.environ.get("OPENAI_API_VERSION"),
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            model=os.environ.get("EMBEDDING_MODEL")
        )

        self.vector_store_prompt_index: AzureCosmosDBVectorSearch = AzureCosmosDBVectorSearch.from_connection_string(
            connection_string=database_service.get_mongo_connection_string(),
            namespace=f"{database_service.get_database_name()}.{prompt_content_index}",
            embedding=self.azure_openai_embeddings,
        )

        self.vector_store_prompt_clean_index: AzureCosmosDBVectorSearch = AzureCosmosDBVectorSearch.from_connection_string(
            connection_string=database_service.get_mongo_connection_string(),
            namespace=f"{database_service.get_database_name()}.{prompt_collection_clean_name}",
            embedding=self.azure_openai_embeddings,
        )

        num_lists = 100
        dimensions = 1536
        similarity_algorithm = CosmosDBSimilarityType.COS
        kind = CosmosDBVectorSearchType.VECTOR_IVF
        m = 16
        ef_construction = 64

        self.vector_store_prompt_index.create_index(
            num_lists, dimensions, similarity_algorithm, kind, m, ef_construction
        )
        self.vector_store_prompt_clean_index.create_index(
            num_lists, dimensions, similarity_algorithm, kind, m, ef_construction
        )

    def retrieve_results_prompt_semantic(self, video_id: str, user_prompt: str):
        video_reference_id = self.video_collection.find_one({"video_id": video_id})
        if not video_reference_id:
            raise Exception("Invalid Video ID when retrieving prompt.")
        else:
            pipeline = [{
                "$vectorSearch": {
                    "index": self.vector_store_prompt_index.get_index_name(),
                    "filter": {
                        "metadata.video_id": {
                            "$eq": video_reference_id.get('video_id')
                        }
                    },
                    "limit": 20,
                    "numCandidates": 10,
                    "path": "vectorContent",
                    "queryVector": self.embedding_function.embed_query(user_prompt)
                }},
                {
                    "$project":
                        {
                            "_id": 1,
                            "textContent": 1,
                            "metadata": 1,
                            "score": {"$meta": "vectorSearchScore"}
                        }
                }]
            docs = self.prompt_content_index_collection.aggregate(pipeline)
            return list(docs)

    def retrieve_results_prompt_text(self, video_id, user_query):
        video_reference_id = self.video_collection.find_one({"video_id": video_id})
        if not video_reference_id:
            return ""
        else:
            docs = self.prompt_content_index_collection.find(
                {
                    "$and": [
                        {"metadata.video_id": video_id},
                        {"$text": {"$search": user_query}}
                    ]
                },
                {
                    "textContent": 1,
                    "metadata": 1,
                    "score": {"$meta": "textScore"}
                }
            ).sort("score", -1)
            return list(docs)

    def retrieve_results_prompt_semantic_v2(self, video_id: str, user_prompt: str):
        print(video_id)
        video_reference_id = self.video_collection.find_one({"video_id": video_id})
        if not video_reference_id:
            raise Exception("Invalid Video ID when retrieving prompt.")
        else:
            pipeline = [{
                "$vectorSearch": {
                    "index": self.vector_store_prompt_clean_index.get_index_name(),
                    "filter": {
                        "metadata.video_id": {
                            "$eq": video_reference_id.get('video_id')
                        }
                    },
                    "limit": 20,
                    "numCandidates": 10,
                    "path": "vectorContent",
                    "queryVector": self.embedding_function.embed_query(user_prompt)
                }},
                {
                    "$project":
                        {
                            "_id": 1,
                            "textContent": 1,
                            "metadata": 1,
                            "score": {"$meta": "vectorSearchScore"}
                        }
                }]
            docs = self.prompt_content_clean_index_collection.aggregate(pipeline)
            return list(docs)
        

    # nicole mutlivideo RAG4.0
    def retrieve_results_prompt_semantic_v2_multivid(self, video_ids: list, user_prompt: str):
        print(f"Input video_ids: {video_ids}, type: {type(video_ids)}")
        
        # Input validation: ensure video_ids is a list
        if not isinstance(video_ids, list):
            if isinstance(video_ids, dict):
                # If it's a dict, try to extract values
                if "video_map" in video_ids:
                    video_ids = list(video_ids["video_map"].values())
                    print(f"Extracted video_ids from dict: {video_ids}")
                else:
                    video_ids = list(video_ids.values())
                    print(f"Extracted video_ids from dict values: {video_ids}")
            else:
                # Convert single value to list
                video_ids = [video_ids]
                print(f"Converted single value to list: {video_ids}")
        
        # Ensure we have at least one video ID
        if not video_ids:
            raise ValueError("video_ids cannot be empty")

        # Find all video documents that match any of the video IDs in the list
        video_reference_ids = self.video_collection.find({"video_id": {"$in": video_ids}})
        video_reference_list = list(video_reference_ids)
        
        if not video_reference_list:
            raise Exception("Invalid Video IDs when retrieving prompt.")
        else:
            # Create OR filter for all video IDs
            video_id_filter = {"$or": [{"metadata.video_id": video_ref.get('video_id')} for video_ref in video_reference_list]}
            
            pipeline = [{
                "$vectorSearch": {
                    "index": self.vector_store_prompt_clean_index.get_index_name(),
                    "filter": video_id_filter,
                    "limit": 20, # <- total 20 chuncks retrieved.
                    "numCandidates": 10, # <- Examines 10 candidate documents per video (for efficiency)
                    "path": "vectorContent", 
                    "queryVector": self.embedding_function.embed_query(user_prompt)
                }},
                {
                    "$project":
                        {
                            "_id": 1,
                            "textContent": 1,
                            "metadata": 1,
                            "score": {"$meta": "vectorSearchScore"}
                        }
                }]
            docs = self.prompt_content_clean_index_collection.aggregate(pipeline)
            return list(docs)

    def retrieve_results_prompt_text_v2(self, video_id, user_query):
        video_reference_id = self.video_collection.find_one({"video_id": video_id})
        if not video_reference_id:
            return ""
        else:
            docs = self.prompt_content_clean_index_collection.find(
                {
                    "$and": [
                        {"metadata.video_id": video_id},
                        {"$text": {"$search": user_query}}
                    ]
                },
                {
                    "textContent": 1,
                    "metadata": 1,
                    "score": {"$meta": "textScore"}
                }
            ).sort("score", -1)
            return list(docs)
        
    #nicole mulitdocs RAG 4.0
    def retrieve_results_prompt_text_v2_multivid(self, video_ids, user_query):
        print(f"Input video_ids (text): {video_ids}, type: {type(video_ids)}")
        
        # Input validation: ensure video_ids is a list
        if not isinstance(video_ids, list):
            if isinstance(video_ids, dict):
                # If it's a dict, try to extract values
                if "video_map" in video_ids:
                    video_ids = list(video_ids["video_map"].values())
                    print(f"Extracted video_ids from dict (text): {video_ids}")
                else:
                    video_ids = list(video_ids.values())
                    print(f"Extracted video_ids from dict values (text): {video_ids}")
            else:
                # Convert single value to list
                video_ids = [video_ids]
                print(f"Converted single value to list (text): {video_ids}")
        
        # Ensure we have at least one video ID
        if not video_ids:
            raise ValueError("video_ids cannot be empty")
            
        # Find all video documents that match any of the video IDs in the list
        video_reference_ids = self.video_collection.find({"video_id": {"$in": video_ids}})
        video_reference_list = list(video_reference_ids)
        
        if not video_reference_list:
            return ""
        else:
            # Create OR filter for all video IDs
            video_id_filter = {"$or": [{"metadata.video_id": video_ref.get('video_id')} for video_ref in video_reference_list]}
            
            docs = self.prompt_content_clean_index_collection.find(
                {
                    "$and": [
                        video_id_filter,
                        {"$text": {"$search": user_query}}
                    ]
                },
                {
                    "textContent": 1,
                    "metadata": 1,
                    "score": {"$meta": "textScore"}
                }
            ).sort("score", -1)
            return list(docs)

    def retrieve_results_prompt_semantic_only(self, video_id: str, query: str, top_n: int=5):
        print ("hei", video_id)
        docs_semantic = self.retrieve_results_prompt_semantic_v2(video_id, query)[:top_n]


        # Enforce that retrieved docs are the same form for each list in retriever_docs
        retrieval_results = [Document(page_content=doc['textContent']) for doc in docs_semantic]
        print(retrieval_results)
        return retrieval_results, [doc['textContent'] for doc in docs_semantic]