import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cards import get_next_cards
from models import Card


def add_cards(db, count: int) -> None:
    for i in range(1, count + 1):
        db.add(
            Card(
                id=i,
                question=f"Вопрос {i}",
                answer=f"Ответ {i}",
                category="Python",
                tags="[]",
                difficulty="easy",
            )
        )
    db.commit()


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Card.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


class TestGetNextCardsRealDb:
    def test_returns_cards_after_last_id_in_order(self, db):
        add_cards(db, 6)
        result = get_next_cards(db, 3, last_id=2)
        assert [c.id for c in result] == [3, 4, 5]

    def test_wraps_around_to_start(self, db):
        add_cards(db, 5)
        result = get_next_cards(db, 3, last_id=4)
        assert [c.id for c in result] == [5, 1, 2]

    def test_last_id_beyond_max_starts_from_beginning(self, db):
        add_cards(db, 5)
        result = get_next_cards(db, 3, last_id=100)
        assert [c.id for c in result] == [1, 2, 3]

    def test_empty_db_returns_empty(self, db):
        assert get_next_cards(db, 3, last_id=0) == []
