from pydantic import BaseModel


class ChatHistory(BaseModel):
    user_input: str
    assistant_response: str

class ChatRequestBody(BaseModel):
    previous_messages: list[ChatHistory] = []
    message: str

class LLMIsTemporalResponse(BaseModel):
    is_temporal: bool
    timestamp: str

class QuestionTypeReponse(BaseModel):
   classification: str
   Video_ids: list[str]
   subQuestion: list[str]
