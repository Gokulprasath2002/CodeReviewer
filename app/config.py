import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_path: str = os.getenv("DATABASE_PATH", "./data/reviews.db")
    webhook_secret: str = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5")
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    publish_reviews: bool = os.getenv("PUBLISH_REVIEWS", "false").lower() == "true"


settings = Settings()
