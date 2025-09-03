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


@router.post("/{video_id}", status_code=200)
async def evaluate_question(video_id: str, body: ChatRequestBody):
    """
    Evaluate a single question using the evaluation flow of temporal pipeline .
    """
    # start_time = time.time()
    question = body.message
    # Step 1: Check if the question is temporal
    is_temporal_res = await chat_service.is_temporal_question(question)
    is_temporal = is_temporal_res.is_temporal
    timestamp = is_temporal_res.timestamp

    if is_temporal:
        if timestamp:
            # Retrieve chunks based on the timestamp
            retrieval_results, _ = chat_service.retrieve_chunks_by_timestamp(video_id, timestamp)
            response = chat_service.generate_video_prompt_response(retrieval_results, question)
        else:
            # fallback if timestamp not extractable
            retrieval_results, _  = chat_service.retrieve_results_prompt_clean(video_id, question)
            response = chat_service.generate_video_prompt_response(retrieval_results, question)
    else:
        retrieval_results, _ = chat_service.retrieve_results_prompt_clean(video_id, question)
        response = chat_service.generate_video_prompt_response(retrieval_results, question)
    
    if response:
        return {"message": "Successfully Retrieve", "answer": response}
    else:
        return {"message": "No Records Found"}
