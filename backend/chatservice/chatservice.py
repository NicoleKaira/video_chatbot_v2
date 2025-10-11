import os
import concurrent.futures
import json
from pydoc import doc #nicole added

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
            #nicole added
            self.prompt_template_temporal = get_prompt_temporal_question()
        except Exception as e:
            print(e)
            self.prompt_template = ""
            #nicole added
            self.prompt_template_temporal = ""
        self.chat_model = AzureChatOpenAI(
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
            azure_deployment=deployment_name,
            temperature=temperature
        )
        self.chat_db = ChatDatabaseService()

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
    
    #nicole added for multivideo
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

    

    #nicole added
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
    

    #'delete later, shifted to repository.py (nicole)
    def retrieve_chunks_by_timestamp(self, video_id: str, timestamp: str):
        """
        Retrieve chunks from prompt_content_clean collection based on timestamp.
        
        Args:
            video_id (str): The video ID to search in
            timestamp (str): Timestamp in format "MM:SS" or "HH:MM:SS"
            
        Returns:
            list: List of documents that match the timestamp range
        """
        try:
            # Convert input timestamp to seconds
            target_seconds = timestamp_to_seconds(timestamp)
            
            # Get video reference
            video_reference = self.chat_db.video_collection.find_one({"video_id": video_id})
            if not video_reference:
                print(f"Video ID {video_id} not found")
                return []
            
            # Query the prompt_content_clean collection
            docs = self.chat_db.prompt_content_clean_index_collection.find(
                {"metadata.video_id": video_id},
                {
                    "_id": 1,
                    "textContent": 1,
                    "metadata": 1
                }
            )
            
            matching_docs = []
            
            for doc in docs:
                metadata = doc.get("metadata", {})
                start_time_str = metadata.get("start")
                end_time_str = metadata.get("end")
                
                if start_time_str and end_time_str:
                    try:
                        # Convert start and end times to seconds
                        start_seconds = timestamp_to_seconds(start_time_str)
                        end_seconds = timestamp_to_seconds(end_time_str)
                        
                        # Check if target timestamp is within range (start - 2min) to (end + 2min)
                        buffer_seconds = 120  # 2 minutes in seconds
                        range_start = start_seconds - buffer_seconds
                        range_end = end_seconds + buffer_seconds
                        
                        if range_start <= target_seconds <= range_end:
                            matching_docs.append(doc)
                            print(f"Found matching doc: start={start_time_str}, end={end_time_str}, target={timestamp}")
                            
                    except Exception as e:
                        print(f"Error parsing timestamp for doc {doc.get('_id')}: {e}")
                        continue
            # print(f"Found {len(matching_docs)} documents matching timestamp {timestamp}")
            retrieval_results = [Document(page_content=doc['textContent']) for doc in matching_docs]
            context = [doc['textContent'] for doc in matching_docs]
            return retrieval_results, context
            
        except Exception as e:
            print(f"[retrieve_chunks_by_timestamp] Error: {e}")
            return []
        

    # nicole: pre-QRAG router that takes user_query and video_map and returns structured JSON
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
            # Return a minimal fallback structure to avoid breaking callers
            # return {
            #     "routing_type": "GENERAL_KB",
            #     "user_query": user_query,
            #     "video_ids": [],
            #     "is_temporal": False,
            #     "temporal_signals": {
            #         "explicit_timestamps": [],
            #         "time_expressions": [],
            #         "ordinal_events": [],
            #         "relative_dates": []
            #     },
            #     "query_variants": [
            #         {"video_id": None, "question": user_query}
            #     ]
            # }

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


    def retrival_multidocs_with_Temporal(self, queryVariants, top_n: int=5):
            
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

    
    
    def retrival_singledocs_with_Temporal(self, queryVariants, top_n: int = 6):
        """
        Process query variants with temporal and semantic/text retrieval.
        queryVariants[0] uses semantic processing, queryVariants[1] uses text processing.
        """
        all_retrieval_results = []
        all_fused_documents = []

        def process_temporal_retrieval(vid_list, temporal_signal, variant_index):
            """Handle temporal retrieval if temporal_signal is provided."""
            if not temporal_signal:
                return [], []
            
            docs_temporal, temporal_fused_docs = self.chat_db.retrieve_chunks_by_timestamp(vid_list, temporal_signal)
            print(f"Query variant {variant_index}: {len(docs_temporal)} temporal chunks")
            return docs_temporal, temporal_fused_docs

        def process_document_retrieval(vid_list, sub_query, retrieval_type, variant_index):
            """Handle semantic or text document retrieval (no reranking)."""
            if retrieval_type == "semantic":
                docs = self.chat_db.retrieve_results_prompt_semantic_v2_multivid(vid_list, sub_query)
            else:  # text
                docs = self.chat_db.retrieve_results_prompt_text_v2_multivid(vid_list, sub_query)
            
            # Format documents for reranking (but don't rerank yet)
            formatted_docs = [
                {"_id": str(doc["_id"]), "text": doc["textContent"], "score": doc["score"]}
                for doc in docs
            ]
            
            # print(f"Query variant {variant_index}: Retrieved {len(formatted_docs)} {retrieval_type} documents")
            return formatted_docs

        def process_variant(variant, variant_index, retrieval_type):
            """Process a single query variant with specified retrieval type."""
            vid_list = variant.get('video_ids')
            sub_query = variant.get('question')
            temporal_signal = variant.get('temporal_signal')

            print ('this is the variant: ',variant)

            retrieval_results_local = []
            fused_documents_local = []

            # Process temporal retrieval if available
            temporal_docs, temporal_fused = process_temporal_retrieval(vid_list, temporal_signal, variant_index)
            retrieval_results_local.extend(temporal_docs)
            fused_documents_local.extend(temporal_fused)

            # Process document retrieval (semantic or text) - return both temporal and document results
            doc_results = process_document_retrieval(vid_list, sub_query, retrieval_type, variant_index)
            
            return retrieval_results_local, fused_documents_local, doc_results

        # Process variants with specific retrieval types concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both variants for concurrent processing
            future_to_variant = {}
            
            if len(queryVariants) > 0:
                # First variant uses semantic processing

                future_to_variant[executor.submit(process_variant, queryVariants[0], 0, "semantic")] = 0
            
            if len(queryVariants) > 1:
                # Second variant uses text processing
                future_to_variant[executor.submit(process_variant, queryVariants[1], 1, "text")] = 1
            
            # Collect results as they complete
            all_doc_lists = []  # Store document lists from both variants
            
            for future in concurrent.futures.as_completed(future_to_variant):
                variant_index = future_to_variant[future]
                try:
                    retrieval_results_local, fused_documents_local, doc_results = future.result()
                    
                    # Add temporal results
                    all_retrieval_results.extend(retrieval_results_local)
                    all_fused_documents.extend(fused_documents_local)
                    
                    # Store document results for combined reranking
                    all_doc_lists.append(doc_results)
                    
                except Exception as exc:
                    print(f'Query variant {variant_index} generated an exception: {exc}')
            
            # Apply weighted reciprocal rank to combined document lists from both variants
            if all_doc_lists:
                print(f"DEBUG: Combining {len(all_doc_lists)} document lists for weighted reciprocal rank")
                
                # Use weighted reciprocal rank for document fusion
                fused_documents_rerank = weighted_reciprocal_rank(all_doc_lists)[:top_n]
                retrieval_results_rerank = [Document(page_content=doc['text']) for doc in fused_documents_rerank]
                print(f"DEBUG: After weighted reciprocal rank: {len(retrieval_results_rerank)} chunks")
                
                # Add reranked results to final results
                all_retrieval_results.extend(retrieval_results_rerank)
                all_fused_documents.extend(fused_documents_rerank)

        return all_retrieval_results, [doc['text'] for doc in all_fused_documents]

    
    
