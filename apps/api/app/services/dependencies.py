from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config.key_vault import load_key_vault_secrets
from app.config.settings import AppSettings
from app.services.interfaces import (
    AuthService,
    ChatCompletionService,
    EpisodicMemoryService,
    PromptBuilder,
    SearchService,
    SessionMemoryService,
)
from app.services.mock_implementations import (
    InMemoryEpisodicMemoryService,
    InMemorySessionMemoryService,
    LocalPdfSearchService,
    MockAuthService,
    MockChatCompletionService,
)
from app.services.prompt_builder import SimplePromptBuilder


@dataclass
class ServiceContainer:
    auth: AuthService
    session_memory: SessionMemoryService
    episodic_memory: EpisodicMemoryService
    search: SearchService
    chat_completion: ChatCompletionService
    prompt_builder: PromptBuilder


def build_service_container(settings: AppSettings) -> ServiceContainer:
    settings = load_key_vault_secrets(settings)
    data_folder = Path(__file__).resolve().parents[1] / "data"

    if settings.use_azure_services:
        from app.services.azure_implementations import (
            AzureAISearchService,
            AzureOpenAIChatCompletionService,
            CosmosDbEpisodicMemoryService,
            CosmosDbSessionMemoryService,
            CosmosMemoryStore,
        )

        chat_completion = AzureOpenAIChatCompletionService(settings)
        search = AzureAISearchService(settings)
        cosmos_store = CosmosMemoryStore(settings)
        session_memory = CosmosDbSessionMemoryService(cosmos_store)
        episodic_memory = CosmosDbEpisodicMemoryService(cosmos_store)
    else:
        chat_completion = MockChatCompletionService()
        search = LocalPdfSearchService(data_folder)
        session_memory = InMemorySessionMemoryService()
        episodic_memory = InMemoryEpisodicMemoryService()

    if settings.microsoft_entra_client_id and settings.microsoft_entra_client_secret:
        # TODO: Replace with an Entra-based AuthService.
        auth = MockAuthService()
    else:
        auth = MockAuthService()

    prompt_builder = SimplePromptBuilder()
    return ServiceContainer(
        auth=auth,
        session_memory=session_memory,
        episodic_memory=episodic_memory,
        search=search,
        chat_completion=chat_completion,
        prompt_builder=prompt_builder,
    )
