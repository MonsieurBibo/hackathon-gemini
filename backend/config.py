from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str = ""
    google_api_key: str = ""  # alias Google Cloud (GOOGLE_API_KEY)

    @property
    def resolved_api_key(self) -> str:
        return self.gemini_api_key or self.google_api_key
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
