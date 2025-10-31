# VideoLearnRAG - Intelligent Video Analysis Library

A comprehensive Python library for intelligent video content analysis, transcript processing, and conversational AI capabilities. Built with FastAPI, Azure services, and advanced AI technologies.

## 🚀 Features

- **Video Processing**: Upload and index educational videos with Azure Video Indexer
- **Intelligent Chat**: Ask questions about video content using natural language
- **Multi-video Search**: Search across multiple videos simultaneously
- **Temporal Processing**: Time-aware document retrieval and analysis
- **Course Management**: Organize videos by courses and manage access
- **Transcript Cleaning**: AI-powered transcript processing and cleaning

## 📦 Installation

```bash
pip install videoLearnRAG
```

## 🏗️ Architecture

The library is built with a microservices architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    VideoLearnRAG Library                    │
├─────────────────────────────────────────────────────────────┤
│  • BrokerService    - Video processing orchestration      │
│  • ChatService      - Conversational AI and Q&A           │
│  • VideoIndexer     - Azure Video Indexer integration     │
│  • TranscriptService - Transcript processing and cleaning  │
│  • DatabaseService  - MongoDB connection management        │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Quick Start

### 1. Environment Setup

Create a `.env` file with your Azure credentials:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
YOUR_DEPLOYMENT_NAME=gpt-4o-mini
OPENAI_API_VERSION=2024-02-15-preview
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
```

### 2. Basic Usage

```python
from videoLearnRAG import BrokerService, ChatService

# Initialize services
broker = BrokerService()
chat = ChatService()

# Create a course
broker.add_course(
    course_code="CS101",
    course_name="Introduction to Computer Science",
    course_description="Basic computer science concepts"
)

# Add videos to the course
from videoLearnRAG.brokerservice.model import Video, VideoList

videos = VideoList(
    course_code="CS101",
    video=[
        Video(
            video_name="Lecture 1: Introduction",
            video_description="Overview of computer science",
            base64_encoded_video="your-base64-encoded-video-data"
        )
    ]
)

# Start video indexing
broker.start_video_index_process(videos)

# Query the videos
response = await chat.query_evaluation(
    course_code="CS101",
    video_ids=["video_id_1"],  # or [] for all videos
    query="What is computer science?"
)
```

## 📚 API Reference

### BrokerService

The BrokerService handles video processing orchestration and course management.

#### Methods

##### `add_course(course_code, course_name, course_description)`

Creates a new course in the database.

**Parameters:**
- `course_code` (str): Unique identifier for the course
- `course_name` (str): Display name of the course
- `course_description` (str): Description of the course content

**Example:**
```python
broker = BrokerService()
broker.add_course(
    course_code="MATH101",
    course_name="Calculus I",
    course_description="Introduction to differential and integral calculus"
)
```

##### `get_video_manage()`

Retrieves all videos under each course for management purposes.

**Returns:**
- `dict`: Course-Video information with management details

**Example:**
```python
videos = broker.get_video_manage()
print(f"Found {len(videos)} courses with videos")
```

##### `start_video_index_process(video_list: VideoList)`

Starts the comprehensive video indexing process.

**Process Flow:**
1. **Validation**: Validates Course ID existence
2. **Registration**: Registers videos in the database
3. **Indexing**: Sends videos to Azure Video Indexer
4. **Insights**: Fetches insights and associates transcripts
5. **Cleaning**: Performs transcript cleaning
6. **Update**: Updates clean transcript in database
7. **Completion**: Changes indexing status to complete

**Parameters:**
- `video_list` (VideoList): List of videos to be indexed

**Example:**
```python
from videoLearnRAG.brokerservice.model import Video, VideoList

# Create video list
video_list = VideoList(
    course_code="CS101",
    video=[
        Video(
            video_name="Lecture 1: Algorithms",
            video_description="Introduction to algorithms and data structures",
            base64_encoded_video="your-video-data-here"
        ),
        Video(
            video_name="Lecture 2: Data Structures",
            video_description="Arrays, linked lists, and trees",
            base64_encoded_video="your-video-data-here"
        )
    ]
)

# Start indexing process
broker.start_video_index_process(video_list)
# Output: "Successfully indexed the video and changed status to complete"
```

### ChatService

The ChatService provides conversational AI capabilities for querying video content.

#### Methods

##### `query_evaluation(course_code, video_ids, query)`

Evaluates a query against video content using advanced PreQRAG routing and multi-video retrieval.

**Parameters:**
- `course_code` (str): Course code that videos are associated with
- `video_ids` (list): List of video IDs to search in (empty list = all videos in course)
- `query` (str): User's natural language question

**Returns:**
- `Response`: LLM-generated response based on video content

**Features:**
- **PreQRAG Routing**: Intelligent query routing system
- **Multi-video Support**: Search across multiple videos simultaneously
- **Temporal Processing**: Time-aware document retrieval
- **Context Management**: Maintains conversation history

**Example:**
```python
# Query specific videos
response = await chat.query_evaluation(
    course_code="CS101",
    video_ids=["video_id_1", "video_id_2"],
    query="What are the main algorithms discussed in these lectures?"
)

