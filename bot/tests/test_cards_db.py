import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from cards import get_next_cards, get_random_card
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


class TestGetRandomCardRealDb:
    def test_returns_one_of_the_cards(self, db):
        add_cards(db, 3)
        assert get_random_card(db).id in {1, 2, 3}

    def test_empty_db_returns_none(self, db):
        assert get_random_card(db) is None

    def test_selects_single_row_in_sql(self, db):
        add_cards(db, 5)
        statements: list[str] = []
        event.listen(
            db.get_bind(),
            "before_cursor_execute",
            lambda conn, cursor, statement, params, context, many: statements.append(
                statement
            ),
        )
        get_random_card(db)
        assert len(statements) == 1
        assert "LIMIT" in statements[0].upper()
