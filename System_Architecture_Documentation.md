# Video Chatbot System Architecture

## System Overview

This is a comprehensive video chatbot system built with a microservices architecture that provides intelligent video content analysis, transcript processing, and conversational AI capabilities. The system integrates Azure services, MongoDB, and advanced AI technologies to create an intelligent video analysis platform.

---

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│  • React/Next.js Frontend Application                                          │
│  • Video Upload Interface                                                      │
│  • Chat Interface                                                               │
│  • Content Management Dashboard                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  • FastAPI Application (main.py)                                               │
│  • CORS Middleware                                                              │
│  • Authentication & Authorization                                               │
│  • Request Routing                                                             │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        MICROSERVICES LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  Broker Service │  │  Chat Service    │  │ Video Indexer   │  │User Service│ │
│  │                 │  │                 │  │    Service      │  │             │ │
│  │ • Orchestration │  │ • PreQRAG       │  │                 │  │ • Auth      │ │
│  │ • Video Pipeline│  │ • AI Responses  │  │ • Azure Video   │  │ • JWT       │ │
│  │ • Status Mgmt   │  │ • Multi-video   │  │   Indexer       │  │ • Roles     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        PROCESSING LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Transcript      │  │ Embedding       │  │ Evaluation      │  │ Utils       │ │
│  │ Service         │  │ Service         │  │ Service         │  │ Service     │ │
│  │                 │  │                 │  │                 │  │             │ │
│  │ • AI Cleaning   │  │ • Text          │  │ • RAG          │  │ • Prompts   │ │
│  │ • Chunking      │  │   Embeddings    │  │   Evaluation   │  │ • Templates │ │
│  │ • Timestamp     │  │ • Vector Search │  │ • Metrics      │  │ • Helpers   │ │
│  │   Processing    │  │ • Similarity    │  │ • Testing      │  │ • Config    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ MongoDB         │  │ Azure Video     │  │ Azure OpenAI    │  │ File System │ │
│  │ Database        │  │ Indexer         │  │ Services        │  │ Storage     │ │
│  │                 │  │                 │  │                 │  │             │ │
│  │ • Videos        │  │ • Video Analysis│  │ • GPT Models    │  │ • Logs      │ │
│  │ • Transcripts   │  │ • OCR Data      │  │ • Embeddings    │  │ • Temp Files│ │
│  │ • Chat History  │  │ • Insights      │  │ • Chat Complet. │  │ • Config    │ │
│  │ • Users         │  │ • Thumbnails    │  │ • Text Analysis │  │ • Results   │ │
│  │ • Courses       │  │ • Widget URLs   │  │ • Prompt Eng.  │  │ • Cache     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Component Architecture

### 1. **API Gateway Layer**

