import importlib
from unittest.mock import patch

from app.models import Card
from app.scripts import migrate_md
from app.scripts.migrate_md import parse_cards
from tests.conftest import make_card


def md(*lines: str) -> str:
    return "\n".join(lines)


def card_data(question: str, category: str = "Python", answer: str = "Ответ.") -> dict:
    return {
        "question": question,
        "answer": answer,
        "code_example": None,
        "category": category,
        "tags": [],
        "difficulty": "normal",
    }


class TestParseCards:
    def test_single_card(self):
        cards = parse_cards(
            md("# Python", "#### Что такое list?", "Изменяемая последовательность.")
        )
        assert cards == [
            {
                "question": "Что такое list?",
                "answer": "Изменяемая последовательность.",
                "code_example": None,
                "category": "Python",
                "tags": [],
                "difficulty": "normal",
            }
        ]

    def test_default_category_when_no_header(self):
        cards = parse_cards(md("### Вопрос?", "Ответ."))
        assert cards[0]["category"] == "General"

    def test_h2_changes_category(self):
        cards = parse_cards(
            md("# Python", "## Функции", "### Что такое lambda?", "Ответ.")
        )
        assert cards[0]["category"] == "Функции"

    def test_several_cards_in_order(self):
        cards = parse_cards(
            md("# A", "### Q1", "a1", "### Q2", "a2", "# B", "### Q3", "a3")
        )
        assert [(c["question"], c["category"]) for c in cards] == [
            ("Q1", "A"),
            ("Q2", "A"),
            ("Q3", "B"),
        ]

    def test_text_before_first_question_ignored(self):
        cards = parse_cards(md("вступление", "# A", "### Q", "ответ"))
        assert len(cards) == 1
        assert cards[0]["answer"] == "ответ"

    def test_single_code_block(self):
        cards = parse_cards(md("### Q", "текст", "```python", "print(1)", "```"))
        assert cards[0]["answer"] == "текст"
        assert cards[0]["code_example"] == "print(1)"

    def test_several_code_blocks_numbered(self):
        cards = parse_cards(
            md(
                "### Q",
                "текст",
                "```python",
                "print(1)",
                "```",
                "```python",
                "print(2)",
                "```",
            )
        )
        assert cards[0]["code_example"] == (
            "# Пример 1\n\nprint(1)\n\n# Пример 2\n\nprint(2)"
        )

    def test_header_inside_code_block_is_not_a_question(self):
        cards = parse_cards(md("### Q", "текст", "```python", "# комментарий", "```"))
        assert len(cards) == 1
        assert cards[0]["code_example"] == "# комментарий"


class TestImportCards:
    def test_inserts_new_cards(self, db):
        result = migrate_md.import_cards(db, [card_data("Q1"), card_data("Q2")])
        assert result == (2, 0)
        assert db.query(Card).count() == 2

    def test_second_run_skips_duplicates(self, db):
        data = [card_data("Q1"), card_data("Q2")]
        migrate_md.import_cards(db, data)
        assert migrate_md.import_cards(db, data) == (0, 2)
        assert db.query(Card).count() == 2

    def test_existing_card_in_db_skipped(self, db):
        make_card(db, question="Q", category="Python")
        assert migrate_md.import_cards(db, [card_data("Q")]) == (0, 1)
        assert db.query(Card).count() == 1

    def test_same_question_in_other_category_is_not_duplicate(self, db):
        data = [card_data("Q", "Python"), card_data("Q", "Django")]
        assert migrate_md.import_cards(db, data) == (2, 0)

    def test_duplicates_inside_file_skipped(self, db):
        assert migrate_md.import_cards(db, [card_data("Q"), card_data("Q")]) == (1, 1)
        assert db.query(Card).count() == 1

    def test_empty_question_or_answer_not_imported(self, db):
        data = [card_data(""), card_data("Q", answer="")]
        assert migrate_md.import_cards(db, data) == (0, 0)
        assert db.query(Card).count() == 0


class TestFindUnclosedCode:
    def test_closed_blocks_give_no_warnings(self):
        text = md(
            "# Python",
            "### Q",
            "```python",
            "print(1)",
            "```",
            "```python",
            "print(2)",
            "```",
        )
        assert migrate_md.find_unclosed_code(text) == []

    def test_header_inside_closed_block_is_not_a_problem(self):
        text = md("### Q", "```python", "# комментарий", "```")
        assert migrate_md.find_unclosed_code(text) == []

    def test_unclosed_at_end_of_file(self):
        text = md("# Python", "### Что такое lambda?", "текст", "```python", "x = 1")
        warnings = migrate_md.find_unclosed_code(text)
        assert len(warnings) == 1
        assert "Что такое lambda?" in warnings[0]
        assert "Python" in warnings[0]

    def test_unclosed_in_middle_reports_question_and_lost_header(self):
        text = md(
            "# Python",
            "### Q1",
            "```python",
            "x = 1",
            "### Q2",
            "ответ",
            "```python",
            "y = 2",
            "```",
        )
        warnings = migrate_md.find_unclosed_code(text)
        assert len(warnings) == 2
        assert "Q1" in warnings[0]
        assert "Q2" in warnings[1]

    def test_unclosed_at_end_reports_lost_header_too(self):
        text = md("### Q1", "```python", "x = 1", "### Q2", "текст")
        warnings = migrate_md.find_unclosed_code(text)
        assert len(warnings) == 2
        assert "Q1" in warnings[0]
        assert "Q2" in warnings[1]


class TestImportHasNoSideEffects:
    def test_import_does_not_create_tables(self):
        with patch("app.models.Base.metadata.create_all") as create_all:
            importlib.reload(migrate_md)
        create_all.assert_not_called()
