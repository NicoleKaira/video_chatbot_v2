# FastAPI Backend Implementation - Endpoints and Commands Summary

## Backend Framework and Environment

### Framework: FastAPI
- **Version**: 0.115.8
- **Server**: Uvicorn 0.34.0
- **Host**: 0.0.0.0
- **Port**: 8080
- **CORS**: Enabled for all origins

## Complete API Endpoints Summary

### 1. **Main Application Endpoints** (`main.py`)

#### Video Upload
- **POST** `/upload`
  - **Purpose**: Upload and process videos for indexing
  - **Input**: VideoList (course_code, video array)
  - **Response**: Confirmation message
  - **Background Task**: Video indexing process

---

### 2. **Chat Service Endpoints** (`/chat`)

#### Intelligent Question Answering
- **POST** `/chat/`
  - **Purpose**: Advanced question answering with PreQRAG routing
  - **Input**: ChatRequestBody (message, course_code, video_ids)
  - **Features**: 
    - PreQRAG intelligent routing
    - Multi-video retrieval
    - Temporal processing
    - Context-aware responses
  - **Response**: AI-generated answers with source context

---

### 3. **Broker Service Endpoints** (Content Management)

#### Visibility Management
- **PUT** `/visibility`
  - **Purpose**: Update visibility status of videos/courses
  - **Input**: UpdateRequestBody (id, type, newOption)
  - **Types**: VIDEO, COURSE
  - **Response**: Success/error message

#### Course Management
- **PUT** `/course`
  - **Purpose**: Update course details
  - **Input**: CourseDetailsRequest (course_detail)
  - **Response**: Success/error message

- **POST** `/course`
  - **Purpose**: Create new course
  - **Input**: CourseDetails (course_id, course_name, course_description)
  - **Response**: Success/error message

#### Video Management
- **PUT** `/video`
  - **Purpose**: Update video details
  - **Input**: VideoDetailsRequest (video_detail)
  - **Response**: Success/error message

#### Content Retrieval
- **GET** `/videos`
  - **Purpose**: Get all public videos
  - **Response**: Course-video mapping for end users

- **GET** `/videos/manage`
  - **Purpose**: Get all videos for admin management
  - **Response**: Complete course-video mapping (including private)

---

### 4. **Video Indexer Service Endpoints** (`/video_indexer`)

#### Video Widgets
- **GET** `/video_indexer/{video_id}`
  - **Purpose**: Get video player widget URL
  - **Input**: video_id (string)
  - **Response**: Video player widget URL

- **GET** `/video_indexer/insights/{video_id}`
  - **Purpose**: Get video insights widget URL
  - **Input**: video_id (string)
  - **Response**: Video insights widget URL

#### Testing Endpoints
- **GET** `/video_indexer/testing/{video_id}`
  - **Purpose**: Generate prompt content for video
  - **Input**: video_id (string)
  - **Response**: Prompt content generation

---

### 5. **User Authentication Endpoints** (`/auth`)

#### Authentication
- **POST** `/auth/login`
  - **Purpose**: User authentication and token generation
  - **Input**: UserDetails (username, password)
  - **Response**: JWT access token, role, user_id
  - **Security**: bcrypt password hashing, JWT tokens
  - **Token Expiry**: 24 hours (86400 seconds)

---

## API Architecture Summary

### **Router Organization**
```
FastAPI Application
├── /upload (main.py)
├── /chat (ChatService)
├── / (BrokerService)
├── /video_indexer (VideoIndexerService)
└── /auth (UserService)
```

### **HTTP Methods Distribution**
- **GET**: 5 endpoints (retrieval operations)
- **POST**: 3 endpoints (creation operations)
- **PUT**: 3 endpoints (update operations)

### **Service Categories**

#### 1. **Core Functionality**
- Video upload and processing
- Intelligent chat with AI
- Content management

#### 2. **Administrative Functions**
- Course and video management
- Visibility controls
- User authentication

#### 3. **Integration Services**
- Azure Video Indexer integration
- Widget URL generation
- Prompt content processing

### **Security Features**
- **CORS Middleware**: Cross-origin request handling
- **JWT Authentication**: Token-based security
- **Password Hashing**: bcrypt encryption
- **Role-based Access**: User role management

### **Background Processing**
- **Asynchronous Video Indexing**: Non-blocking video processing
- **Background Tasks**: Video upload and analysis
- **Token Management**: Automatic token refresh

### **Response Formats**
- **Success Responses**: JSON with message and data
- **Error Handling**: HTTP status codes with detailed messages
- **Data Models**: Pydantic models for request/response validation

## Implementation Commands

### **Development Server**
```bash
python main.py
# Runs on http://0.0.0.0:8080
```

### **API Documentation**
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

### **Environment Configuration**
- **Environment Variables**: Loaded via python-dotenv
- **Database**: MongoDB connection pooling
- **External Services**: Azure OpenAI, Azure Video Indexer

## Key Features

### **Advanced AI Integration**
- PreQRAG routing system
- Multi-video question answering
- Temporal document processing
- Context-aware responses

### **Content Management**
- Course and video lifecycle management
- Visibility controls
- Background processing
- Widget integration

### **Security & Authentication**
- JWT token-based authentication
- Role-based access control
- Secure password handling
- CORS protection

This FastAPI implementation provides a comprehensive backend for a video chatbot system with advanced AI capabilities, content management, and secure authentication.
