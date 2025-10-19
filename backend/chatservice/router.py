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
        # Use the new query_evaluation function from ChatService
        retrieval_results, context = await chat_service.query_evaluation(
            question=question,
            video_ids=video_ids,
            course_code=course_code
        )
        
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

