from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VakiBot API"
    app_version: str = "0.1.0"
    app_env: str = "dev"

    chroma_persist_dir: str = "/app/storage/chroma"
    data_dir: str = "/app/data"

    top_k_default: int = 4
    max_context_chunks: int = 6

    groq_api_key: str = ""
    groq_api_keys: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    embedding_api_key: str = ""
    embedding_api_keys: str = ""
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"

    retrieval_mode: str = "hybrid"
    rag_engine: str = "diy"
    hybrid_vector_weight: float = 0.7
    hybrid_bm25_weight: float = 0.3
    retrieval_min_score: float = 0.35
    strict_legal_mode: bool = True
    legal_default_domain: str = "loi"
    legal_filename_hint: str = "code"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
