import json
from html import unescape
from unittest.mock import MagicMock

import pytest

from cards import (
    _PRE_CLOSE,
    _PRE_OPEN,
    _split_text,
    format_card,
    format_card_discord,
    get_next_cards,
    get_random_card,
)
from config import settings
from models import Card

BAD_TAGS = ["{bad", "5", '"abc"', '{"a": 1}', "[1, 2]"]


def make_card(**kwargs) -> Card:
    """Создаёт карточку с дефолтными значениями для тестов."""
    defaults = {
        "id": 1,
        "question": "Что такое list?",
        "answer": "Изменяемая последовательность элементов.",
        "code_example": None,
        "category": "Python",
        "tags": "[]",
        "difficulty": "easy",
    }
    defaults.update(kwargs)
    card = Card()
    for k, v in defaults.items():
        setattr(card, k, v)
    return card


class TestSplitMessage:
    def test_short_message_not_split(self):
        text = "короткое сообщение"
        assert _split_text(text, 4096) == [text]

    def test_long_message_split(self):
        text = "а" * 5000
        parts = _split_text(text, 4096)
        assert len(parts) > 1
        assert all(len(p) <= 4096 for p in parts)

    def test_split_preserves_content(self):
        text = "\n".join(f"строка {i}" for i in range(1000))
        parts = _split_text(text, limit=500)
        assert len(parts) > 1
        assert "\n".join(parts) == text

    def test_exact_limit_not_split(self):
        text = "а" * 4096
        assert _split_text(text, 4096) == [text]

    def test_split_prefers_newline(self):
        line = "а" * 100
        text = (line + "\n") * 50
        parts = _split_text(text, limit=512)
        assert len(parts) > 1
        assert all(len(part) <= 512 for part in parts)
        for part in parts:
            assert all(item == line for item in part.split("\n") if item)


class TestFormatCard:
    def test_returns_list(self):
        card = make_card()
        result = format_card(card)
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_contains_question(self):
        card = make_card(question="Что такое dict?")
        result = format_card(card)
        assert any("dict" in part for part in result)

    def test_contains_category(self):
        card = make_card(category="Django")
        result = format_card(card)
        assert any("Django" in part for part in result)

    def test_difficulty_emoji_easy(self):
        card = make_card(difficulty="easy")
        result = format_card(card)
        assert any("🟢" in part for part in result)

    def test_difficulty_emoji_normal(self):
        card = make_card(difficulty="normal")
        result = format_card(card)
        assert any("🟡" in part for part in result)

    def test_difficulty_emoji_hard(self):
        card = make_card(difficulty="hard")
        result = format_card(card)
        assert any("🔴" in part for part in result)

    def test_code_example_in_separate_message(self):
        card = make_card(code_example="print('hello')")
        result = format_card(card)
        # код идёт отдельным сообщением последним элементом списка
        assert any("print" in part for part in result)
        assert "<pre>" in result[-1]

    def test_no_code_example(self):
        card = make_card(code_example=None)
        result = format_card(card)
        assert any(
            "list" in part.lower() or "последовательность" in part for part in result
        )

    def test_code_example_none_no_pre_tag(self):
        card = make_card(code_example=None)
        result = format_card(card)
        assert not any("<pre>" in part for part in result)

    def test_tags_included(self):
        card = make_card(tags=json.dumps(["list", "basics"]))
        result = format_card(card)
        assert any("list" in part for part in result)

    def test_each_part_within_limit(self):
        long_answer = "текст " * 1000
        card = make_card(answer=long_answer)
        result = format_card(card)
        assert all(len(part) <= 4096 for part in result)

    def test_special_chars_escaped(self):
        card = make_card(answer="цена < 100 & скидка > 10%")
        result = format_card(card)
        full = "".join(result)
        assert "&lt;" in full
        assert "&gt;" in full
        assert "&amp;" in full

    def test_code_parts_within_limit_after_escape(self):
        """Код с символами < > & после escape и обёртки не длиннее 4096."""
        card = make_card(code_example="<" * 5000)
        result = format_card(card)
        assert all(len(part) <= 4096 for part in result)

    def test_code_parts_preserve_code(self):
        """Склейка кусков кода даёт исходный код."""
        code = "\n".join(f"    if a < {i} and b > {i}: pass" for i in range(400))
        card = make_card(code_example=code)
        code_parts = format_card(card)[1:]
        restored = "".join(
            unescape(p.removeprefix(_PRE_OPEN).removesuffix(_PRE_CLOSE))
            for p in code_parts
        )
        assert len(code_parts) > 1
        assert restored.replace("\n", "") == code.replace("\n", "")


class TestGetNextCards:
    def test_returns_requested_count(self):
        db = MagicMock()
        cards = [make_card(id=i) for i in range(1, 4)]
        db.query().filter().order_by().limit().all.return_value = cards
        result = get_next_cards(db, 3, last_id=0)
        assert len(result) == 3

    def test_wraps_around_when_end_reached(self):
        db = MagicMock()
        first_cards = [make_card(id=10)]
        extra_cards = [make_card(id=1), make_card(id=2)]
        db.query().filter().order_by().limit().all.return_value = first_cards
        db.query().order_by().limit().all.return_value = extra_cards
        result = get_next_cards(db, 3, last_id=9)
        assert len(result) == 3

    def test_empty_db_returns_empty(self):
        db = MagicMock()
        db.query().filter().order_by().limit().all.return_value = []
        db.query().order_by().limit().all.return_value = []
        result = get_next_cards(db, 3, last_id=0)
        assert result == []


class TestGetRandomCard:
    def test_returns_card(self):
        db = MagicMock()
        cards = [make_card(id=1), make_card(id=2)]
        db.query().all.return_value = cards
        result = get_random_card(db)
        assert result in cards

    def test_returns_none_for_empty_db(self):
        db = MagicMock()
        db.query().all.return_value = []
        result = get_random_card(db)
        assert result is None


class TestFormatCardDiscord:
    def test_long_code_parts_within_discord_limit(self):
        """Каждое сообщение вместе с обёрткой ```python не длиннее лимита Discord."""
        card = make_card(code_example="x" * 5000)
        result = format_card_discord(card)
        assert all(len(part) <= settings.discord_max_length for part in result)


class TestBrokenTags:
    @pytest.mark.parametrize("tags", BAD_TAGS)
    def test_telegram_ignores_invalid_tags(self, tags):
        card = make_card(tags=tags)
        assert "🏷" not in "".join(format_card(card))

    @pytest.mark.parametrize("tags", BAD_TAGS)
    def test_discord_ignores_invalid_tags(self, tags):
        card = make_card(tags=tags)
        assert "🏷" not in "".join(format_card_discord(card))

    def test_invalid_tags_logged_with_card_id(self, caplog):
        card = make_card(id=7, tags="{bad")
        with caplog.at_level("WARNING"):
            format_card(card)
        assert "id=7" in caplog.text

    def test_discord_valid_tags_included(self):
        card = make_card(tags=json.dumps(["list", "basics"]))
        assert "`list`" in "".join(format_card_discord(card))
