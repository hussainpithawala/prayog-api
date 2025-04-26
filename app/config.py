from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    cassandra_host: str = "localhost"
    cassandra_port: int = 9042
    cassandra_keyspace: str = "prayog_api_keyspace"
    otel_enabled: bool = True
    otel_service_name: str = "prayog-api-service"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"

    class Config:
        env_file = ".env"

settings = Settings()