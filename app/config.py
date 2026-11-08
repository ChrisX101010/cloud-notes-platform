from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str
    supabase_service_role_key: str
    supabase_bucket: str = "codomax-files"
    app_env: str = "development"
    max_upload_bytes: int = 1_048_576
    max_note_chars: int = 1_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
