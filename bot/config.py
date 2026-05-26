import os
from dotenv import load_dotenv

load_dotenv("../.env")

class Settings:
    bot_token: str = os.environ["BOT_TOKEN"]
    admin_ids: list[int] = [int(i) for i in os.environ["ADMIN_IDS"].split(",")]
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/cards.db")
    cards_per_session: int = int(os.getenv("CARDS_PER_SESSION", "4"))
    schedule_interval_hours: int = int(os.getenv("SCHEDULE_INTERVAL_HOURS", "5"))
    pause_between_cards_seconds: int = int(os.getenv("PAUSE_BETWEEN_CARDS_SECONDS", "240"))
    telegram_enabled: bool = os.getenv("TELEGRAM_ENABLED", "true").lower() == "true"

    discord_webhook_url: str = os.getenv("DISCORD_WEBHOOK_URL", "")
    discord_max_length: int = 2000
    discord_timeout: int = 15

settings = Settings()
