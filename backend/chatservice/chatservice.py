import os
import concurrent.futures
import json
from pydoc import doc 

from dotenv import load_dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain_openai import AzureChatOpenAI


from langchain_core.prompts import PromptTemplate
from openai import AsyncAzureOpenAI

from chatservice.repository import ChatDatabaseService
from chatservice.model import ChatHistory, LLMIsTemporalResponse
from chatservice.utils import weighted_reciprocal_rank
from loggingConfig import logger
from utils import process_file, get_prompt_template, get_prompt_template_naive, prompt_template_test, get_prompt_temporal_question, timestamp_to_seconds, get_prompt_preQrag, get_prompt_preQrag_temporal

load_dotenv()

class ChatService:
    """
    ChatService is a wrapper class of AsyncAzureOpenAI used for generating responses from Azure OpenAI LLM.
    It provides the ability to add system message, grounding text, and a generic prompt template.

    Args:
        azure_endpoint (str): Azure OpenAI Endpoint. Example: https://<YOUR_RESOURCE_NAME>.openai.azure.com/. Required.
        api_key (str): Azure OpenAI API Key. Required.
        deployment_name (str): Azure OpenAI Deployment Name. Example: gpt-4o-mini. Required.
        prompt_template_fp (str): Filepath to prompt template to be used in chatbot prompt. Default: "prompt_template.txt".
        temperature (float): Chatbot Temperature. Default: 0.
        embedding_model (str): Embedding Model. Default: "all-MiniLM-L6-v2".
    """
    def __init__(
            self,
            azure_endpoint: str = os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key: str = os.environ.get("AZURE_OPENAI_API_KEY"),
            deployment_name: str = os.environ.get("YOUR_DEPLOYMENT_NAME"),
            api_version : str = os.environ.get("OPENAI_API_VERSION"),
            temperature: float=0,
    ):
        self.azure_endpoint = azure_endpoint
        self.api_key = api_key
        self.api_version = api_version
        self.client = self.initiate_client()
        try:
            self.prompt_template = get_prompt_template()
            
            self.prompt_template_temporal = get_prompt_temporal_question()
        except Exception as e:
            print(e)
            self.prompt_template = ""
            
            self.prompt_template_temporal = ""
        self.chat_model = AzureChatOpenAI(
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
            azure_deployment=deployment_name,
            temperature=temperature
        )
        self.chat_db = ChatDatabaseService()

    async def query_evaluation(self, question: str, video_ids: list, course_code: str):
        """
        Evaluate a single question using PreQRAG routing and multi-video retrieval.
        
        Args:
            question (str): The user's question
            video_ids (list): List of video IDs to search in (empty list means all videos)
            course_code (str): Course code to search in
            
        Returns:
            tuple: (retrieval_results, context) - Retrieved documents and context information
        """
        try:
            # Step 1: Get video mapping from CosmosDB and filter by selected video_ids
            full_video_mapping = self.get_video_id_title_mapping(course_code)
            print(f"Full video mapping for course {course_code}: {full_video_mapping}")
            
            # Filter video mapping to only include selected video_ids
            if video_ids and len(video_ids) > 0:
                # Create a reverse mapping from video_id to video_name
                video_id_to_name = {v: k for k, v in full_video_mapping.get("video_map", {}).items()}
                filtered_video_map = {}
                for video_id in video_ids:
                    if video_id in video_id_to_name:
                        video_name = video_id_to_name[video_id]
                        filtered_video_map[video_name] = video_id
                video_mapping = {"video_map": filtered_video_map}
                print(f"Filtered video mapping for selected videos {video_ids}: {video_mapping}")
            else:
                # If no video_ids specified, use all videos
                video_mapping = full_video_mapping
                print(f"Using all videos for course {course_code}: {video_mapping}")
            
            # Step 2: Route question using PreQRAG
            json_results_llm = await self.route_pre_qrag_temporal(
                user_query=question, 
                video_map=video_mapping
            )
            print(f"PreQRAG routing result:\n{json_results_llm}")
            
            # Step 3: Extract routing information
            # routing_type = json_results_llm.get("routing_type")
            query_variants = json_results_llm.get("query_variants")
            
            # Step 4: Retrieve documents using the routed query variants
            retrieval_results, context = self.retrival_singledocs_multidocs_with_Temporal(query_variants)
            
            return retrieval_results, context
            
        except Exception as e:
            logger.error(f"Error in query_evaluation: {str(e)}")
            raise e

    def initiate_client(self):
        """
        Initialises a AsyncAzureOpenAI instance to interact with Azure OpenAI services.
        Uses provided Azure endpoint, API key, and API version.
        If an error occurs during initialization, the Azure endpoint and the exception are printed for debugging.

        Returns:
            AsyncAzureOpenAI: An initialised instance of the AsyncAzureOpenAI class.

        Raises:
            Exception: For any errors that occur during initialization.
        """
        try:
            return AsyncAzureOpenAI(
                azure_endpoint=self.azure_endpoint,
                api_key=self.api_key,
                api_version=self.api_version,
            )
        except Exception as ex:
            print("something happened here")
            print(ex)

    

    
    
    def generate_video_prompt_response(self, retrieval_results, user_input, previous_messages=None):
        
        """
        Generate response based on user prompt and selected video.

        Args:
            user_prompt (str): User prompt to query chatbot. Required.
            video_id (str): Video ID of the video selected. Required.
            :param previous_messages:
            :param user_input:
            :param retrieval_results:
        """
        if previous_messages is None:
            previous_messages = []
        try:
            formatted_history = "\n".join(
                [f"User: {msg.user_input}\nAssistant: {msg.assistant_response}" for msg in previous_messages])

            prompt = PromptTemplate(
                template=get_prompt_template(),
                input_variables=["context", "input", "history"]
            )

            context = retrieval_results

            combine_docs_chain = create_stuff_documents_chain(self.chat_model, prompt)

            # Generate the full prompt with context and input
            final_prompt = prompt.format(context=context, input=user_input, history=formatted_history)

            # Save the prompt to a file
            process_file(fp="generated_prompt.txt", mode="w", content=final_prompt)

            # Return the response
            return combine_docs_chain.invoke({
                "context": retrieval_results,
                "input": user_input,
                "history": formatted_history
            })
        except Exception as ex:
            print("Something happened: ", ex)
            return ex

    def get_video_id_title_mapping(self, course_code: str) -> dict:
        """
        Retrieve a mapping of video names to video IDs for a given course.

        Args:
            course_code (str): Course Code. Required.

        Returns:
            dict: {"video_map": {"<video_name>": "<video_id>", ...}}
        """
        # First, get the course document
        course_doc = self.chat_db.check_if_course_exist(course_code)
        if not course_doc:
            return {"video_map": {}}
        
        video_map = {}
        
        # Get the video ObjectIds from the course document
        video_object_ids = course_doc.get("videos", [])
        
        # For each video ObjectId, get the video document
        for video_object_id in video_object_ids:
            video_doc = self.chat_db.video_collection.find_one({"_id": video_object_id})
            if video_doc:
                video_id = video_doc.get("video_id")
                video_name = video_doc.get("name")
                if video_id and video_name:
                    video_map[video_name] = video_id
        
        return {"video_map": video_map}
   


    # Semantic Search on Uncleaned results
    def retrieve_results_prompt_naive(self, video_id, message, top_n: int = 5):
        docs_semantic = self.chat_db.retrieve_results_prompt_semantic(video_id, message)[:top_n]
        logger.info(list(docs_semantic))
        retrieval_results = [Document(page_content=doc['textContent']) for doc in docs_semantic]
        return retrieval_results, [doc['textContent'] for doc in docs_semantic]

    def retrieve_results_prompt_clean_naive(self, video_id, message, top_n: int = 5):
        print("hei1",video_id)
        docs_semantic = self.chat_db.retrieve_results_prompt_semantic_v2(video_id, message)[:top_n]
        logger.info(list(docs_semantic))
        retrieval_results = [Document(page_content=doc['textContent']) for doc in docs_semantic]
        return retrieval_results, [doc['textContent'] for doc in docs_semantic]

    # Text + Semantic Search on Uncleaned results
    def retrieve_results_prompt(self, video_id, message, top_n: int = 5):
        docs_semantic = self.chat_db.retrieve_results_prompt_semantic(video_id, message)
        docs_text = self.chat_db.retrieve_results_prompt_text(video_id, message)
        logger.info(list(docs_semantic))
        logger.info(list(docs_text))
        doc_lists = [docs_semantic, docs_text]
        # Enforce that retrieved docs are the same form for each list in retriever_docs
        for i in range(len(doc_lists)):
            doc_lists[i] = [
                {"_id": str(doc["_id"]), "text": doc["textContent"], "score": doc["score"]}
                for doc in doc_lists[i]]
        fused_documents = weighted_reciprocal_rank(doc_lists)[:top_n]
        retrieval_results = [Document(page_content=doc['text']) for doc in fused_documents]
        print(retrieval_results)
        return retrieval_results, [doc['text'] for doc in fused_documents]

    # Text + Semantic Search on Cleaned results
    def retrieve_results_prompt_clean(self, video_id, message, top_n: int=5):
        docs_semantic = self.chat_db.retrieve_results_prompt_semantic_v2(video_id, message)
        docs_text = self.chat_db.retrieve_results_prompt_text_v2(video_id, message)
        # logger.info(list(docs_semantic))
        # logger.info(list(docs_text))
        doc_lists = [docs_semantic, docs_text]
        # Enforce that retrieved docs are the same form for each list in retriever_docs
        for i in range(len(doc_lists)):
            doc_lists[i] = [
                {"_id": str(doc["_id"]), "text": doc["textContent"], "score": doc["score"]}
                for doc in doc_lists[i]]
        fused_documents = weighted_reciprocal_rank(doc_lists)[:top_n]
        retrieval_results = [Document(page_content=doc['text']) for doc in fused_documents]
        # print(retrieval_results)
        return retrieval_results, [doc['text'] for doc in fused_documents]
    
    # can retrieve from multiple videos and on cleaned results
    def retrieve_results_prompt_clean_multivid(self, video_ids, message, top_n: int=5):
        docs_semantic = self.chat_db.retrieve_results_prompt_semantic_v2_multivid(video_ids, message)
        docs_text = self.chat_db.retrieve_results_prompt_text_v2_multivid(video_ids, message)
        # logger.info(list(docs_semantic))
        # logger.info(list(docs_text))
        doc_lists = [docs_semantic, docs_text]
        # Enforce that retrieved docs are the same form for each list in retriever_docs
        for i in range(len(doc_lists)):
            doc_lists[i] = [
                {"_id": str(doc["_id"]), "text": doc["textContent"], "score": doc["score"]}
                for doc in doc_lists[i]]
        fused_documents = weighted_reciprocal_rank(doc_lists)[:top_n]
        retrieval_results = [Document(page_content=doc['text']) for doc in fused_documents]
        # print(retrieval_results)
        return retrieval_results, [doc['text'] for doc in fused_documents]

    # Check for temporal anchors from the question
    async def is_temporal_question(self, question: str) -> LLMIsTemporalResponse:
        try:
            prompt = PromptTemplate(
                template=self.prompt_template_temporal,
                input_variables=["question"]
            )

            chain = prompt | self.chat_model  # Using LangChain operator chaining
            result = await chain.ainvoke({"question": question})

            print('llm result', result)

            # Parse JSON-style result (be sure your LLM returns structured JSON)
            
            parsed = json.loads(result.content if hasattr(result, "content") else result)
            return LLMIsTemporalResponse(**parsed)
        
        except Exception as e:
            print(f"[is_temporal_question] Error: {e}")
            return False
         

    # Document Scope router that takes user_query and video_map and returns structured JSON
    async def route_pre_qrag(self, user_query: str, video_map: list) -> dict:
        """
        Call LLM with the PRE-QRAG routing prompt, injecting the user query and the video map.

        Args:
            user_query (str): The user's natural language question.
            video_map (list): Array of objects like {"name": str, "video_id": str}.

        Returns:
            dict: Parsed JSON with routing_type, video_ids, temporal signals, and query_variants.
        """
        try:
            prompt = PromptTemplate(
                template=get_prompt_preQrag(),
                input_variables=["user_query", "video_map"]
            )

            # Ensure video_map is injected as JSON text to the prompt
            video_map_json = json.dumps(video_map, ensure_ascii=False)

            chain = prompt | self.chat_model
            result = await chain.ainvoke({
                "user_query": user_query,
                "video_map": video_map_json
            })

            content = result.content if hasattr(result, "content") else str(result)
            return json.loads(content)
        except Exception as e:
            print(f"[route_pre_qrag] Error: {e}")
            
    # PreQRAG with Temporal checker
    async def route_pre_qrag_temporal(self, user_query: str, video_map: list) -> dict:
        """
        Call LLM with the PRE-QRAG routing prompt, injecting the user query and the video map.

        Args:
            user_query (str): The user's natural language question.
            video_map (list): Array of objects like {"name": str, "video_id": str}.

        Returns:
            dict: Parsed JSON with routing_type, video_ids, temporal signals, and query_variants.
        """
        try:
            prompt = PromptTemplate(
                template=get_prompt_preQrag_temporal(),
                input_variables=["user_query", "video_map"]
            )

            # Ensure video_map is injected as JSON text to the prompt
            video_map_json = json.dumps(video_map, ensure_ascii=False)

            chain = prompt | self.chat_model
            result = await chain.ainvoke({
                "user_query": user_query,
                "video_map": video_map_json
            })

            content = result.content if hasattr(result, "content") else str(result)
            return json.loads(content)
        except Exception as e:
            print(f"[route_pre_qrag] Error: {e}")
            
            
    def retrival_singledocs_multidocs(self, queryVariants, top_n: int=5):
        
        all_retrieval_results = []
        all_fused_documents = []

        def process_variant(index_and_variant):
            i, variant = index_and_variant
            vid_list = variant.get('video_ids')
            sub_query = variant.get('question')

            docs_semantic = self.chat_db.retrieve_results_prompt_semantic_v2_multivid(vid_list, sub_query)
            docs_text = self.chat_db.retrieve_results_prompt_text_v2_multivid(vid_list, sub_query)
            doc_lists = [docs_semantic, docs_text]
            for j in range(len(doc_lists)):
                doc_lists[j] = [
                    {"_id": str(doc["_id"]), "text": doc["textContent"], "score": doc["score"]}
                    for doc in doc_lists[j]
                ]
            fused_documents_local = weighted_reciprocal_rank(doc_lists)[:top_n]
            retrieval_results_local = [Document(page_content=doc['text']) for doc in fused_documents_local]
            print(f"Query variant {i}: {len(retrieval_results_local)} chunks")
            return retrieval_results_local, fused_documents_local

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(queryVariants) or 1) as executor:
            futures = [executor.submit(process_variant, (i, queryVariants[i])) for i in range(len(queryVariants))]
            for future in concurrent.futures.as_completed(futures):
                retrieval_results_local, fused_documents_local = future.result()
                all_retrieval_results.extend(retrieval_results_local)
                all_fused_documents.extend(fused_documents_local)

        return all_retrieval_results, [doc['text'] for doc in all_fused_documents]


    def retrival_singledocs_multidocs_with_Temporal(self, queryVariants, top_n: int=5):
            
            all_retrieval_results = []
            all_fused_documents = []

            def process_variant(index_and_variant):
                i, variant = index_and_variant
                vid_list = variant.get('video_ids')
                sub_query = variant.get('question')
                temporal_signal  = variant.get('temporal_signal')

                retrieval_results_local = []
                fused_documents_local = []

                if temporal_signal:
                    docs_temporal, temporal_fused_docs = self.chat_db.retrieve_chunks_by_timestamp(vid_list, temporal_signal)
                    print(f"Query variant {i}: {len(docs_temporal)} chunks")
                    retrieval_results_local.extend(docs_temporal)
                    fused_documents_local.extend(temporal_fused_docs)

                docs_semantic = self.chat_db.retrieve_results_prompt_semantic_v2_multivid(vid_list, sub_query)
                docs_text = self.chat_db.retrieve_results_prompt_text_v2_multivid(vid_list, sub_query)
                doc_lists = [docs_semantic, docs_text]
                for j in range(len(doc_lists)):
                    doc_lists[j] = [
                        {"_id": str(doc["_id"]), "text": doc["textContent"], "score": doc["score"]}
                        for doc in doc_lists[j]
                    ]
                fused_documents_rerank = weighted_reciprocal_rank(doc_lists)[:top_n]
                retrieval_results_rerank = [Document(page_content=doc['text']) for doc in fused_documents_rerank]
                print(f"Query variant {i}: {len(retrieval_results_rerank)} chunks")

                retrieval_results_local.extend(retrieval_results_rerank)
                fused_documents_local.extend(fused_documents_rerank)

                return retrieval_results_local, fused_documents_local

            with concurrent.futures.ThreadPoolExecutor(max_workers=len(queryVariants) or 1) as executor:
                futures = [executor.submit(process_variant, (i, queryVariants[i])) for i in range(len(queryVariants))]
                for future in concurrent.futures.as_completed(futures):
                    retrieval_results_local, fused_documents_local = future.result()
                    all_retrieval_results.extend(retrieval_results_local)
                    all_fused_documents.extend(fused_documents_local)

            return all_retrieval_results, [doc['text'] for doc in all_fused_documents]

    
    
 

    
    
