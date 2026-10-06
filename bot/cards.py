import json
import logging
from html import escape

from sqlalchemy import func
from sqlalchemy.orm import Session

from config import settings
from models import Card

log = logging.getLogger(__name__)

_CODE_FENCE_OPEN = "```python\n"
_CODE_FENCE_CLOSE = "\n```"
_PRE_OPEN = '<pre><code class="language-python">'
_PRE_CLOSE = "</code></pre>"
_TELEGRAM_MAX_LENGTH = 4096


def _difficulty_emoji(difficulty: str) -> str:
    return {"easy": "🟢", "normal": "🟡", "hard": "🔴"}.get(difficulty, "⚪")


def _parse_tags(card: Card) -> list[str]:
    """Разбирает теги карточки. Битые или неожиданные данные дают пустой список."""
    try:
        tags = json.loads(card.tags or "[]")
    except (ValueError, TypeError):
        log.warning(f"Карточка id={card.id}: теги не разобрать как JSON, пропуск")
        return []
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        log.warning(f"Карточка id={card.id}: теги не список строк, пропуск")
        return []
    return tags


def get_next_cards(db: Session, count: int, last_id: int = 0) -> list[Card]:
    """Возвращает следующие карточки по порядку начиная с last_id."""
    cards = (
        db.query(Card).filter(Card.id > last_id).order_by(Card.id).limit(count).all()
    )

    if len(cards) < count:
        extra = db.query(Card).order_by(Card.id).limit(count - len(cards)).all()
        cards += extra
    return cards


def get_random_card(db: Session) -> Card | None:
    return db.query(Card).order_by(func.random()).first()


def format_card(card: Card) -> list[str]:
    """Форматирует карточку для Telegram (HTML)."""
    difficulty_emoji = _difficulty_emoji(card.difficulty)

    text = (
        f"{difficulty_emoji} <b>{escape(card.category)}</b>\n\n"
        f"❓ <b>{escape(card.question)}</b>\n\n"
        f"{escape(card.answer)}"
    )

    tags = _parse_tags(card)
    if tags:
        tags_line = " ".join(f"<code>{escape(t)}</code>" for t in tags)
        text += f"\n\n🏷 {tags_line}"
    parts = _split_text(text, _TELEGRAM_MAX_LENGTH)

    if card.code_example:
        for code_part in _split_code_telegram(card.code_example):
            parts.append(f"{_PRE_OPEN}{escape(code_part)}{_PRE_CLOSE}")
    return parts


def _split_code_telegram(code: str, limit: int = 4096) -> list[str]:
    """Режет код так, чтобы после escape и обёртки <pre><code> сообщение влезло в limit.
    Режет по последнему переводу строки, отступы следующего куска не трогает.
    """
    budget = limit - len(_PRE_OPEN) - len(_PRE_CLOSE)
    parts: list[str] = []
    while code:
        used = 0
        end = 0
        for ch in code:
            size = len(escape(ch))
            if used + size > budget:
                break
            used += size
            end += 1
        else:
            parts.append(code)
            break
        cut = code.rfind("\n", 0, end)
        if cut <= 0:
            cut = end
        parts.append(code[:cut])
        code = code[cut:].lstrip("\n")
    return parts


def _split_text(text: str, limit: int) -> list[str]:
    """Режет текст на части не длиннее limit, предпочитая границы строк."""
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
    difficulty_emoji = _difficulty_emoji(card.difficulty)
    text = (
        f"{difficulty_emoji} **{card.category}**\n\n"
        f"**```{card.question} ```**"
        f"{card.answer}\n"
    )

    tags = _parse_tags(card)
    if tags:
        text += "\n\n🏷 " + " ".join(f"`{t}`" for t in tags)

    parts = _split_text(text, settings.discord_max_length)
    if card.code_example:
        _append_discord_code(card.code_example, parts)
    return parts


def _append_discord_code(code: str, parts: list[str]) -> None:
    """Оборачивает код в ```python блок, разбивая если нужно."""
    limit = settings.discord_max_length
    chunk_limit = limit - len(_CODE_FENCE_OPEN) - len(_CODE_FENCE_CLOSE)

    if len(code) <= chunk_limit:
        parts.append(f"{_CODE_FENCE_OPEN}{code}{_CODE_FENCE_CLOSE}")
        return

    for chunk in _split_text(code, chunk_limit):
        parts.append(f"{_CODE_FENCE_OPEN}{chunk}{_CODE_FENCE_CLOSE}")
