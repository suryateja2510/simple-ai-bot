# Simple RAG Bot

A simple full-stack RAG chatbot with streaming responses, session memory, episodic memory, and Azure AI Foundry-ready service adapters.

The project runs locally with mock services by default. When you are ready for Azure, the same API can switch to Azure OpenAI/Foundry model deployments, Azure AI Search, Cosmos DB, Key Vault, and managed identity through environment configuration.

## What This App Does

- Provides a React chat UI with conversation sessions.
- Streams assistant responses token by token from the backend.
- Keeps per-session chat history.
- Keeps user-level episodic memory that can be read or updated through the API.
- Retrieves RAG context through a `SearchService`.
- Builds prompts from system instructions, episodic memory, recent session history, retrieved context, and the latest user question.
- Uses dependency injection so local mocks and Azure services share the same route contracts.

## Project Structure

```text
simple-ai-bot/
  apps/
    api/                 FastAPI backend
    web/                 React + TypeScript + Vite frontend
  packages/
    shared/              Shared TypeScript DTOs
  docs/
    AZURE_SETUP.md       Azure configuration and identity guide
  infra/                 Future infrastructure files
```

## Backend Services

The backend has six service interfaces:

- `AuthService`: identifies the current user.
- `SessionMemoryService`: stores chat sessions and messages.
- `EpisodicMemoryService`: stores long-term user memory.
- `SearchService`: retrieves grounding chunks for RAG.
- `ChatCompletionService`: streams model output.
- `PromptBuilder`: assembles the model prompt.

Local mode uses mocks and in-memory stores. Azure mode uses:

- Azure OpenAI-compatible chat completions for Foundry model deployments.
- Azure AI Search for retrieval.
- Cosmos DB for session and episodic memory.
- Azure Key Vault for secrets, when enabled.
- Managed identity or API keys for Azure authentication.

## Local Development

### Backend

```powershell
cd apps/api
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`. Swagger is available at `http://localhost:8000/docs`.

### Frontend

```powershell
cd apps/web
npm install
npm run dev
```

The web app is available at `http://localhost:5173`.

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Redirect to Swagger docs |
| `POST` | `/sessions` | Create a chat session |
| `GET` | `/sessions` | List sessions for the current user |
| `GET` | `/sessions/{session_id}` | Get session messages |
| `GET` | `/memory/episodic` | Get user episodic memory |
| `PUT` | `/memory/episodic` | Update user episodic memory |
| `POST` | `/chat/stream` | Stream a RAG chat response |

## Azure Mode

Copy the backend env template:

```powershell
cd apps/api
Copy-Item .env.example .env
```

Then set:

```env
USE_AZURE_SERVICES=true
AZURE_AUTH_MODE=api_key
```

For local Azure testing, `api_key` mode is usually simplest. Put keys directly in `.env`, or set `USE_KEY_VAULT=true` and let the app read missing keys from Key Vault.

For deployed Azure hosting, prefer:

```env
USE_AZURE_SERVICES=true
AZURE_AUTH_MODE=managed_identity
USE_KEY_VAULT=true
KEY_VAULT_URL=https://<your-vault>.vault.azure.net/
```

Use `MANAGED_IDENTITY_CLIENT_ID` only when using a user-assigned managed identity. Leave it empty for a system-assigned managed identity.

See [docs/AZURE_SETUP.md](docs/AZURE_SETUP.md) for the detailed Azure resource, Key Vault, and managed identity setup.

## Required Azure Resources

To run real RAG on Azure, create:

- A deployed chat model in Azure AI Foundry or Azure OpenAI.
- An Azure AI Search index containing your documents.
- A Cosmos DB account for sessions and episodic memory.
- Optionally, a Key Vault for API keys/secrets.
- A managed identity with the required RBAC roles if using `AZURE_AUTH_MODE=managed_identity`.

## Request protection

- Frontend prevents duplicate sends while a request is in progress.
- Backend protects `/chat/stream` with a per-client rate limiter and a per-session in-flight request guard.

## Verification

Frontend build:

```powershell
cd apps/web
npm.cmd run build
```

Backend import check:

```powershell
cd apps/api
.\.venv\Scripts\python.exe -c "from app.main import app; print(app.title)"
```

Expected backend title:

```text
Simple RAG Bot
```
