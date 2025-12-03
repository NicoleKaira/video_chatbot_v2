#  CCDS24-1273 Final Year Project

## LLM-based Learning Companion & Co-Pilot - A Video to Text Approach (Gen2)

### Set Up Guide

***
#### Backend

Backend requires the following Azure services:
- Azure AI Video Indexer 
- Azure OpenAI
- Azure Cosmos DB for MongoDB (vCore)

##### Environment Set Up

Provision Azure AI Video Indexer

Environment Variables:
- ```ACCOUNT_NAME=<Azure AI Video Indexer Name>```
  - Name in Azure AI Video Indexer
- ```RESOURCE_GROUP=<Resource group>```
  - Resource Group in Azure AI Video Indexer
- ```SUBSCRIPTION_ID=<Subscription ID>```
  - Subscription ID in Azure AI Video Indexer
- ```API_VERSION=2024-01-01```
- ```API_ENDPOINT=https://api.videoindexer.ai```
- ```AZURE_RESOURCE_MANAGER=https://management.azure.com```

Provision Azure OpenAI

Environment Variables:
- ```YOUR_DEPLOYMENT_NAME_4O=<gpt-4o Deployment Name>``` 
  - The name you inputted when creating a gpt-4o deployment (can view in Azure AI Foundry|Deployments)
- ```YOUR_DEPLOYMENT_NAME=<got-4o-mini Deployment Name>```
  - The name you inputted when creating a gpt-4o-mini deployment (can view in Azure AI Foundry|Deployments)
- ```AZURE_OPENAI_API_KEY=<KEY 1/KEY 2>```
  - Enter Azure OpenAI Resource
  - Go to Resource Management|Keys and Endpoint
  - Copy KEY 1
- ```AZURE_OPENAI_ENDPOINT=<Endpoint>```
  - Enter Azure OpenAI Resource
  - Go to Resource Management|Keys and Endpoint
  - Copy Endpoint
- ```OPENAI_API_VERSION=<API Version of Deployments>```
  - Enter Azure OpenAI Resource 
  - Go to Azure AI Foundry
  - Enter any Deployments and view api version from target URI (api-version=...)
- ```EMBEDDING_MODEL=<text-embedding-ada-002 Deployment Name>```
  - The name you inputted when creating a text-embedding-ada-002 deployment (can view in Azure AI Foundry|Deployments)

Provision Azure Cosmos DB for MongoDB (vCore)

Environment Variables:
- ```MONGODB_CONNECTION_STRING=<Connection String>```
  - Enter Azure Cosmos DB for MongoDB (vCore) Resource
  - Go to Settings|Connection strings
  - Copy the connection string
  - Replace 'username' and '<password>' with your credentials you inputted when creating the resource
- ```DB_NAME=<Database Name>```
  -  Can be any name

 Access  useing  compass
  - Download compass here: https://www.mongodb.com/try/download/compass
  - Add a new connection 
  - connect using the <Connection String> that was used in azure. 
  - create a database called fypdatabase
  - Create the following collections in the database: course, prompt_content_clean, prompt_content_index,   prompt_content_raw, transcript_full, video, video_indexer_raw



##### Start Up

Go to the backend Folder:
```cd backend```

Create a virtual environment:
```python -m venv .venv```

Activate the virtual environment:
```.venv\Scripts\activate```

Download dependencies:
```pip install -r requirements.txt```

Run the program:
```python main.py```

*Useful links*:
- [MongoDB Atlas GUI](https://www.mongodb.com/products/platform/atlas-database)
- [Azure Video Indexer API](https://api-portal.videoindexer.ai/)


***
#### Frontend

##### Start Up

Go to the frontend Folder:
```cd frontend```

Download next (if you have not):
```npm i next```
```npm install``` 

Run the program:
```npm run dev```

***
### Make sure you have Azure CLI installed to be able to use the AZURE services

Download Azure SDK here: https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-interactively?view=azure-cli-latest  

Go to the backend Folder:
```cd backend```

Login to Azure:
```az login```

***
### Download a video using the video_Download.py

