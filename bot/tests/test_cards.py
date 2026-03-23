import json
from unittest.mock import MagicMock

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cards import split_message, format_card, get_next_cards, get_random_card
from models import Card


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
        assert split_message(text) == [text]

    def test_long_message_split(self):
        text = "а" * 5000
        parts = split_message(text)
        assert len(parts) > 1
        assert all(len(p) <= 4096 for p in parts)

    def test_split_preserves_content(self):
        text = "слово " * 1000
        parts = split_message(text)
        assert "".join(parts).replace(" ", "") == text.replace(" ", "")

    def test_exact_limit_not_split(self):
        text = "а" * 4096
        assert split_message(text) == [text]

    def test_split_prefers_newline(self):
        line = "а" * 100 + "\n"
        text = line * 50
        parts = split_message(text, limit=512)
        for part in parts:
            assert len(part) <= 512


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
        assert any("list" in part.lower() or "последовательность" in part for part in result)

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
