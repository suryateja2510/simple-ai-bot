# Azure Setup for Simple AI Bot

This guide is written for beginners. It shows the simplest way to connect the app to Azure so you can test it locally with Azure endpoints.

## What this app needs from Azure

The app uses Azure for these services:

- Azure OpenAI / Foundry model deployment for chat responses
- Azure AI Search for retrieval (RAG)
- Cosmos DB for session and episodic memory storage
- Optional Key Vault for secrets

You do not need app login or user authentication for this POC.

## Quick start: local Azure test

1. Open a terminal.
2. Go to `apps/api`.
3. Copy the env example:

```powershell
cd apps/api
Copy-Item .env.example .env
```

4. Open `apps/api/.env` and set:

```env
USE_AZURE_SERVICES=true
AZURE_AUTH_MODE=api_key
```

5. Fill in your Azure values:

```env
AZURE_OPENAI_ENDPOINT=https://<your-openai-or-foundry-endpoint>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=<your-model-deployment-name>
AZURE_OPENAI_KEY=<your-openai-api-key>
AZURE_SEARCH_ENDPOINT=https://<your-search-service>.search.windows.net
AZURE_SEARCH_INDEX=<your-index-name>
AZURE_SEARCH_KEY=<your-search-api-key>
COSMOS_ENDPOINT=https://<your-cosmos-account>.documents.azure.com:443/
COSMOS_KEY=<your-cosmos-key>
```

6. Save the file.
7. Start the backend and frontend.

## Run the app locally

### Backend

```powershell
cd apps/api
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd apps/web
npm install
npm run dev
```

Open the frontend at `http://localhost:5173`.

## How the app uses Azure

- `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_KEY` -> chat model
- `AZURE_SEARCH_ENDPOINT` + `AZURE_SEARCH_KEY` -> search retrieval
- `COSMOS_ENDPOINT` + `COSMOS_KEY` -> session and memory storage

The app can run locally with this setup. It does not require user authentication.

## Optional: use Azure Key Vault

If you prefer not to store keys in `.env`, use Key Vault.

In `apps/api/.env`:

```env
USE_KEY_VAULT=true
KEY_VAULT_URL=https://<your-vault>.vault.azure.net/
```

Then create secrets in Key Vault with these names:

```env
AZURE_OPENAI_KEY_SECRET_NAME=azure-openai-key
AZURE_SEARCH_KEY_SECRET_NAME=azure-search-key
COSMOS_KEY_SECRET_NAME=cosmos-key
MICROSOFT_ENTRA_CLIENT_SECRET_SECRET_NAME=microsoft-entra-client-secret
```

If you use Key Vault, the app loads the missing keys automatically.

## Optional: managed identity (for Azure deployment)

For local testing, use `api_key` mode.

Managed identity is only needed when you deploy the app to Azure.

If you use it, set:

```env
USE_AZURE_SERVICES=true
AZURE_AUTH_MODE=managed_identity
USE_KEY_VAULT=true
KEY_VAULT_URL=https://<your-vault>.vault.azure.net/
```

For a user-assigned identity:

```env
MANAGED_IDENTITY_CLIENT_ID=<identity-client-id>
```

## Verify Azure setup

Use the backend OpenAPI docs:

- `http://localhost:8000/docs`

Try these API calls:

- `POST /sessions` → creates a chat session
- `GET /sessions` → lists sessions
- `GET /sessions/{session_id}` → gets session messages
- `POST /chat/stream` → streams a chat response

If these work, your Azure connection is configured correctly.

## Notes for beginners

- This app works as a simple chatbot POC.
- You can start with local mock mode first by leaving `USE_AZURE_SERVICES=false`.
- Then switch to Azure mode by setting `USE_AZURE_SERVICES=true`.
- You do not need a login or authentication flow for the app.
- Focus on getting the Azure endpoint keys correct first.
