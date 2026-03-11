from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres@127.0.0.1:5432/derby"
    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    entry_cost_tokens: int = 10
    starting_tokens: int = 100
    winner_bonus_tokens: int = 50
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
