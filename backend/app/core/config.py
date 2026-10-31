from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Sistema de Control de Pagos"
    app_version: str = "1.0.0"

    database_host: str
    database_port: int = 5432
    database_name: str
    database_user: str
    database_password: str
    paymentschool_storage_dir: str = "storage"
    cors_origins: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    )
    cors_origin_regex: str | None = (
        r"^https://payment-school-[a-z0-9-]+-william-4d5e"
        r"\.vercel\.app$"
    )

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,



    )


settings = Settings()