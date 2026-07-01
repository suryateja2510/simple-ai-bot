# Azure Foundry and Azure Setup - Step by Step

This guide is written for beginners. It explains the minimum Azure steps you need to run this app locally with Azure services.

## What you need

The app can use Azure for:

- Azure OpenAI / Foundry chat model
- Azure AI Search for retrieval (RAG)
- Cosmos DB for session and memory storage
- Optional Key Vault for secrets

You do not need a login page or app authentication to run this POC.

## Minimal Azure POC setup

For the first demo, only these environment variables are required:

```env
USE_AZURE_SERVICES=true
AZURE_AUTH_MODE=api_key
AZURE_OPENAI_ENDPOINT=https://<your-openai-or-foundry-endpoint>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=<your-model-deployment-name>
AZURE_OPENAI_KEY=<your-openai-key>
AZURE_SEARCH_ENDPOINT=https://<your-search-service>.search.windows.net
AZURE_SEARCH_INDEX=<your-index-name>
AZURE_SEARCH_KEY=<your-search-key>
COSMOS_ENDPOINT=https://<your-cosmos-account>.documents.azure.com:443/
COSMOS_KEY=<your-cosmos-key>
```

The rest are optional and only needed later for Key Vault or managed identity.

## Step 1: Create Azure resources

Use the Azure Portal to create these resources.

### 1.1 Create an Azure OpenAI / Foundry model deployment

1. Go to the Azure Portal.
2. Search for **Azure OpenAI** or **Azure AI Foundry**.
3. Create a new OpenAI resource or Foundry AI resource.
4. Inside that resource, deploy a chat model such as `gpt-4o-mini` or another supported model.
5. Note these values:
   - `AZURE_OPENAI_ENDPOINT` (resource endpoint)
   - `AZURE_OPENAI_DEPLOYMENT` (model deployment name)

### 1.2 Create an Azure AI Search service

1. Search for **Azure AI Search** in the Azure Portal.
2. Create a new search service in the same region if possible.
3. Create an index with at least one text field, for example:
   - `content` as searchable text
   - `source` or `id` as a metadata field
4. Note these values:
   - `AZURE_SEARCH_ENDPOINT`
   - `AZURE_SEARCH_INDEX`

### 1.3 Create a Cosmos DB account

1. Search for **Azure Cosmos DB**.
2. Create a new account using the Core (SQL) API.
3. Record the account endpoint and key.

### 1.4 Optional: Create a Key Vault

1. Search for **Key Vault**.
2. Create a new Key Vault.
3. If you want to use Key Vault, create secrets with these names:
   - `azure-openai-key`
   - `azure-search-key`
   - `cosmos-key`
   - `microsoft-entra-client-secret` (optional)

## Step 2: Fill in the backend `.env`

In the repo, open `apps/api/.env.example` and copy it to `apps/api/.env`.

```powershell
cd apps/api
Copy-Item .env.example .env
```

Then set these values:

```env
USE_AZURE_SERVICES=true
AZURE_AUTH_MODE=api_key
AZURE_OPENAI_ENDPOINT=https://<your-openai-or-foundry-endpoint>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=<your-model-deployment-name>
AZURE_OPENAI_KEY=<your-openai-key>
AZURE_SEARCH_ENDPOINT=https://<your-search-service>.search.windows.net
AZURE_SEARCH_INDEX=<your-index-name>
AZURE_SEARCH_KEY=<your-search-key>
COSMOS_ENDPOINT=https://<your-cosmos-account>.documents.azure.com:443/
COSMOS_KEY=<your-cosmos-key>
```

If you use Key Vault, also add:

```env
USE_KEY_VAULT=true
KEY_VAULT_URL=https://<your-vault>.vault.azure.net/
```

You can keep the rest of the settings as the defaults.

## Step 3: Run the backend

In `apps/api`:

```powershell
cd apps/api
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend should run at `http://localhost:8000`.

## Step 4: Run the frontend

In a new terminal:

```powershell
cd apps/web
npm install
npm run dev
```

Open the app at `http://localhost:5173`.

## Step 5: Test the app

### 5.1 Open Swagger docs

Open `http://localhost:8000/docs`.

### 5.2 Test the API

Use the docs or a tool like Postman to call:

- `POST /sessions`
- `GET /sessions`
- `GET /sessions/{session_id}`
- `POST /chat/stream`

If these calls work, the Azure connection is configured.

## What happens in the app

- `POST /chat/stream` sends your question to Azure OpenAI / Foundry.
- `Azure AI Search` retrieves related text for RAG.
- `Cosmos DB` stores sessions and user memory.
- `Key Vault` is only used if `USE_KEY_VAULT=true`.

## Notes for beginners

- Start with `api_key` mode first.
- Do not worry about app login.
- If Azure does not work, first check the `.env` values.
- The app is designed as a POC, not a full production product.

## Troubleshooting

- If the frontend shows a CORS error, make sure the backend is running on `http://localhost:8000`.
- If the backend fails to start, check `apps/api/.env` for missing values.
- If the chat API returns errors, check `http://localhost:8000/docs` and the backend logs.
