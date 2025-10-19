# Backend Implementation Report - Video Chatbot System

## Project Overview
This is a comprehensive video chatbot system built with FastAPI that provides intelligent video content analysis, transcript processing, and conversational AI capabilities. The system integrates Azure Video Indexer, OpenAI services, and MongoDB for a complete video-to-chat pipeline.

## Backend Architecture

### Core Framework & Dependencies
```
FastAPI (0.115.8) - Main web framework
Uvicorn (0.34.0) - ASGI server
MongoDB (PyMongo 4.11.1) - Database
Azure OpenAI (1.62.0) - LLM services
LangChain (0.3.6) - LLM orchestration
```

### Directory Structure

```
backend/
├── main.py                          # FastAPI application entry point
├── requirements.txt                  # Python dependencies
├── loggingConfig.py                 # Logging configuration
├── utils.py                         # Utility functions and prompt templates
├── calculate.py                     # Calculation utilities
├── EmbeddingService.py              # Text embedding service
├── EvaluatorServiceV2.py           # Evaluation service v2
├── EvaluatorServiceV3.py            # Evaluation service v3
│
├── brokerservice/                   # Video processing orchestration
│   ├── __init__.py
│   ├── brokerService.py            # Main broker service
│   ├── model.py                    # Data models
│   ├── repository.py               # Database operations
│   ├── router.py                   # API endpoints
│   └── status.py                   # Status definitions
│
├── chatservice/                     # Conversational AI service
│   ├── __init__.py
│   ├── chatservice.py              # Core chat logic
│   ├── model.py                    # Chat data models
│   ├── repository.py              # Chat database operations
│   ├── router.py                  # Chat API endpoints
│   └── utils.py                   # Chat utilities
│
├── databaseservice/                 # Database connection management
│   └── databaseService.py          # MongoDB singleton service
│
├── transcriptservice/              # Transcript processing
│   ├── __init__.py
│   ├── TranscriptService.py        # Transcript cleaning & processing
│   └── repository.py              # Transcript database operations
│
├── userservice/                     # User management
│   ├── __init__.py
│   ├── model.py                    # User data models
│   ├── repository.py              # User database operations
│   └── router.py                  # User API endpoints
│
├── videoindexerclient/             # Azure Video Indexer integration
│   ├── __init__.py
│   ├── Consts.py                   # Constants and configuration
│   ├── model.py                    # Video data models
│   ├── repository.py              # Video database operations
│   ├── router.py                  # Video API endpoints
│   ├── utils.py                   # Video utilities
│   ├── VideoIndexerClient.py      # Azure Video Indexer client
│   └── VideoService.py            # Video processing service
│
└── evaluation_results/             # Evaluation data storage
    ├── evaluation_results_*.json   # Various evaluation results
    └── results/                    # Additional result files
```

## Core Services Implementation

### 1. Main Application (`main.py`)
- **FastAPI Application Setup**: CORS middleware, router registration
- **Background Tasks**: Asynchronous video processing
- **Service Integration**: Orchestrates all microservices
- **Entry Point**: Runs on port 8080

### 2. Broker Service (`brokerservice/`)
**Purpose**: Central orchestration service for video processing pipeline

**Key Components**:
- `brokerService.py`: Main orchestration logic
- `repository.py`: Database operations for video management
- `router.py`: API endpoints for video operations
- `model.py`: Data models for courses and videos

**Core Functionality**:
- Video registration and validation
- Course management
- Video status tracking
- Integration with Video Indexer and Transcript services

### 3. Chat Service (`chatservice/`)
**Purpose**: Conversational AI and question-answering system

**Key Components**:
- `chatservice.py`: Core chat logic with PreQRAG routing
- `repository.py`: Chat history and context management
- `router.py`: Chat API endpoints
- `utils.py`: Chat utilities and ranking algorithms

**Advanced Features**:
- **PreQRAG Routing**: Intelligent query routing system
- **Temporal Processing**: Time-aware document retrieval
- **Multi-video Support**: Cross-video question answering
- **Context Management**: Conversation history tracking

### 4. Video Indexer Client (`videoindexerclient/`)
**Purpose**: Azure Video Indexer integration for video analysis

**Key Components**:
- `VideoIndexerClient.py`: Azure Video Indexer API client
- `VideoService.py`: Video processing service
- `utils.py`: Authentication and token management

**Core Functionality**:
- Video upload and indexing
- Thumbnail extraction
- Prompt content generation
- Widget URL generation
- Authentication token management

