import json

from app.auth import create_token
from app.models import Card
from tests.conftest import make_card

URL = "/api/admin/cards"


def auth() -> dict:
    return {"Authorization": f"Bearer {create_token()}"}


def card_payload(**overrides) -> dict:
    payload = {
        "question": "Что такое GIL?",
        "answer": "Глобальная блокировка интерпретатора.",
        "category": "Python",
    }
    payload.update(overrides)
    return payload


class TestCreateCard:
    def test_requires_auth(self, client, db):
        response = client.post(URL, json=card_payload())
        assert response.status_code == 401
        assert db.query(Card).count() == 0

    def test_creates_card_with_defaults(self, client, db):
        response = client.post(URL, json=card_payload(), headers=auth())
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == "Что такое GIL?"
        assert data["difficulty"] == "normal"
        assert data["tags"] == []
        assert db.query(Card).count() == 1

    def test_saves_tags_and_returns_them_as_list(self, client):
        response = client.post(
            URL, json=card_payload(tags=["список", "dict"]), headers=auth()
        )
        data = response.json()
        assert data["tags"] == ["список", "dict"]
        saved = client.get(f"/api/cards/{data['id']}").json()
        assert saved["tags"] == ["список", "dict"]

    def test_invalid_difficulty_rejected(self, client):
        response = client.post(
            URL, json=card_payload(difficulty="impossible"), headers=auth()
        )
        assert response.status_code == 422

    def test_missing_required_field_rejected(self, client):
        payload = card_payload()
        del payload["category"]
        response = client.post(URL, json=payload, headers=auth())
        assert response.status_code == 422


class TestUpdateCard:
    def test_requires_auth(self, client, db):
        card = make_card(db, question="Старый вопрос")
        response = client.put(f"{URL}/{card.id}", json={"question": "Новый"})
        assert response.status_code == 401

    def test_changes_only_given_fields(self, client, db):
        card = make_card(db, question="Старый вопрос", answer="Старый ответ")
        response = client.put(
            f"{URL}/{card.id}", json={"question": "Новый вопрос"}, headers=auth()
        )
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == "Новый вопрос"
        assert data["answer"] == "Старый ответ"

    def test_updates_tags(self, client, db):
        card = make_card(db, tags=json.dumps(["old"]))
        response = client.put(
            f"{URL}/{card.id}", json={"tags": ["new", "tags"]}, headers=auth()
        )
        assert response.json()["tags"] == ["new", "tags"]
        saved = client.get(f"/api/cards/{card.id}").json()
        assert saved["tags"] == ["new", "tags"]

    def test_unknown_id_returns_404(self, client):
        response = client.put(f"{URL}/999", json={"question": "x"}, headers=auth())
        assert response.status_code == 404


class TestDeleteCard:
    def test_requires_auth(self, client, db):
        card = make_card(db)
        response = client.delete(f"{URL}/{card.id}")
        assert response.status_code == 401
        assert db.query(Card).count() == 1

    def test_deletes_card(self, client, db):
        card = make_card(db)
        response = client.delete(f"{URL}/{card.id}", headers=auth())
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        assert client.get(f"/api/cards/{card.id}").status_code == 404

    def test_unknown_id_returns_404(self, client):
        response = client.delete(f"{URL}/999", headers=auth())
        assert response.status_code == 404
