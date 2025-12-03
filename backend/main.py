
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, Query
from starlette.middleware.cors import CORSMiddleware
from typing import Optional
import os
from datetime import datetime

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

@app.get("/logs")
def get_logs(
    lines: Optional[int] = Query(default=100, description="Number of recent log lines to fetch"),
    since: Optional[str] = Query(default=None, description="ISO timestamp to fetch logs since (optional)")
):
    """
    Fetch recent log messages from message.log file.
    
    Args:
        lines: Number of recent lines to fetch (default: 100)
        since: ISO timestamp string to fetch logs since (optional)
    
    Returns:
        Dictionary with log entries and metadata
    """
    # Try multiple possible locations for the log file
    # The logger creates it in the current working directory
    possible_paths = [
        "message.log",  # Current working directory (where server is run from)
        os.path.join(relative_path, "message.log"),  # backend/message.log
        os.path.join(os.path.dirname(__file__), "message.log"),  # Same directory as main.py
    ]
    
    log_file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            log_file_path = path
            break
    
    try:
        if not log_file_path or not os.path.exists(log_file_path):
            return {
                "logs": [], 
                "total_lines": 0, 
                "error": f"Log file not found. Checked: {', '.join(possible_paths)}"
            }
        
        # Try to read with UTF-8, fallback to latin-1 or error handling
        try:
            with open(log_file_path, 'r', encoding='utf-8', errors='replace') as f:
                all_lines = f.readlines()
        except UnicodeDecodeError:
            # If UTF-8 fails, try with latin-1 encoding (handles most cases)
            with open(log_file_path, 'r', encoding='latin-1', errors='replace') as f:
                all_lines = f.readlines()
        
        total_lines = len(all_lines)
        
        # Filter by timestamp if provided
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
                filtered_lines = []
                for line in all_lines:
                    # Extract timestamp from log line (format: YYYY-MM-DD HH:MM:SS,mmm)
                    try:
                        timestamp_str = line[:23]  # First 23 characters contain timestamp
                        log_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                        if log_dt >= since_dt:
                            filtered_lines.append(line.strip())
                    except:
                        # If timestamp parsing fails, include the line anyway
                        filtered_lines.append(line.strip())
                log_entries = filtered_lines[-lines:] if len(filtered_lines) > lines else filtered_lines
            except Exception as e:
                return {"logs": [], "total_lines": total_lines, "error": f"Invalid timestamp format: {str(e)}"}
        else:
            # Get last N lines
            log_entries = [line.strip() for line in all_lines[-lines:]]
        
        return {
            "logs": log_entries,
            "total_lines": total_lines,
            "returned_lines": len(log_entries)
        }
    
    except Exception as e:
        return {"logs": [], "total_lines": 0, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, access_log=False)