#### FastAPI Application (`main.py`)
```python
# Core Application Structure
app = FastAPI()
app.include_router(video_indexer_router)  # /video_indexer/*
app.include_router(chat_router)          # /chat/*
app.include_router(broker_router)        # /* (broker service)
app.include_router(user_router)          # /auth/*

# Middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

**Key Features:**
- **CORS Support**: Cross-origin request handling
- **Router Management**: Modular endpoint organization
- **Background Tasks**: Asynchronous video processing
- **Authentication**: JWT-based security

---

### 2. **Microservices Layer**

#### A. **Broker Service** (Orchestration Hub)
```
┌─────────────────────────────────────────────────────────────┐
│                    BROKER SERVICE                           │
├─────────────────────────────────────────────────────────────┤
│  • Video Upload Orchestration                               │
│  • Status Management                                        │
│  • Course & Video Management                               │
│  • Visibility Controls                                      │
│  • Integration Coordination                                 │
└─────────────────────────────────────────────────────────────┘
```

**Responsibilities:**
- Orchestrates video processing pipeline
- Manages video and course lifecycle
- Coordinates between services
- Handles background processing

#### B. **Chat Service** (AI Intelligence)
```
┌─────────────────────────────────────────────────────────────┐
│                    CHAT SERVICE                             │
├─────────────────────────────────────────────────────────────┤
│  • PreQRAG Routing System                                  │
│  • Multi-video Question Answering                          │
│  • Temporal Document Processing                             │
│  • Context-aware Responses                                 │
│  • Conversation Management                                 │
└─────────────────────────────────────────────────────────────┘
```

**Advanced Features:**
- **PreQRAG Routing**: Intelligent query routing
- **Temporal Processing**: Time-aware document retrieval
- **Multi-video Support**: Cross-video question answering
- **Context Management**: Conversation history tracking

#### C. **Video Indexer Service** (Azure Integration)
```
┌─────────────────────────────────────────────────────────────┐
│                VIDEO INDEXER SERVICE                        │
├─────────────────────────────────────────────────────────────┤
│  • Azure Video Indexer Integration                         │
│  • Video Upload & Processing                               │
│  • Thumbnail Generation                                    │
│  • Widget URL Management                                   │
│  • Authentication Token Management                         │
└─────────────────────────────────────────────────────────────┘
```

**Azure Services Integration:**
- Video analysis and insights
- OCR data extraction
- Thumbnail generation
- Widget URL creation

#### D. **User Service** (Authentication)
```
┌─────────────────────────────────────────────────────────────┐
│                    USER SERVICE                             │
├─────────────────────────────────────────────────────────────┤
│  • JWT Authentication                                       │
│  • Password Hashing (bcrypt)                               │
│  • Role-based Access Control                               │
│  • User Management                                         │
└─────────────────────────────────────────────────────────────┘
```

---

### 3. **Processing Layer**

#### A. **Transcript Service**
```
┌─────────────────────────────────────────────────────────────┐
│                TRANSCRIPT SERVICE                           │
├─────────────────────────────────────────────────────────────┤
│  • AI-powered Transcript Cleaning                           │
│  • Chunk Processing (10,000 char chunks)                   │
│  • Timestamp Mapping                                       │
│  • Content Organization                                    │
└─────────────────────────────────────────────────────────────┘
```

#### B. **Embedding Service**
```
┌─────────────────────────────────────────────────────────────┐
│                EMBEDDING SERVICE                           │
├─────────────────────────────────────────────────────────────┤
│  • Text Embedding Generation                               │
│  • Vector Search Capabilities                              │
│  • Semantic Similarity Matching                            │
│  • Query Processing                                        │
└─────────────────────────────────────────────────────────────┘
```

#### C. **Evaluation Service**
```
┌─────────────────────────────────────────────────────────────┐
│                EVALUATION SERVICE                           │
├─────────────────────────────────────────────────────────────┤
│  • RAG Evaluation Metrics                                  │
│  • Performance Testing                                     │
│  • Quality Assessment                                      │
│  • Benchmarking                                            │
└─────────────────────────────────────────────────────────────┘
```

---

### 4. **Data Layer**

#### A. **MongoDB Database**
```
┌─────────────────────────────────────────────────────────────┐
│                    MONGODB DATABASE                         │
├─────────────────────────────────────────────────────────────┤
│  Collections:                                               │
│  • videos: Video metadata and processing status            │
│  • transcripts: Transcript data with timestamps             │
│  • chat_history: Conversation tracking                     │
│  • courses: Course information                             │
│  • users: User authentication data                         │
│  • video_indexer_raw: Raw Azure insights                   │
│  • prompt_context: AI prompt data                          │
└─────────────────────────────────────────────────────────────┘
```

**Database Features:**
- **Connection Pooling**: 5-20 connections
- **Singleton Pattern**: Efficient resource management
- **Environment Configuration**: Flexible deployment

#### B. **External Services**
```
┌─────────────────────────────────────────────────────────────┐
│                EXTERNAL SERVICES                            │
├─────────────────────────────────────────────────────────────┤
│  • Azure Video Indexer: Video analysis and insights        │
│  • Azure OpenAI: LLM services and embeddings              │
│  • File System: Logs, temp files, configuration          │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow Architecture

