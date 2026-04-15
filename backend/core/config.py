import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Georgia Tech RAG Chatbot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # NVIDIA NIM settings
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "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")
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    
    # Model selections
    LLM_MODEL: str = "meta/llama-3.1-70b-instruct"
    EMBEDDING_MODEL: str = "nvidia/nv-embedqa-e5-v5"

    # Context management
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.2

    # Vector DB settings
    VECTOR_DB_PATH: str = "./data/qdrant_storage"
    QDRANT_URL: str | None = os.getenv("QDRANT_URL", None)

    # Redis settings
    REDIS_URL: str | None = os.getenv("REDIS_URL", None)

settings = Settings()
