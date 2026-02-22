import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Card


@pytest.fixture(scope="function")
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()


@pytest.fixture
def client(db):
    return TestClient(app)


def make_card(db, **kwargs) -> Card:
    defaults = {
        "question": "Что такое list?",
        "answer": "Изменяемая последовательность.",
        "code_example": None,
        "category": "Python",
        "tags": json.dumps([]),
        "difficulty": "normal",
    }
    defaults.update(kwargs)
    card = Card(**defaults)
    db.add(card)
    db.commit()
    db.refresh(card)
    return card
