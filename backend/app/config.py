from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    azure_language_endpoint: str
    azure_language_key: str
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"

    class Config:
        env_file = ".env"


settings = Settings()
