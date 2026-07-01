from __future__ import annotations

from datetime import datetime
from typing import Any, AsyncIterator, Dict, List
from uuid import uuid4

from app.config.settings import AppSettings
from app.models.domain import ChatMessage, ChatSession, EpisodicMemoryItem, SearchResultChunk
from app.services.interfaces import ChatCompletionService, EpisodicMemoryService, SearchService, SessionMemoryService


def _require_package(package_name: str, install_hint: str) -> None:
    raise RuntimeError(
        f"{package_name} is required for Azure mode. Install backend dependencies with "
        f"`pip install -r requirements.txt`. Missing package: {install_hint}"
    )


def _uses_managed_identity(settings: AppSettings) -> bool:
    return settings.azure_auth_mode.lower() == "managed_identity"


def _build_default_credential(settings: AppSettings):
    try:
        from azure.identity import DefaultAzureCredential
    except ImportError:
        _require_package("azure-identity", "azure-identity")

    credential_options = {}
    if settings.managed_identity_client_id:
        credential_options["managed_identity_client_id"] = settings.managed_identity_client_id
    return DefaultAzureCredential(**credential_options)


def _parse_datetime(value: str | datetime | None) -> datetime:
    if isinstance(value, datetime):
        return value
    if not value:
        return datetime.utcnow()
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _message_to_dict(message: ChatMessage) -> Dict[str, Any]:
    return {
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at.isoformat(),
    }


def _message_from_dict(data: Dict[str, Any]) -> ChatMessage:
    return ChatMessage(
        role=str(data.get("role", "")),
        content=str(data.get("content", "")),
        created_at=_parse_datetime(data.get("created_at")),
    )


class AzureOpenAIChatCompletionService(ChatCompletionService):
    def __init__(self, settings: AppSettings) -> None:
        if not settings.azure_openai_endpoint or not settings.azure_openai_deployment:
            raise ValueError("Azure OpenAI endpoint and deployment are required for Azure chat completion.")

        try:
            from openai import AsyncAzureOpenAI
        except ImportError:
            _require_package("openai", "openai")

        self.deployment = settings.azure_openai_deployment
        client_options = {
            "azure_endpoint": settings.azure_openai_endpoint,
            "api_version": settings.azure_openai_api_version,
        }
        if _uses_managed_identity(settings):
            try:
                from azure.identity import get_bearer_token_provider
            except ImportError:
                _require_package("azure-identity", "azure-identity")
            credential = _build_default_credential(settings)
            client_options["azure_ad_token_provider"] = get_bearer_token_provider(
                credential,
                "https://cognitiveservices.azure.com/.default",
            )
        else:
            if not settings.azure_openai_key:
                raise ValueError("AZURE_OPENAI_KEY is required when AZURE_AUTH_MODE=api_key.")
            client_options["api_key"] = settings.azure_openai_key

        self.client = AsyncAzureOpenAI(**client_options)

    async def stream_complete(self, prompt: str) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.deployment,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            stream=True,
        )
        async for chunk in stream:
            if not chunk.choices:
                continue
            token = chunk.choices[0].delta.content
            if token:
                yield token


class AzureAISearchService(SearchService):
    def __init__(self, settings: AppSettings) -> None:
        if not settings.azure_search_endpoint or not settings.azure_search_index:
            raise ValueError("Azure AI Search endpoint and index are required for Azure search.")

        try:
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents.aio import SearchClient
        except ImportError:
            _require_package("azure-search-documents", "azure-search-documents")

        if _uses_managed_identity(settings):
            credential = _build_default_credential(settings)
        else:
            if not settings.azure_search_key:
                raise ValueError("AZURE_SEARCH_KEY is required when AZURE_AUTH_MODE=api_key.")
            credential = AzureKeyCredential(settings.azure_search_key)

        self.content_field = settings.azure_search_content_field
        self.source_field = settings.azure_search_source_field
        self.top_k = settings.azure_search_top_k
        self.client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index,
            credential=credential,
        )

    async def retrieve(self, query: str) -> List[SearchResultChunk]:
        results: List[SearchResultChunk] = []
        search_results = await self.client.search(search_text=query, top=self.top_k)
        async for result in search_results:
            content = str(result.get(self.content_field, ""))
            if not content:
                continue
            source = str(result.get(self.source_field, result.get("id", "azure-ai-search")))
            score = float(result.get("@search.score", 0.0))
            results.append(SearchResultChunk(source=source, content=content, score=score))
        return results


