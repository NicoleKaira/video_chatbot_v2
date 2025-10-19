
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware

from brokerservice.brokerService import BrokerService
from videoindexerclient.model import VideoList
from videoindexerclient.router import router as video_indexer_router
from chatservice.router import router as chat_router
from brokerservice.router import router as broker_router
from userservice.router import router as user_router

load_dotenv()
relative_path = "backend/"

app = FastAPI()
app.include_router(video_indexer_router)
app.include_router(chat_router)
app.include_router(broker_router)
app.include_router(user_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

broker_service = BrokerService()

@app.post("/upload", status_code=200)
def upload_video(video_list: VideoList, background_tasks: BackgroundTasks):
    background_tasks.add_task(broker_service.start_video_index_process, video_list)
    return {"message": "Video Index process started"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

