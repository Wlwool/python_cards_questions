import json
import random
from html import escape

from sqlalchemy.orm import Session

from config import settings
from models import Card


def get_next_cards(db: Session, count: int, last_id: int = 0) -> list[Card]:
    """Возвращает следующие карточки по порядку начиная с last_id."""
    cards = db.query(Card).filter(Card.id > last_id).order_by(Card.id).limit(count).all()

    if len(cards) < count:
        extra = db.query(Card).order_by(Card.id).limit(count - len(cards)).all()
        cards += extra

    return cards


def get_random_card(db: Session) -> Card | None:
    cards = db.query(Card).all()
    if not cards:
        return None
    return random.choice(cards)


def format_card(card: Card) -> list[str]:
    """Форматирует карточку для Telegram (HTML)."""
    difficulty_emoji = {"easy": "🟢", "normal": "🟡", "hard": "🔴"}.get(card.difficulty, "⚪")

    text = (
        f"{difficulty_emoji} <b>{escape(card.category)}</b>\n\n"
        f"❓ <b>{escape(card.question)}</b>\n\n"
        f"{escape(card.answer)}"
    )

    tags = json.loads(card.tags or "[]")
    if tags:
        tags_line = " ".join(f"<code>{escape(t)}</code>" for t in tags)
        text += f"\n\n🏷 {tags_line}"

    parts = _split_telegram(text)

    if card.code_example:
        for code_part in _split_telegram(card.code_example, limit=4000):
            parts.append(
                f"<pre><code class=\"language-python\">{escape(code_part)}</code></pre>"
            )
    return parts

def _split_telegram(text: str, limit: int = 4096) -> list[str]:
    if len(text) <= limit:
        return [text]

    parts = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        parts.append(text[:split_at])
        text = text[split_at:].lstrip()

    return parts


def format_card_discord(card: Card) -> list[str]:
    """Форматирует карточку для Discord (Markdown)."""
    difficulty_emoji = {"easy": "🟢", "normal": "🟡", "hard": "🔴"}.get(card.difficulty, "⚪")
    text = (
        f"{difficulty_emoji} **{card.category}**\n"
        f"**``` {card.question} ```**"
        f"{card.answer}\n")

    tags = json.loads(card.tags or "[]")
    if tags:
        text += "\n\n🏷 " + " ".join(f"`{t}`" for t in tags)

    parts = _split_discord(text)
    if card.code_example:
        _append_discord_code(card.code_example, parts)
    return parts


def _append_discord_code(code: str, parts: list[str]) -> None:
    """Оборачивает код в ```python блок, разбивая если нужно."""
    limit = settings.discord_max_length
    # 12 = len("```python\n") + len("\n```")
    chunk_limit = limit - 12

    if len(code) <= chunk_limit:
        parts.append(f"```python\n{code}\n```")
        return

    for chunk in _split_discord(code, limit=chunk_limit):
        parts.append(f"```python\n{chunk}\n```")


def _split_discord(text: str, limit: int | None = None) -> list[str]:
    if limit is None:
        limit = settings.discord_max_length

    if len(text) <= limit:
        return [text]

    parts = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        parts.append(text[:split_at])
        text = text[split_at:].lstrip()

    return parts
