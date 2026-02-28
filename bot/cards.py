import json
import random
from html import escape

from sqlalchemy.orm import Session

from models import Card


def get_next_cards(db: Session, count: int, last_id: int = 0) -> list[Card]:
    """Возвращает следующие карточки по порядку начиная с last_id."""
    cards = db.query(Card).filter(Card.id > last_id).order_by(Card.id).limit(count).all()

    # если дошли до конца — начинаем сначала
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
    """Форматирует карточку в список сообщений с учётом лимита Telegram 4096 символов."""
    difficulty_emoji = {"easy": "🟢", "normal": "🟡", "hard": "🔴"}.get(card.difficulty, "⚪")

    text = (
        f"{difficulty_emoji} *{escape(card.category)}*\n\n"
        f"❓ *{escape(card.question)}*\n\n"
        f"{escape(card.answer)}"
    )

    if card.code_example:
        text += f"\n\n<pre><code class=\"language-python\">{escape(card.code_example)}</code></pre>"

    tags = json.loads(card.tags or "[]")
    if tags:
        tags_line = " ".join(f"<code>{escape(t)}</code>" for t in tags)
        text += f"\n\n🏷 {tags_line}"

    return split_message(text)


# def escape_md(text: str) -> str:
#     """Экранирует спецсимволы Markdown v2."""
#     chars = r"_*[]()~`>#+-=|{}.!"
#     for ch in chars:
#         text = text.replace(ch, f"\\{ch}")
#     return text


def split_message(text: str, limit: int = 4096) -> list[str]:
    """Разбивает текст на части если превышает лимит Telegram."""
    if len(text) <= limit:
        return [text]

    parts = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        # разбивает по последнему переносу строки перед лимитом
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        parts.append(text[:split_at])
        text = text[split_at:].lstrip()

    return parts