### 5. Transcript Service (`transcriptservice/`)
**Purpose**: Transcript processing and cleaning

**Key Components**:
- `TranscriptService.py`: Transcript cleaning and processing
- `repository.py`: Transcript database operations

**Core Functionality**:
- Transcript extraction from video insights
- AI-powered transcript cleaning
- Timestamp mapping
- Chunk processing for large transcripts

### 6. Database Service (`databaseservice/`)
**Purpose**: MongoDB connection management

**Key Features**:
- Singleton pattern for connection pooling
- Connection pool optimization (5-20 connections)
- Environment-based configuration
- Automatic connection management

### 7. User Service (`userservice/`)
**Purpose**: User authentication and management

**Key Components**:
- `model.py`: User data models
- `repository.py`: User database operations
- `router.py`: User API endpoints

## Advanced Features

### 1. PreQRAG Routing System
- **Intelligent Query Analysis**: Determines optimal retrieval strategy
- **Query Variants**: Generates multiple query formulations
- **Temporal Awareness**: Time-based document retrieval
- **Multi-document Support**: Cross-video information synthesis

### 2. Evaluation Framework
- **EvaluatorServiceV2/V3**: Comprehensive evaluation system
- **Multiple Evaluation Metrics**: Various RAG evaluation approaches
- **Temporal Evaluation**: Time-aware evaluation methods
- **Performance Tracking**: Detailed evaluation result storage

### 3. Embedding Service
- **Text Embeddings**: Azure OpenAI embedding generation
- **Vector Search**: Semantic similarity matching
- **Query Processing**: Embedding-based query understanding

## API Endpoints Structure

### Video Management
- `POST /upload` - Video upload and processing
- `GET /videos` - Retrieve video information
- `POST /courses` - Course management

### Chat Interface
- `POST /chat/` - Main chat endpoint with PreQRAG routing
- `GET /chat/history` - Chat history retrieval

### User Management
- `POST /users/login` - User authentication
- `GET /users/profile` - User profile management

## Data Models

### Core Models
- **VideoList**: Video collection with course association
- **ChatRequestBody**: Chat request with message and context
- **User**: User authentication and role management
- **CourseDetails**: Course information structure

### Database Collections
- **videos**: Video metadata and processing status
- **transcripts**: Transcript data with timestamps
- **chat_history**: Conversation tracking
- **courses**: Course information
- **users**: User authentication data

## Integration Points

### External Services
1. **Azure Video Indexer**: Video analysis and insights
2. **Azure OpenAI**: LLM services and embeddings
3. **MongoDB**: Primary database storage
4. **FastAPI**: Web framework and API management

### Internal Services
1. **Broker Service**: Central orchestration
2. **Chat Service**: Conversational AI
3. **Transcript Service**: Content processing
4. **Video Service**: Video management
5. **User Service**: Authentication

## Performance Optimizations

### Database
- Connection pooling for MongoDB
- Efficient query patterns
- Indexed collections for fast retrieval

### Processing
- Asynchronous video processing
- Background task management
- Chunked transcript processing
- Token-based authentication caching

### Caching
- Access token management
- Connection pooling
- Result caching for repeated queries

## Security Features

### Authentication
- Azure AD integration
- Token-based authentication
- Role-based access control

### Data Protection
- Environment variable configuration
- Secure API key management
- CORS middleware protection

## Deployment Configuration

### Environment Variables
- `MONGODB_CONNECTION_STRING`: Database connection
- `AZURE_OPENAI_ENDPOINT`: OpenAI service endpoint
- `AZURE_OPENAI_API_KEY`: API authentication
- `YOUR_DEPLOYMENT_NAME`: Model deployment
- `OPENAI_API_VERSION`: API version

### Server Configuration
- Host: 0.0.0.0
- Port: 8080
- CORS: Enabled for all origins
- Background tasks: Enabled

## Evaluation and Testing

### Evaluation Services
- **EvaluatorServiceV2**: Basic evaluation framework
- **EvaluatorServiceV3**: Advanced evaluation with temporal support
- **Multiple Evaluation Methods**: Naive, PreQRAG, Temporal, and Combined approaches

### Test Data
- Evaluation results stored in JSON format
- Multiple evaluation scenarios
- Performance metrics tracking

## Conclusion

This backend implementation provides a robust, scalable foundation for a video chatbot system with advanced AI capabilities. The modular architecture ensures maintainability, while the integration of Azure services provides enterprise-grade functionality. The system successfully combines video processing, natural language understanding, and conversational AI to create an intelligent video analysis platform.