### 1. **Video Upload Flow**
```
Frontend → FastAPI → BrokerService → VideoService → Azure Video Indexer
    ↓
MongoDB ← TranscriptService ← Video Indexer Results
```

### 2. **Chat Processing Flow**
```
User Query → ChatService → PreQRAG Router → Query Variants
    ↓
Document Retrieval → Context Assembly → AI Response Generation
    ↓
Response → User Interface
```

### 3. **Authentication Flow**
```
User Credentials → UserService → bcrypt Verification → JWT Generation
    ↓
Token Storage → Protected Route Access
```

---

## Technology Stack

### **Backend Framework**
- **FastAPI**: 0.115.8 (Web framework)
- **Uvicorn**: 0.34.0 (ASGI server)
- **Python**: 3.8+ (Programming language)

### **Database**
- **MongoDB**: Document database
- **PyMongo**: 4.11.1 (MongoDB driver)

### **AI Services**
- **Azure OpenAI**: 1.62.0 (LLM services)
- **LangChain**: 0.3.6 (AI orchestration)
- **RAGAS**: 0.2.13 (RAG evaluation)

### **External Integrations**
- **Azure Video Indexer**: Video analysis
- **Azure AI Vision**: Image analysis
- **JWT**: Token-based authentication
- **bcrypt**: Password hashing

---

## Security Architecture

### **Authentication & Authorization**
```
┌─────────────────────────────────────────────────────────────┐
│                SECURITY LAYER                               │
├─────────────────────────────────────────────────────────────┤
│  • JWT Token Authentication                                │
│  • bcrypt Password Hashing                                  │
│  • Role-based Access Control                               │
│  • CORS Protection                                         │
│  • Environment Variable Security                           │
└─────────────────────────────────────────────────────────────┘
```

### **Data Protection**
- **Environment Variables**: Secure configuration
- **Connection Pooling**: Resource optimization
- **Error Handling**: Secure error responses
- **Input Validation**: Pydantic models

---

## Deployment Architecture

### **Development Environment**
```
┌─────────────────────────────────────────────────────────────┐
│                DEVELOPMENT SETUP                            │
├─────────────────────────────────────────────────────────────┤
│  • Local FastAPI Server (localhost:8080)                   │
│  • MongoDB Local/Cloud Instance                            │
│  • Azure Services (Video Indexer, OpenAI)                  │
│  • Environment Variables (.env)                            │
└─────────────────────────────────────────────────────────────┘
```

### **Production Considerations**
- **Containerization**: Docker support
- **Load Balancing**: Multiple instances
- **Database Scaling**: MongoDB clustering
- **Monitoring**: Logging and metrics
- **Security**: HTTPS, authentication

---

## Key Architectural Patterns

### 1. **Microservices Architecture**
- Modular service design
- Independent service scaling
- Service-to-service communication
- Centralized orchestration

### 2. **Repository Pattern**
- Data access abstraction
- Service layer separation
- Database independence
- Testing isolation

### 3. **Singleton Pattern**
- Database connection management
- Resource optimization
- Global state management

### 4. **Background Processing**
- Asynchronous task handling
- Non-blocking operations
- Queue-based processing
- Status tracking

---

## Performance Optimizations

### **Database Level**
- Connection pooling (5-20 connections)
- Indexed collections
- Efficient query patterns
- Caching strategies

### **Application Level**
- Background task processing
- Token-based authentication caching
- Chunked transcript processing
- Lazy loading patterns

### **External Services**
- Azure service optimization
- Embedding caching
- Widget URL caching
- Response optimization

---

## Monitoring & Logging

### **Application Monitoring**
- Request/response logging
- Error tracking
- Performance metrics
- Service health checks

### **Database Monitoring**
- Connection pool status
- Query performance
- Storage utilization
- Backup management

### **External Service Monitoring**
- Azure service status
- API rate limits
- Token expiration
- Service availability

---

This architecture provides a robust, scalable foundation for a video chatbot system with advanced AI capabilities, comprehensive content management, and secure authentication mechanisms.
