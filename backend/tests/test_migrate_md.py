from app.scripts.migrate_md import parse_cards


def md(*lines: str) -> str:
    return "\n".join(lines)


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
