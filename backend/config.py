from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    database_url: str = "postgresql+asyncpg://legal_ai:legal_ai_dev@localhost:5432/legal_ai"

    @model_validator(mode="after")
    def fix_database_url(self):
        # Render provides postgres:// but asyncpg needs postgresql+asyncpg://
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self
    upload_dir: str = "/var/data/uploads"
    frontend_url: str = "http://localhost:3000"
    max_upload_size_mb: int = 50

    # Embedding config
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # Chunking config
    chunk_target_tokens: int = 512
    chunk_overlap_tokens: int = 50

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
