from __future__ import annotations

from app.config.settings import AppSettings


def load_key_vault_secrets(settings: AppSettings) -> AppSettings:
    if not settings.use_key_vault:
        return settings
    if not settings.key_vault_url:
        raise ValueError("KEY_VAULT_URL is required when USE_KEY_VAULT=true.")

    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient
    except ImportError as exc:
        raise RuntimeError(
            "azure-identity and azure-keyvault-secrets are required when USE_KEY_VAULT=true."
        ) from exc

    credential_options = {}
    if settings.managed_identity_client_id:
        credential_options["managed_identity_client_id"] = settings.managed_identity_client_id

    credential = DefaultAzureCredential(**credential_options)
    client = SecretClient(vault_url=settings.key_vault_url, credential=credential)

    _set_missing_secret(client, settings, "azure_openai_key", settings.azure_openai_key_secret_name)
    _set_missing_secret(client, settings, "azure_search_key", settings.azure_search_key_secret_name)
    _set_missing_secret(client, settings, "cosmos_key", settings.cosmos_key_secret_name)
    _set_missing_secret(
        client,
        settings,
        "microsoft_entra_client_secret",
        settings.microsoft_entra_client_secret_secret_name,
    )
    return settings


def _set_missing_secret(client: "SecretClient", settings: AppSettings, field_name: str, secret_name: str) -> None:
    if getattr(settings, field_name) or not secret_name:
        return
    secret = client.get_secret(secret_name)
    setattr(settings, field_name, secret.value or "")
