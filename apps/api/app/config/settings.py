from __future__ import annotations

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    app_environment: str = "local"
    use_azure_services: bool = False
    azure_auth_mode: str = "api_key"
    managed_identity_client_id: str = ""
    azure_ai_project_endpoint: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_key: str = ""
    azure_openai_key_secret_name: str = "azure-openai-key"
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_deployment: str = ""
    azure_search_endpoint: str = ""
    azure_search_key: str = ""
    azure_search_key_secret_name: str = "azure-search-key"
    azure_search_index: str = ""
    azure_search_content_field: str = "content"
    azure_search_source_field: str = "source"
    azure_search_top_k: int = 5
    key_vault_url: str = ""
    use_key_vault: bool = False
    cosmos_endpoint: str = ""
    cosmos_key: str = ""
    cosmos_key_secret_name: str = "cosmos-key"
    cosmos_database_name: str = "ragbot"
    cosmos_sessions_container: str = "sessions"
    cosmos_episodic_container: str = "episodic-memory"
    microsoft_entra_tenant: str = ""
    microsoft_entra_client_id: str = ""
    microsoft_entra_client_secret: str = ""
    microsoft_entra_client_secret_secret_name: str = "microsoft-entra-client-secret"
    api_base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
