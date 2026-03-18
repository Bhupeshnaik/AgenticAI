"""
Azure configuration and settings for the Bank Marketing AI platform.
All settings loaded from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass


@dataclass
class AzureSettings:
    # Azure OpenAI
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    azure_openai_embedding_deployment: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")

    # Azure AI Foundry / Agent Service
    azure_ai_project_connection_string: str = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING", "")
    azure_ai_project_endpoint: str = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")

    # Azure Cosmos DB
    cosmos_endpoint: str = os.getenv("AZURE_COSMOS_ENDPOINT", "")
    cosmos_key: str = os.getenv("AZURE_COSMOS_KEY", "")
    cosmos_database: str = os.getenv("AZURE_COSMOS_DATABASE", "bank_marketing_ai")

    # Azure Blob Storage (DAM)
    storage_account_name: str = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "")
    storage_account_key: str = os.getenv("AZURE_STORAGE_ACCOUNT_KEY", "")
    storage_connection_string: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    dam_container: str = os.getenv("AZURE_STORAGE_DAM_CONTAINER", "digital-assets")
    documents_container: str = os.getenv("AZURE_STORAGE_DOCS_CONTAINER", "documents")

    # Azure AI Search
    search_endpoint: str = os.getenv("AZURE_SEARCH_ENDPOINT", "")
    search_api_key: str = os.getenv("AZURE_SEARCH_API_KEY", "")
    search_index_assets: str = os.getenv("AZURE_SEARCH_INDEX_ASSETS", "assets-index")
    search_index_campaigns: str = os.getenv("AZURE_SEARCH_INDEX_CAMPAIGNS", "campaigns-index")
    search_index_compliance: str = os.getenv("AZURE_SEARCH_INDEX_COMPLIANCE", "compliance-index")

    # Azure Document Intelligence
    document_intelligence_endpoint: str = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "")
    document_intelligence_key: str = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY", "")

    # Azure Communication Services
    communication_connection_string: str = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING", "")
    communication_email_sender: str = os.getenv("AZURE_COMMUNICATION_EMAIL_SENDER", "marketing@bank.com")

    # Azure Service Bus
    service_bus_connection_string: str = os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING", "")
    service_bus_queue_campaigns: str = os.getenv("AZURE_SERVICE_BUS_QUEUE_CAMPAIGNS", "campaigns-queue")
    service_bus_queue_leads: str = os.getenv("AZURE_SERVICE_BUS_QUEUE_LEADS", "leads-queue")

    # Azure Event Grid
    event_grid_endpoint: str = os.getenv("AZURE_EVENT_GRID_ENDPOINT", "")
    event_grid_key: str = os.getenv("AZURE_EVENT_GRID_KEY", "")

    # Application Settings
    app_name: str = "Bank Marketing AI Platform"
    app_version: str = "1.0.0"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    cors_origins: list = None

    def __post_init__(self):
        if self.cors_origins is None:
            origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
            self.cors_origins = [o.strip() for o in origins.split(",")]


settings = AzureSettings()
