from datetime import datetime, timedelta, timezone

import jwt

from app.auth import create_token
from app.config import settings

CARD_URL = "/api/admin/cards/1"


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def make_jwt(sub="admin", key=None, expires_in=timedelta(hours=1)) -> str:
    payload = {"sub": sub, "exp": datetime.now(timezone.utc) + expires_in}
    return jwt.encode(payload, key or settings.secret_key, algorithm="HS256")


class TestLogin:
    def test_correct_password_returns_token(self, client):
        response = client.post(
            "/api/admin/login", json={"password": settings.admin_password}
        )
        assert response.status_code == 200
        assert response.json()["access_token"]

    def test_wrong_password_rejected(self, client):
        response = client.post("/api/admin/login", json={"password": "wrong"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Wrong password"


class TestVerifyToken:
    def test_no_token_rejected(self, client):
        assert client.delete(CARD_URL).status_code == 401

    def test_garbage_token_rejected(self, client):
        response = client.delete(CARD_URL, headers=auth_headers("garbage"))
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"

    def test_expired_token_rejected(self, client):
        token = make_jwt(expires_in=timedelta(hours=-1))
        response = client.delete(CARD_URL, headers=auth_headers(token))
        assert response.status_code == 401
        assert response.json()["detail"] == "Token expired"

    def test_token_signed_with_other_key_rejected(self, client):
        token = make_jwt(key="some-other-secret-key-with-32-plus-characters")
        response = client.delete(CARD_URL, headers=auth_headers(token))
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"

    def test_token_with_wrong_subject_rejected(self, client):
        token = make_jwt(sub="user")
        response = client.delete(CARD_URL, headers=auth_headers(token))
        assert response.status_code == 401

    def test_valid_token_passes_auth(self, client):
        response = client.delete(CARD_URL, headers=auth_headers(create_token()))
        # авторизация пройдена, карточки с id=1 в пустой БД нет
        assert response.status_code == 404
