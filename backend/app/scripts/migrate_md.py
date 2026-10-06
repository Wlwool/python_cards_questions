"""
Запуск: python scripts/migrate_md.py --file questions.md

Формат questions.md который ожидаем:
# Категория
## Подкатегория (опционально)
#### Вопрос?
Текст ответа...

```python
код пример
```
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models import Base, Card

Base.metadata.create_all(bind=engine)


def parse_cards(text: str) -> list[dict]:
    cards = []
    current_category = "General"
    current_question = None
    current_answer_lines = []
    current_code_blocks: list[list[str]] = []
    current_code_lines: list[str] = []
    in_code_block = False

    lines = text.splitlines()

    def flush_card():
        if not current_question:
            return
        answer = "\n".join(current_answer_lines).strip()

        if current_code_blocks:
            if len(current_code_blocks) == 1:
                code = "\n".join(current_code_blocks[0]).strip()
            else:
                parts = []
                for i, block_lines in enumerate(current_code_blocks, start=1):
                    parts.append(f"# Пример {i}")
                    parts.append("\n".join(block_lines).strip())
                code = "\n\n".join(parts)
        else:
            code = None

        cards.append(
            {
                "question": current_question.strip(),
                "answer": answer,
                "code_example": code,
                "category": current_category,
                "tags": [],
                "difficulty": "normal",
            }
        )

    for line in lines:
        # отслеживает блоки кода
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                current_code_lines = []
            else:
                current_code_blocks.append(current_code_lines)
                current_code_lines = []
                in_code_block = False
            continue

        if in_code_block:
            current_code_lines.append(line)
            continue

        # определяет уровень заголовка
        header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()

            if level <= 2:
                # сохраняет предыдущую карточку и обновляет категорию
                flush_card()
                current_question = None
                current_answer_lines = []
                current_code_blocks = []
                current_code_lines = []
                current_category = title
            else:
                # заголовок 3+ уровня считается вопросом
                flush_card()
                current_question = title
                current_answer_lines = []
                current_code_blocks = []
                current_code_lines = []
            continue

        if current_question is not None:
            current_answer_lines.append(line)

    flush_card()
    return cards


def find_unclosed_code(text: str) -> list[str]:
    """Ищет незакрытые блоки кода и вопросы, потерянные из-за них.
    Это эвристика: ограда с языком внутри блока считается началом нового блока.
    """
    warnings: list[str] = []
    category = "General"
    question = None
    in_code = False
    code_owner: tuple[str | None, str] = (None, category)
    lost: list[str] = []

    def report_unclosed() -> None:
        q, c = code_owner
        warnings.append(
            f'Незакрытый блок кода в вопросе "{q or "?"}" (категория "{c}"): '
            "проверьте карточку"
        )
        warnings.extend(
            f'Заголовок "{title}" внутри незакрытого блока: карточка не будет создана'
            for title in lost
        )

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code:
                in_code = True
                code_owner = (question, category)
            elif len(stripped) > 3:
                report_unclosed()
                code_owner = (question, category)
            else:
                in_code = False
            lost = []
            continue

        header = re.match(r"^(#{1,6})\s+(.+)$", line)
        if in_code:
            if header and len(header.group(1)) >= 3:
                lost.append(header.group(2).strip())
            continue

        if header:
            title = header.group(2).strip()
            if len(header.group(1)) <= 2:
                category = title
                question = None
            else:
                question = title

    if in_code:
        report_unclosed()
    return warnings


def import_cards(db, cards_data: list[dict]) -> tuple[int, int]:
    """Добавляет карточки в БД, пропуская дубли по паре (вопрос, категория).
    Возвращает (добавлено, пропущено как дубли).
    Карточки с пустым вопросом или ответом не считаются ни добавленными, ни дублями.
    """
    seen = set(db.query(Card.question, Card.category).all())
    inserted = 0
    skipped = 0
    for data in cards_data:
        if not data["question"] or not data["answer"]:
            continue
        key = (data["question"], data["category"])
        if key in seen:
            skipped += 1
            continue
        seen.add(key)
        db.add(
            Card(
                question=data["question"],
                answer=data["answer"],
                code_example=data["code_example"],
                category=data["category"],
                tags=json.dumps(data["tags"], ensure_ascii=False),
                difficulty=data["difficulty"],
            )
        )
        inserted += 1
    db.commit()
    return inserted, skipped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to questions.md")
    parser.add_argument(
        "--clear", action="store_true", help="Удалить все карточки перед импортом"
    )
    args = parser.parse_args()

    with open(args.file, encoding="utf-8") as f:
        text = f.read()

    for warning in find_unclosed_code(text):
        print(f"ВНИМАНИЕ: {warning}")

    cards_data = parse_cards(text)
    print(f"Найдено карточек: {len(cards_data)}")

    db = SessionLocal()
    try:
        if args.clear:
            db.query(Card).delete()
            db.commit()
            print("Старые карточки удалены")

        inserted, skipped = import_cards(db, cards_data)
        print(f"Импортировано: {inserted} карточек, пропущено дублей: {skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
