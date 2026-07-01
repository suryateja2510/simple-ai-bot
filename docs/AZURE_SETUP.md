# Azure Setup

This guide explains how to connect the bot to Azure AI Foundry, Azure AI Search, Cosmos DB, Key Vault, and managed identity.

## Configuration Modes

The backend supports two Azure authentication modes.

### API Key Mode

Best for local development and first tests.

```env
USE_AZURE_SERVICES=true
AZURE_AUTH_MODE=api_key
```

You can either put keys directly in `.env`:

```env
AZURE_OPENAI_KEY=
AZURE_SEARCH_KEY=
COSMOS_KEY=
```

Or store those keys in Key Vault and set:

```env
USE_KEY_VAULT=true
KEY_VAULT_URL=https://<your-vault>.vault.azure.net/
```

### Managed Identity Mode

Best for Azure App Service, Container Apps, AKS, or any deployed Azure host with managed identity enabled.

```env
USE_AZURE_SERVICES=true
AZURE_AUTH_MODE=managed_identity
USE_KEY_VAULT=true
KEY_VAULT_URL=https://<your-vault>.vault.azure.net/
```

For a user-assigned managed identity, also set:

```env
MANAGED_IDENTITY_CLIENT_ID=<identity-client-id>
```

Leave `MANAGED_IDENTITY_CLIENT_ID` empty when using a system-assigned managed identity.

## Required Settings

```env
AZURE_OPENAI_ENDPOINT=https://<openai-or-foundry-resource>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=<chat-model-deployment-name>
AZURE_SEARCH_ENDPOINT=https://<search-service>.search.windows.net
AZURE_SEARCH_INDEX=<index-name>
COSMOS_ENDPOINT=https://<cosmos-account>.documents.azure.com:443/
```

In `api_key` mode, provide these directly or through Key Vault:

```env
AZURE_OPENAI_KEY=
AZURE_SEARCH_KEY=
COSMOS_KEY=
```

## Key Vault Secret Names

The app reads missing secrets from Key Vault only when `USE_KEY_VAULT=true`.

Default secret names:

```env
AZURE_OPENAI_KEY_SECRET_NAME=azure-openai-key
AZURE_SEARCH_KEY_SECRET_NAME=azure-search-key
COSMOS_KEY_SECRET_NAME=cosmos-key
MICROSOFT_ENTRA_CLIENT_SECRET_SECRET_NAME=microsoft-entra-client-secret
```

You can change these names in `.env` if your vault uses a different naming convention.

## Managed Identity RBAC

When `AZURE_AUTH_MODE=managed_identity`, assign the app identity permissions to each Azure resource.

Recommended roles:

| Resource | Role |
| --- | --- |
| Azure OpenAI / Foundry AI Services resource | `Cognitive Services OpenAI User` |
| Azure AI Search | `Search Index Data Reader` |
| Cosmos DB | `Cosmos DB Built-in Data Contributor` |
| Key Vault | `Key Vault Secrets User` |

The app still needs endpoint and deployment/index names in environment variables. Managed identity replaces secret keys; it does not discover resource names automatically.

## Azure AI Search Index

The search adapter expects a retrievable text field and a source/title field.

Defaults:

```env
AZURE_SEARCH_CONTENT_FIELD=content
AZURE_SEARCH_SOURCE_FIELD=source
AZURE_SEARCH_TOP_K=5
```

If your index uses different field names, update those values.

## Cosmos DB Memory

Defaults:

```env
COSMOS_DATABASE_NAME=ragbot
COSMOS_SESSIONS_CONTAINER=sessions
COSMOS_EPISODIC_CONTAINER=episodic-memory
```

The app creates the database and containers if they do not already exist. Both containers use `/user_id` as the partition key.

## Foundry Note

This app uses your Azure AI Foundry model deployment through the Azure OpenAI-compatible chat completions API. It is not a Foundry hosted-agent app yet. That is intentional for a simple RAG bot where FastAPI owns orchestration, retrieval, memory, and prompt assembly.

If you later want Foundry hosted agents, add an adapter behind `ChatCompletionService` that invokes the hosted agent instead of calling chat completions directly.

## Minimal Local Azure Test

1. Copy `apps/api/.env.example` to `apps/api/.env`.
2. Set `USE_AZURE_SERVICES=true`.
3. Set `AZURE_AUTH_MODE=api_key`.
4. Fill in Azure OpenAI, Azure AI Search, and Cosmos DB values.
5. Start the backend.
6. Open `http://localhost:8000/docs`.
7. Test `POST /sessions`.
8. Test `PUT /memory/episodic`.
9. Test `POST /chat/stream`.
