import os

from dotenv import load_dotenv

load_dotenv("../.env")


def _require(name: str) -> str:
    """Возвращает обязательную переменную окружения или бросает понятную ошибку."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Не задана переменная окружения {name}")
    return value


def _parse_admin_ids(raw: str) -> list[int]:
    """Разбирает список id через запятую; пустые элементы пропускает."""
    ids: list[int] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            ids.append(int(item))
        except ValueError:
            raise RuntimeError(
                f"ADMIN_IDS: «{item}» не число (нужны id через запятую)"
            ) from None
    if not ids:
        raise RuntimeError("ADMIN_IDS не содержит ни одного id")
    return ids


class Settings:
    bot_token: str = _require("BOT_TOKEN")
    admin_ids: list[int] = _parse_admin_ids(_require("ADMIN_IDS"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/cards.db")
    cards_per_session: int = int(os.getenv("CARDS_PER_SESSION", "4"))
    # schedule_interval_hours: int = int(os.getenv("SCHEDULE_INTERVAL_HOURS", "5"))  # не нужен при настройке почасового крона
    pause_between_cards_seconds: int = int(
        os.getenv("PAUSE_BETWEEN_CARDS_SECONDS", "240")
    )
    telegram_enabled: bool = os.getenv("TELEGRAM_ENABLED", "true").lower() == "true"

    discord_webhook_url: str = os.getenv("DISCORD_WEBHOOK_URL", "")
    discord_max_length: int = 2000
    discord_timeout: int = 15


settings = Settings()
