from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./derby.db"
    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    entry_cost_tokens: int = 10
    starting_tokens: int = 100
    winner_bonus_tokens: int = 50
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"

    # Prize tiers: entry cost and winner bonus on top of pool (pool = sum of entry costs)
    entry_cost_standard: int = 10
    entry_cost_grand: int = 25
    entry_cost_prestigious: int = 50
    winner_bonus_standard: int = 50
    winner_bonus_grand: int = 150
    winner_bonus_prestigious: int = 300

    # SSO (optional): set to enable "Sign in with Google"
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: Optional[str] = None  # e.g. http://localhost:5173/auth/callback or your frontend URL

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()


def entry_cost_for_tier(tier: str) -> int:
    if tier == "grand":
        return settings.entry_cost_grand
    if tier == "prestigious":
        return settings.entry_cost_prestigious
    return settings.entry_cost_standard

def winner_bonus_for_tier(tier: str) -> int:
    if tier == "grand":
        return settings.winner_bonus_grand
    if tier == "prestigious":
        return settings.winner_bonus_prestigious
    return settings.winner_bonus_standard
