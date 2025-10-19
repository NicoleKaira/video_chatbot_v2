# Backend-Frontend Integration Guide
## Connecting Your Video Chatbot Backend to Any Frontend Application

This guide explains how to integrate your existing FastAPI backend with any frontend application, covering the complete workflow from video upload to chatbot responses.

## Table of Contents
1. [Backend API Overview](#backend-api-overview)
2. [Frontend Integration Steps](#frontend-integration-steps)
3. [Complete Workflow Implementation](#complete-workflow-implementation)
4. [Authentication Setup](#authentication-setup)
5. [Error Handling](#error-handling)
6. [Testing & Deployment](#testing--deployment)

---

## Backend API Overview

### Base URL
```
http://localhost:8080
```

### Key Endpoints for Frontend Integration
- **Video Upload**: `POST /upload`
- **Chat Interface**: `POST /chat/`
- **Content Management**: `GET /videos`, `PUT /visibility`
- **Authentication**: `POST /auth/login`

---

## Frontend Integration Steps

### 1. **Environment Setup**

#### Backend Configuration
```bash
# Ensure your backend is running
cd backend
python main.py
# Server runs on http://localhost:8080
```

#### Frontend Environment Variables
```javascript
// Create .env file in your frontend project
const API_BASE_URL = 'http://localhost:8080';
const API_ENDPOINTS = {
  UPLOAD: '/upload',
  CHAT: '/chat/',
  VIDEOS: '/videos',
  LOGIN: '/auth/login'
};
```

### 2. **HTTP Client Setup**

#### JavaScript/React Example
```javascript
// apiClient.js
class ApiClient {
  constructor(baseURL = 'http://localhost:8080') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('authToken');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Request failed');
      }
      
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Authentication
  async login(username, password) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    
    this.token = response.access_token;
    localStorage.setItem('authToken', this.token);
    return response;
  }

  // Video Upload
  async uploadVideo(courseCode, videos) {
    return await this.request('/upload', {
      method: 'POST',
      body: JSON.stringify({
        course_code: courseCode,
        video: videos.map(video => ({
          video_name: video.name,
          video_description: video.description,
          base64_encoded_video: video.base64Data
        }))
      })
    });
  }

  // Chat Interface
  async sendMessage(message, courseCode, videoIds = []) {
    return await this.request('/chat/', {
      method: 'POST',
      body: JSON.stringify({
        message: message,
        course_code: courseCode,
        video_ids: videoIds
      })
    });
  }

  // Get Videos
  async getVideos() {
    return await this.request('/videos');
  }
}

export default new ApiClient();
```

#### Python/Flask Example
```python
# api_client.py
import requests
import json

class VideoChatbotAPI:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            return data
        else:
            raise Exception("Login failed")
    
    def upload_video(self, course_code, videos):
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        response = requests.post(
            f"{self.base_url}/upload",
            json={
                "course_code": course_code,
                "video": videos
            },
            headers=headers
        )
        return response.json()
    
    def send_message(self, message, course_code, video_ids=None):
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        response = requests.post(
            f"{self.base_url}/chat/",
            json={
                "message": message,
                "course_code": course_code,
                "video_ids": video_ids or []
            },
            headers=headers
        )
        return response.json()
```

---

## Complete Workflow Implementation

### 1. **Video Upload Workflow**

#### Frontend Implementation
```javascript
// VideoUploadComponent.jsx
import React, { useState } from 'react';
import apiClient from './apiClient';

const VideoUploadComponent = () => {
  const [uploading, setUploading] = useState(false);
  const [videos, setVideos] = useState([]);
  const [courseCode, setCourseCode] = useState('');

  const handleFileUpload = async (files) => {
    const videoFiles = Array.from(files).map(file => ({
      name: file.name,
      description: `Video: ${file.name}`,
      base64Data: await convertToBase64(file)
    }));
    
    setVideos(videoFiles);
  };

  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
    });
  };

  const handleUpload = async () => {
    setUploading(true);
    try {
      const response = await apiClient.uploadVideo(courseCode, videos);
      console.log('Upload successful:', response);
      // Handle success (redirect, show message, etc.)
    } catch (error) {
      console.error('Upload failed:', error);
      // Handle error
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input 
        type="text" 
        placeholder="Course Code" 
        value={courseCode}
        onChange={(e) => setCourseCode(e.target.value)}
      />
      <input 
        type="file" 
        multiple 
        accept="video/*"
        onChange={(e) => handleFileUpload(e.target.files)}
      />
      <button onClick={handleUpload} disabled={uploading}>
        {uploading ? 'Uploading...' : 'Upload Videos'}
      </button>
    </div>
  );
};
```

### 2. **Chat Interface Workflow**

#### Frontend Implementation
```javascript
// ChatComponent.jsx
import React, { useState, useEffect } from 'react';
import apiClient from './apiClient';

const ChatComponent = ({ courseCode, selectedVideos = [] }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await apiClient.sendMessage(
        inputMessage, 
        courseCode, 
        selectedVideos
      );
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.answer || response.message,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="content">{message.content}</div>
            <div className="timestamp">{message.timestamp.toLocaleTimeString()}</div>
          </div>
        ))}
        {loading && <div className="loading">AI is thinking...</div>}
      </div>
      
      <div className="input-area">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask a question about the videos..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !inputMessage.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};
```

### 3. **Video Management Workflow**

#### Frontend Implementation
```javascript
// VideoManagementComponent.jsx
import React, { useState, useEffect } from 'react';
import apiClient from './apiClient';

const VideoManagementComponent = () => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      const response = await apiClient.getVideos();
      setVideos(response.course_video_mapping || []);
    } catch (error) {
      console.error('Failed to load videos:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateVisibility = async (id, type, newOption) => {
    try {
      await apiClient.request('/visibility', {
        method: 'PUT',
        body: JSON.stringify({ id, type, newOption })
      });
      loadVideos(); // Refresh the list
    } catch (error) {
      console.error('Failed to update visibility:', error);
    }
  };

  if (loading) return <div>Loading videos...</div>;

  return (
    <div className="video-management">
      <h2>Video Management</h2>
      {videos.map(course => (
        <div key={course.course_id} className="course-section">
          <h3>{course.course_name}</h3>
          {course.videos.map(video => (
            <div key={video.video_id} className="video-item">
              <span>{video.video_name}</span>
              <select 
                value={video.visibility}
                onChange={(e) => updateVisibility(video.video_id, 'VIDEO', e.target.value)}
              >
                <option value="public">Public</option>
                <option value="private">Private</option>
              </select>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};
```

---

## Authentication Setup

### 1. **Login Component**
```javascript
// LoginComponent.jsx
import React, { useState } from 'react';
import apiClient from './apiClient';

const LoginComponent = ({ onLogin }) => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await apiClient.login(credentials.username, credentials.password);
      onLogin(response); // Pass user data to parent
    } catch (error) {
      console.error('Login failed:', error);
      // Show error message to user
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="text"
        placeholder="Username"
        value={credentials.username}
        onChange={(e) => setCredentials({...credentials, username: e.target.value})}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={credentials.password}
        onChange={(e) => setCredentials({...credentials, password: e.target.value})}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};
```

### 2. **Protected Route Component**
```javascript
// ProtectedRoute.jsx
import React from 'react';

const ProtectedRoute = ({ children, user }) => {
  if (!user) {
    return <div>Please log in to access this page.</div>;
  }
  
  return children;
};

export default ProtectedRoute;
```

---

## Error Handling

### 1. **Global Error Handler**
```javascript
// errorHandler.js
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    switch (status) {
      case 401:
        return 'Authentication required. Please log in.';
      case 403:
        return 'Access denied. You do not have permission.';
      case 404:
        return 'Resource not found.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return data.message || 'An error occurred.';
    }
  } else if (error.request) {
    // Network error
    return 'Network error. Please check your connection.';
  } else {
    // Other error
    return 'An unexpected error occurred.';
  }
};
```

### 2. **Retry Logic**
```javascript
// retryLogic.js
export const retryRequest = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
    }
  }
};
```

---

## Testing & Deployment

### 1. **Local Testing**
```bash
# Start backend
cd backend
python main.py

# Test endpoints
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'

curl -X GET http://localhost:8080/videos
```

### 2. **Frontend Testing**
```javascript
// testApi.js
import apiClient from './apiClient';

const testApi = async () => {
  try {
    // Test login
    const loginResponse = await apiClient.login('testuser', 'testpass');
    console.log('Login successful:', loginResponse);

    // Test video retrieval
    const videosResponse = await apiClient.getVideos();
    console.log('Videos retrieved:', videosResponse);

    // Test chat
    const chatResponse = await apiClient.sendMessage(
      'What is this video about?', 
      'SC1007', 
      []
    );
    console.log('Chat response:', chatResponse);
  } catch (error) {
    console.error('API test failed:', error);
  }
};
```

### 3. **Production Deployment**
```javascript
// production config
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-backend-domain.com';
const API_ENDPOINTS = {
  UPLOAD: '/upload',
  CHAT: '/chat/',
  VIDEOS: '/videos',
  LOGIN: '/auth/login'
};
```

---

## Complete Integration Example

### **Main App Component**
```javascript
// App.jsx
import React, { useState } from 'react';
import LoginComponent from './LoginComponent';
import VideoUploadComponent from './VideoUploadComponent';
import ChatComponent from './ChatComponent';
import VideoManagementComponent from './VideoManagementComponent';
import ProtectedRoute from './ProtectedRoute';

const App = () => {
  const [user, setUser] = useState(null);
  const [currentCourse, setCurrentCourse] = useState('');
  const [selectedVideos, setSelectedVideos] = useState([]);

  return (
    <div className="app">
      {!user ? (
        <LoginComponent onLogin={setUser} />
      ) : (
        <div>
          <h1>Video Chatbot System</h1>
          <nav>
            <button onClick={() => setCurrentCourse('')}>Home</button>
            <button onClick={() => setCurrentCourse('upload')}>Upload Videos</button>
            <button onClick={() => setCurrentCourse('manage')}>Manage Videos</button>
            <button onClick={() => setCurrentCourse('chat')}>Chat</button>
          </nav>

          <main>
            {currentCourse === 'upload' && (
              <ProtectedRoute user={user}>
                <VideoUploadComponent />
              </ProtectedRoute>
            )}
            
            {currentCourse === 'manage' && (
              <ProtectedRoute user={user}>
                <VideoManagementComponent />
              </ProtectedRoute>
            )}
            
            {currentCourse === 'chat' && (
              <ProtectedRoute user={user}>
                <ChatComponent 
                  courseCode="SC1007" 
                  selectedVideos={selectedVideos}
                />
              </ProtectedRoute>
            )}
          </main>
        </div>
      )}
    </div>
  );
};

export default App;
```

This guide provides everything you need to integrate your backend with any frontend application, covering the complete workflow from video upload to chatbot responses.