# Query all videos in a course
response = await chat.query_evaluation(
    course_code="CS101",
    video_ids=[],  # Empty list = all videos
    query="Summarize the key concepts from this course"
)

# Temporal query
response = await chat.query_evaluation(
    course_code="CS101",
    video_ids=["video_id_1"],
    query="What did the professor say at 15:30 about binary trees?"
)
```

## 📋 Data Models

### Video Model

```python
class Video(BaseModel):
    video_name: str
    base64_encoded_video: Optional[str] = None
    video_id: Optional[str] = None
    video_description: str
```

### VideoList Model

```python
class VideoList(BaseModel):
    course_code: str
    video: List[Video]
```

## 🔍 Advanced Features

### PreQRAG Routing System

The ChatService uses an advanced PreQRAG (Pre-Query Retrieval Augmented Generation) routing system that:

- **Analyzes queries** to determine the best retrieval strategy
- **Routes to appropriate videos** based on content relevance
- **Handles temporal queries** with timestamp-aware retrieval
- **Supports multi-video queries** with intelligent document fusion

### Temporal Processing

The system can handle time-based queries:

```python
# Find content at specific timestamps
response = await chat.query_evaluation(
    course_code="CS101",
    video_ids=["video_id_1"],
    query="What was discussed at 10:30 in the lecture?"
)

# Find content within time ranges
response = await chat.query_evaluation(
    course_code="CS101",
    video_ids=["video_id_1"],
    query="What concepts were covered in the first 20 minutes?"
)
```

### Multi-video Search

Search across multiple videos simultaneously:

```python
# Compare concepts across videos
response = await chat.query_evaluation(
    course_code="CS101",
    video_ids=["lecture_1", "lecture_2", "lecture_3"],
    query="How do the algorithms discussed in these lectures relate to each other?"
)
```

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | Yes |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Yes |
| `YOUR_DEPLOYMENT_NAME` | Azure OpenAI deployment name | Yes |
| `OPENAI_API_VERSION` | OpenAI API version | Yes |
| `MONGODB_CONNECTION_STRING` | MongoDB connection string | Yes |

### Dependencies

The library requires Python 3.9+ and includes these key dependencies:

- `fastapi>=0.115.8` - Web framework
- `uvicorn>=0.34.0` - ASGI server
- `pymongo>=4.11.1` - MongoDB driver
- `openai>=1.62.0` - OpenAI client
- `langchain>=0.3.6` - LLM orchestration
- `azure-ai-vision-imageanalysis>=1.0.0` - Azure Vision services

## 📖 Usage Examples

### Complete Workflow Example

```python
import asyncio
from videoLearnRAG import BrokerService, ChatService
from videoLearnRAG.brokerservice.model import Video, VideoList

async def main():
    # Initialize services
    broker = BrokerService()
    chat = ChatService()
    
    # 1. Create a course
    broker.add_course(
        course_code="AI101",
        course_name="Introduction to AI",
        course_description="Fundamentals of artificial intelligence"
    )
    
    # 2. Prepare videos
    videos = VideoList(
        course_code="AI101",
        video=[
            Video(
                video_name="AI Basics",
                video_description="Introduction to AI concepts",
                base64_encoded_video="your-video-data"
            )
        ]
    )
    
    # 3. Index videos
    broker.start_video_index_process(videos)
    
    # 4. Query the content
    response = await chat.query_evaluation(
        course_code="AI101",
        video_ids=[],
        query="What are the main types of machine learning?"
    )
    
    print(f"AI Response: {response}")

# Run the example
asyncio.run(main())
```

### Error Handling

```python
try:
    # Start video indexing
    broker.start_video_index_process(video_list)
except Exception as e:
    print(f"Video indexing failed: {e}")
    # Handle error appropriately

try:
    # Query videos
    response = await chat.query_evaluation(
        course_code="CS101",
        video_ids=["invalid_id"],
        query="Test query"
    )
except Exception as e:
    print(f"Query failed: {e}")
    # Handle error appropriately
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the examples in this README

---

**VideoLearnRAG** - Making video content searchable and conversational through AI.

## Getting Started (Quick Link)

See GETTING_STARTED.md for step-by-step installation, .env setup, and minimal examples to run `test.py` locally.
