# Getting Started with VideoLearnRAG

This guide helps you install and run VideoLearnRAG locally (Windows/macOS/Linux). It covers environment setup, installing the library into a virtual environment, configuring your `.env`, and minimal examples for video processing and chat.

## 1) Prerequisites
- Python 3.9+
- An Azure OpenAI resource and deployment (model), with API key
- MongoDB instance (local or cloud)
- Azure Video Indexer account for video indexing

## 2) Create and activate a virtual environment

Windows (PowerShell):
```powershell
cd C:\Users\nicol\OneDrive\Desktop\Video_chatbot_v2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux (bash/zsh):
```bash
cd ~/Desktop/Video_chatbot_v2
python3 -m venv .venv
source .venv/bin/activate
```

## 3) Install the library

If working from this repo:
```bash
pip install -e backend/src/videoLearnRAG
# or, from repo root
pip install -e backend
```

## 4) Configure environment variables (.env)

Where does the code load .env from?
- The ChatService calls `load_dotenv()` without a path, so Python will look for the nearest `.env` from your current working directory up the folder tree.
- If you run `python test.py` from the repo root, place your `.env` at `Video_chatbot_v2/.env`.
- If you `cd backend` and run there, place it at `backend/.env`.

Start from the template at `backend/src/videoLearnRAG/.env-template`. Copy it to a real `.env` and fill values:
```text
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
YOUR_DEPLOYMENT_NAME=
YOUR_DEPLOYMENT_NAME_4O=
OPENAI_API_VERSION=

MONGODB_CONNECTION_STRING=
DB_NAME=

EMBEDDING_MODEL=

# Azure Video Indexer (if using video indexing)
AZURE_VIDEO_INDEXER_ACCOUNT_ID=
AZURE_VIDEO_INDEXER_LOCATION=
AZURE_VIDEO_INDEXER_API_KEY=

SECRET_KEY=
```

Minimum required keys to run ChatService:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `YOUR_DEPLOYMENT_NAME`
- `OPENAI_API_VERSION`
- `MONGODB_CONNECTION_STRING`

If you plan to index videos, also set AVI keys.

## 5) Minimal usage

### 5.1 Video processing (BrokerService)
```python
from videoLearnRAG.brokerservice.brokerService import BrokerService
from videoLearnRAG.videoindexerclient.model import Video, VideoList

# 1) Create course
broker = BrokerService()
broker.add_course(
    course_code="CS101",
    course_name="Intro to CS",
    course_description="Fundamentals of computer science"
)

# 2) Prepare videos
videos = VideoList(
    course_code="CS101",
    video=[
        Video(
            video_name="Lecture 1",
            video_description="Overview of the course",
            base64_encoded_video="<base64-encoded-video>"
        )
    ]
)

# 3) Start indexing
broker.start_video_index_process(videos)
# Output (on success): "Successfully indexed the video and changed status to complete"
```

What the pipeline does:
1. Validates the course exists
2. Registers video documents
3. Sends to Azure Video Indexer
4. Fetches insights and associates transcripts
5. Cleans transcript
6. Updates cleaned transcript in DB
7. Marks status as complete

### 5.2 Chat generation (ChatService)
```python
import asyncio
from videoLearnRAG.chatservice.chatservice import ChatService

async def main():
    chat = ChatService()
    # video_ids: list of video_indexer IDs to restrict context; [] uses all in the course
    retrieval_results, context = await chat.query_evaluation(
        question="What is mentioned at the 5 minute mark of each video?",
        video_ids=["zwb6lqhpzl", "tg2fy923h1"],
        course_code="SC1007"
    )
    print(retrieval_results, context)

asyncio.run(main())
```

## 6) Running your test.py
A simple example that mirrors your test layout:
```python
# test.py (run from repo root)
from videoLearnRAG.chatservice.chatservice import ChatService
import asyncio

async def test_query():
    cs = ChatService()
    result = await cs.query_evaluation(
        "what is mentioned at the 5 minutes mark of each video?",
        ["zwb6lqhpzl", "tg2fy923h1"],
        "SC1007"
    )
    print(result)

asyncio.run(test_query())
```
Run it after your venv is activated and `.env` is in place:
```powershell
python test.py
```

## 7) Common pitfalls
- Missing `.env` or wrong working directory (the loader won’t find your variables)
- Invalid Azure deployment name or API version
- MongoDB not running/reachable
- Not providing `base64_encoded_video` when indexing new videos

You’re ready to build with VideoLearnRAG!

