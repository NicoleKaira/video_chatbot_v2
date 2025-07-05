# CCDS24-0653 Final Year Project

## LLM-based Learning Companion & Co-Pilot - A Video to Text Approach 

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

Run the program:
```npm run dev```

***
#### Deployment

Make sure you have Azure CLI installed

Go to the backend Folder:
```cd backend```

Login to Azure:
```az login```

Deploy your code:
```az webapp up --runtime PYTHON:3.12 --sku B1 --logs```
- use ```--sku F1``` to use free version of Azure Web Service
- use ```PYTHON:<version>``` to change version

Configure Start Up Script:
- Go to Web App resource|Settings|Configuration
- ```
  pip install -r requirements.txt 
  gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app
  ```

Add Environment Variables:
- Go to Web App resource|Settings|Environment variables
- Add environment variables in .env

*Useful links*:
- [Quickstart: Deploy a Python (Django, Flask, or FastAPI) web app to Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python?tabs=flask%2Cwindows%2Cazure-portal%2Cazure-cli-deploy%2Cdeploy-instructions-azportal%2Cterminal-bash%2Cdeploy-instructions-zip-azcli)
