import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Qdrant Configuration
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    REGULATIONS_COLLECTION_NAME: str = "regulations_bbmp_2003"
    PATTERNS_COLLECTION_NAME: str = "patterns_resplan"
    
    # Embedding Model (Local - No API Key required)
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    VECTOR_SIZE: int = 384
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    PDF_SOURCE_DIR: str = os.path.join(BASE_DIR, "rag", "regulations", "sources")

    class Config:
        env_file = ".env"

# 👇 THIS WAS LIKELY MISSING 👇
settings = Settings()