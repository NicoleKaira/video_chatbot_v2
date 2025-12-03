# CCDS24-1273 Final Year Project

## LLM-based Learning Companion & Co-Pilot - A Video to Text Approach (Gen2)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Setup Guide](#setup-guide)
   - [Backend Setup](#backend-setup)
   - [Frontend Setup](#frontend-setup)
4. [Azure Services Configuration](#azure-services-configuration)
5. [Database Setup](#database-setup)
6. [Video Download Utility](#video-download-utility)
7. [Useful Resources](#useful-resources)

---

## Project Overview

This project implements an LLM-based learning companion and co-pilot system that processes video content and converts it to text, enabling intelligent interactions and learning assistance through natural language processing.

---

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python** (version 3.x recommended)
- **Node.js** (version 18.x or higher recommended)
- **npm** (comes with Node.js)
- **Azure CLI** (required for Azure service authentication)
- **FFmpeg** (required for video processing)
  - Windows: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

---

## Setup Guide

### Backend Setup

#### Step 1: Navigate to Backend Directory

```bash
cd backend
```

#### Step 2: Create Virtual Environment

```bash
python -m venv .venv
```

#### Step 3: Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

#### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 5: Run the Application

```bash
python main.py
```

---

### Frontend Setup

#### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

#### Step 2: Install Dependencies

```bash
npm install
```

**Note:** If Next.js is not already installed, it will be installed as part of the dependencies.

#### Step 3: Run the Development Server

```bash
npm run dev
```

---

## Azure Services Configuration

The backend requires the following Azure services to be provisioned and configured:

### Azure AI Video Indexer

#### Environment Variables

Configure the following environment variables in your `.env` file:

- `ACCOUNT_NAME=<Azure AI Video Indexer Name>`
  - The account name specified in Azure AI Video Indexer
- `RESOURCE_GROUP=<Resource Group>`
  - The resource group name in Azure AI Video Indexer
- `SUBSCRIPTION_ID=<Subscription ID>`
  - The subscription ID in Azure AI Video Indexer
- `API_VERSION=2024-01-01`
- `API_ENDPOINT=https://api.videoindexer.ai`
- `AZURE_RESOURCE_MANAGER=https://management.azure.com`

---

### Azure OpenAI

#### Environment Variables

Configure the following environment variables in your `.env` file:

- `YOUR_DEPLOYMENT_NAME_4O=<gpt-4o Deployment Name>`
  - The deployment name you specified when creating a gpt-4o deployment
  - Can be viewed in Azure AI Foundry → Deployments
- `YOUR_DEPLOYMENT_NAME=<gpt-4o-mini Deployment Name>`
  - The deployment name you specified when creating a gpt-4o-mini deployment
  - Can be viewed in Azure AI Foundry → Deployments
- `AZURE_OPENAI_API_KEY=<KEY 1/KEY 2>`
  - Navigate to Azure OpenAI Resource
  - Go to Resource Management → Keys and Endpoint
  - Copy KEY 1
- `AZURE_OPENAI_ENDPOINT=<Endpoint>`
  - Navigate to Azure OpenAI Resource
  - Go to Resource Management → Keys and Endpoint
  - Copy the Endpoint
- `OPENAI_API_VERSION=<API Version of Deployments>`
  - Navigate to Azure OpenAI Resource
  - Go to Azure AI Foundry
  - Enter any Deployment and view the API version from the target URI (api-version=...)
- `EMBEDDING_MODEL=<text-embedding-ada-002 Deployment Name>`
  - The deployment name you specified when creating a text-embedding-ada-002 deployment
  - Can be viewed in Azure AI Foundry → Deployments

---

### Azure Cosmos DB for MongoDB (vCore)

#### Environment Variables

Configure the following environment variables in your `.env` file:

- `MONGODB_CONNECTION_STRING=<Connection String>`
  - Navigate to Azure Cosmos DB for MongoDB (vCore) Resource
  - Go to Settings → Connection strings
  - Copy the connection string
  - Replace `username` and `<password>` with your credentials specified when creating the resource
- `DB_NAME=<Database Name>`
  - Can be any name of your choice

---

## Database Setup

### Access Using MongoDB Compass

1. **Download MongoDB Compass**
   - Download from: [https://www.mongodb.com/try/download/compass](https://www.mongodb.com/try/download/compass)

2. **Create a New Connection**
   - Open MongoDB Compass
   - Add a new connection using the `<Connection String>` that was used in Azure

3. **Create Database**
   - Create a database named `fypdatabase`

4. **Create Collections**
   - Create the following collections in the `fypdatabase` database:
     - `course`
     - `prompt_content_clean`
     - `prompt_content_index`
     - `prompt_content_raw`
     - `transcript_full`
     - `video`
     - `video_indexer_raw`

---

## Azure CLI Authentication

To use Azure services, you must authenticate using Azure CLI.

### Step 1: Install Azure CLI

Download and install Azure CLI from:
[https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-interactively?view=azure-cli-latest](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-interactively?view=azure-cli-latest)

### Step 2: Login to Azure

```bash
az login
```

Follow the authentication prompts to complete the login process.

---

## Video Download Utility

The project includes a video download utility script (`Video_download.py`) located in the main project directory. This script allows you to download YouTube videos for processing.

### Description

The `Video_download.py` script uses `yt-dlp` (a fork of youtube-dl) to download YouTube videos in the highest available quality. The script automatically handles:
- Best video and audio stream selection
- Automatic merging with FFmpeg
- Resume capability for interrupted downloads
- Better error handling and retry logic

### Requirements

- `yt-dlp`: Install using `pip install yt-dlp`
- `FFmpeg`: Must be installed and added to system PATH (see [Prerequisites](#prerequisites))

### Usage

1. Open `Video_download.py` in the main project directory
2. Replace the `url` variable with your YouTube video URL
3. Run the script:
   ```bash
   python Video_download.py
   ```
4. The video will be saved in the current directory as `[video_title].mp4`

### Configuration

The script is configured to:
- Download the best available video and audio quality
- Merge streams using FFmpeg to MP4 format
- Retry failed downloads up to 10 times
- Resume interrupted downloads automatically

---

## Useful Resources

- [MongoDB Atlas GUI](https://www.mongodb.com/products/platform/atlas-database)
- [Azure Video Indexer API](https://api-portal.videoindexer.ai/)
- [Azure CLI Documentation](https://learn.microsoft.com/en-us/cli/azure/)

---

## Notes

- Ensure all environment variables are properly configured in your `.env` file before running the application
- The backend and frontend must be running simultaneously for the full application to function
- Make sure Azure CLI is authenticated before attempting to use Azure services

---

## Missing Information to Consider Adding

The following sections may be beneficial for examiners but are currently not included:

1. **Project Architecture**: Overview of system architecture and component interactions
2. **API Documentation**: Endpoint descriptions and request/response formats
3. **Usage Examples**: Step-by-step guide on how to use the application after setup
4. **Troubleshooting**: Common issues and solutions
5. **Testing**: How to run tests (if applicable)
6. **Contributing Guidelines**: If this is a collaborative project
7. **License Information**: Project license details
8. **Author/Credits**: Project author and acknowledgments
9. **Version Information**: Current version and changelog
10. **Deployment Instructions**: Production deployment guidelines (if applicable)
