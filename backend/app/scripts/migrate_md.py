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
    current_code_lines = []
    in_code_block = False

    lines = text.splitlines()

    def flush_card():
        if not current_question:
            return
        answer = "\n".join(current_answer_lines).strip()
        code = "\n".join(current_code_lines).strip() if current_code_lines else None
        cards.append({
            "question": current_question.strip(),
            "answer": answer,
            "code_example": code,
            "category": current_category,
            "tags": [],
            "difficulty": "normal",
        })

    for line in lines:
        # отслеживает блоки кода
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                current_code_lines = []
            else:
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
                current_code_lines = []
                current_category = title
            else:
                # заголовок 3+ уровня считается вопросом
                flush_card()
                current_question = title
                current_answer_lines = []
                current_code_lines = []
            continue

        if current_question is not None:
            current_answer_lines.append(line)

    flush_card()
    return cards


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to questions.md")
    parser.add_argument("--clear", action="store_true", help="Удалить все карточки перед импортом")
    args = parser.parse_args()

    with open(args.file, encoding="utf-8") as f:
        text = f.read()

    cards_data = parse_cards(text)
    print(f"Найдено карточек: {len(cards_data)}")

    db = SessionLocal()
    try:
        if args.clear:
            db.query(Card).delete()
            db.commit()
            print("Старые карточки удалены")

        inserted = 0
        for data in cards_data:
            if not data["question"] or not data["answer"]:
                continue
            card = Card(
                question=data["question"],
                answer=data["answer"],
                code_example=data["code_example"],
                category=data["category"],
                tags=json.dumps(data["tags"], ensure_ascii=False),
                difficulty=data["difficulty"],
            )
            db.add(card)
            inserted += 1

        db.commit()
        print(f"Импортировано: {inserted} карточек")
    finally:
        db.close()


if __name__ == "__main__":
    main()
