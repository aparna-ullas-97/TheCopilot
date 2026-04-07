from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Rubix AI Backend"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    LLM_PROVIDER: str = "gemini"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    LLAMA_MODEL: str = "llama3"
    LLAMA_BASE_URL: str = "http://localhost:11434"

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/rubix_ai"
    UPLOAD_DIR: str = "storage/uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()