class CosmosMemoryStore:
    def __init__(self, settings: AppSettings) -> None:
        if not settings.cosmos_endpoint:
            raise ValueError("Cosmos endpoint is required for Azure memory.")

        try:
            from azure.cosmos import PartitionKey
            from azure.cosmos.aio import CosmosClient
        except ImportError:
            _require_package("azure-cosmos", "azure-cosmos")

        if _uses_managed_identity(settings):
            credential = _build_default_credential(settings)
        else:
            if not settings.cosmos_key:
                raise ValueError("COSMOS_KEY is required when AZURE_AUTH_MODE=api_key.")
            credential = settings.cosmos_key

        self.PartitionKey = PartitionKey
        self.client = CosmosClient(settings.cosmos_endpoint, credential=credential)
        self.database_name = settings.cosmos_database_name
        self.sessions_container_name = settings.cosmos_sessions_container
        self.episodic_container_name = settings.cosmos_episodic_container
        self._database = None
        self._sessions_container = None
        self._episodic_container = None

    async def sessions_container(self):
        if self._sessions_container is None:
            database = await self._get_database()
            self._sessions_container = await database.create_container_if_not_exists(
                id=self.sessions_container_name,
                partition_key=self.PartitionKey(path="/user_id"),
            )
        return self._sessions_container

    async def episodic_container(self):
        if self._episodic_container is None:
            database = await self._get_database()
            self._episodic_container = await database.create_container_if_not_exists(
                id=self.episodic_container_name,
                partition_key=self.PartitionKey(path="/user_id"),
            )
        return self._episodic_container

    async def _get_database(self):
        if self._database is None:
            self._database = await self.client.create_database_if_not_exists(id=self.database_name)
        return self._database


class CosmosDbSessionMemoryService(SessionMemoryService):
    def __init__(self, store: CosmosMemoryStore) -> None:
        self.store = store

    async def create_session(self, user_id: str, title: str) -> ChatSession:
        session = ChatSession(id=str(uuid4()), user_id=user_id, title=title)
        container = await self.store.sessions_container()
        await container.create_item(
            {
                "id": session.id,
                "user_id": user_id,
                "title": title,
                "messages": [],
                "created_at": session.created_at.isoformat(),
            }
        )
        return session

    async def list_sessions(self, user_id: str) -> List[ChatSession]:
        container = await self.store.sessions_container()
        query = "SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.created_at DESC"
        params = [{"name": "@user_id", "value": user_id}]
        sessions: List[ChatSession] = []
        async for item in container.query_items(query=query, parameters=params, partition_key=user_id):
            sessions.append(self._session_from_item(item))
        return sessions

    async def get_session(self, session_id: str) -> ChatSession | None:
        container = await self.store.sessions_container()
        query = "SELECT * FROM c WHERE c.id = @session_id"
        params = [{"name": "@session_id", "value": session_id}]
        async for item in container.query_items(query=query, parameters=params, enable_cross_partition_query=True):
            return self._session_from_item(item)
        return None

    async def add_message(self, session_id: str, message: ChatMessage) -> None:
        session = await self.get_session(session_id)
        if session is None:
            return
        session.messages.append(message)
        container = await self.store.sessions_container()
        await container.upsert_item(
            {
                "id": session.id,
                "user_id": session.user_id,
                "title": session.title,
                "messages": [_message_to_dict(item) for item in session.messages],
                "created_at": session.created_at.isoformat(),
            }
        )

    def _session_from_item(self, item: Dict[str, Any]) -> ChatSession:
        return ChatSession(
            id=str(item["id"]),
            user_id=str(item["user_id"]),
            title=str(item.get("title", "New chat session")),
            messages=[_message_from_dict(message) for message in item.get("messages", [])],
            created_at=_parse_datetime(item.get("created_at")),
        )


class CosmosDbEpisodicMemoryService(EpisodicMemoryService):
    def __init__(self, store: CosmosMemoryStore) -> None:
        self.store = store

    async def get_memory(self, user_id: str) -> EpisodicMemoryItem | None:
        container = await self.store.episodic_container()
        try:
            item = await container.read_item(item=user_id, partition_key=user_id)
        except Exception:
            return None
        return EpisodicMemoryItem(
            user_id=user_id,
            memory=str(item.get("memory", "")),
            created_at=_parse_datetime(item.get("created_at")),
        )

    async def upsert_memory(self, user_id: str, memory: str) -> EpisodicMemoryItem:
        item = EpisodicMemoryItem(user_id=user_id, memory=memory)
        container = await self.store.episodic_container()
        await container.upsert_item(
            {
                "id": user_id,
                "user_id": user_id,
                "memory": memory,
                "created_at": item.created_at.isoformat(),
            }
        )
        return item
