import logging

from dotenv import load_dotenv
from fastapi import APIRouter

from chatservice.chatservice import ChatService
from chatservice.model import ChatRequestBody


load_dotenv()
ROUTE_PREFIX = "/chat"

router = APIRouter(prefix=ROUTE_PREFIX, tags=["chat-service"])


chat_service = ChatService()


# @router.post("/{video_id}", status_code=200)
# async def get_videos(video_id: str, body: ChatRequestBody):
#     retrieval_results, _ = chat_service.retrieve_results_prompt_clean(video_id, body.message)
#     response = chat_service.generate_video_prompt_response(retrieval_results, body.message, body.previous_messages)
#     if response:
#         return {"message": "Successfully Retrieve", "answer": response}
#     else:
#         return {"message": "No Records Found"}


@router.post("/", status_code=200)
async def evaluate_question(body: ChatRequestBody):
    """
    Evaluate a single question using PreQRAG routing and multi-video retrieval.
    """
    question = body.message
    video_ids = body.video_ids  # Get list of video IDs from request body
    course_code = body.course_code  # Get course code from request body
    
    try:
        # Step 1: Get video mapping from CosmosDB
        
        video_mapping = chat_service.get_video_id_title_mapping(course_code)
        print(f"Video mapping for course {course_code}: {video_mapping}")
        
        # Step 2: Route question using PreQRAG
        json_results_llm = await chat_service.route_pre_qrag_temporal(
            user_query=question, 
            video_map=video_mapping
        )
        print(f"PreQRAG routing result:\n{json_results_llm}")
        
        # Step 3: Extract routing information
        routing_type = json_results_llm.get("routing_type")
        query_variants = json_results_llm.get("query_variants")
        
        # Step 4: Retrieve documents using the routed query variants
        retrieval_results, context = chat_service.retrival_singledocs_multidocs_with_Temporal(query_variants)
        
        # Step 5: Generate answer using retrieved context
        response = chat_service.generate_video_prompt_response(retrieval_results, question)
        
        if response:
            return {"message": "Successfully Retrieve", "answer": response}
        else:
            return {"message": "No Records Found"}
            
    except Exception as e:
        print(f"Error processing question: {e}")
        # Fallback to simple retrieval if PreQRAG fails
        try:
            retrieval_results, _ = chat_service.retrieve_results_prompt_clean_multivid(video_ids, question)
            response = chat_service.generate_video_prompt_response(retrieval_results, question)
            
            if response:
                return {"message": "Successfully Retrieve", "answer": response}
            else:
                return {"message": "No Records Found"}
        except Exception as fallback_error:
            print(f"Fallback retrieval also failed: {fallback_error}")
            return {"message": "Error processing request"}

