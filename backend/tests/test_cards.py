import json
import pytest
from tests.conftest import make_card


class TestGetCards:
    def test_returns_all_cards(self, client, db):
        make_card(db, question="Вопрос 1")
        make_card(db, question="Вопрос 2")
        response = client.get("/api/cards")
        assert response.status_code == 200
        assert response.json()["total"] == 2

    def test_response_structure(self, client, db):
        make_card(db)
        data = client.get("/api/cards").json()
        card = data["items"][0]
        assert "id" in card
        assert "question" in card
        assert "answer" in card
        assert "category" in card
        assert "difficulty" in card
        assert "tags" in card

    def test_search_by_question(self, client, db):
        make_card(db, question="Что такое декоратор?")
        make_card(db, question="Как работает GIL?")
        response = client.get("/api/cards?search=декоратор")
        data = response.json()
        assert data["total"] == 1
        assert "декоратор" in data["items"][0]["question"]

    def test_search_by_answer(self, client, db):
        make_card(db, answer="GIL блокирует потоки")
        make_card(db, answer="Декоратор оборачивает функцию")
        response = client.get("/api/cards?search=GIL")
        assert response.json()["total"] == 1

    def test_search_case_insensitive(self, client, db):
        make_card(db, question="Что такое List Comprehension?")
        response = client.get("/api/cards?search=list comprehension")
        assert response.json()["total"] == 1

    def test_filter_by_category(self, client, db):
        make_card(db, category="Python")
        make_card(db, category="Django")
        response = client.get("/api/cards?category=Python")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category"] == "Python"

    def test_filter_by_difficulty_easy(self, client, db):
        make_card(db, difficulty="easy")
        make_card(db, difficulty="hard")
        response = client.get("/api/cards?difficulty=easy")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["difficulty"] == "easy"

    def test_filter_by_difficulty_hard(self, client, db):
        make_card(db, difficulty="hard")
        make_card(db, difficulty="normal")
        response = client.get("/api/cards?difficulty=hard")
        assert response.json()["total"] == 1

    def test_filter_by_tags(self, client, db):
        make_card(db, tags=json.dumps(["list", "basics"]))
        make_card(db, tags=json.dumps(["dict"]))
        response = client.get("/api/cards?tags=list")
        assert response.json()["total"] == 1

    def test_combined_filters(self, client, db):
        make_card(db, category="Python", difficulty="hard")
        make_card(db, category="Python", difficulty="easy")
        make_card(db, category="Django", difficulty="hard")
        response = client.get("/api/cards?category=Python&difficulty=hard")
        assert response.json()["total"] == 1

    def test_pagination_page_size(self, client, db):
        for i in range(5):
            make_card(db, question=f"Вопрос {i}")
        response = client.get("/api/cards?per_page=2")
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

    def test_pagination_second_page(self, client, db):
        for i in range(5):
            make_card(db, question=f"Вопрос {i}")
        response = client.get("/api/cards?per_page=2&page=2")
        assert len(response.json()["items"]) == 2

    def test_pagination_last_page(self, client, db):
        for i in range(5):
            make_card(db, question=f"Вопрос {i}")
        response = client.get("/api/cards?per_page=2&page=3")
        assert len(response.json()["items"]) == 1

    def test_search_no_results(self, client, db):
        make_card(db)
        response = client.get("/api/cards?search=несуществующийтекст")
        assert response.json()["total"] == 0

    def test_tags_returned_as_list(self, client, db):
        make_card(db, tags=json.dumps(["list", "dict"]))
        data = client.get("/api/cards").json()
        assert isinstance(data["items"][0]["tags"], list)


class TestGetCardById:
    def test_returns_card(self, client, db):
        card = make_card(db, question="Тестовый вопрос?")
        response = client.get(f"/api/cards/{card.id}")
        assert response.status_code == 200
        assert response.json()["question"] == "Тестовый вопрос?"

    def test_response_contains_all_fields(self, client, db):
        card = make_card(db, code_example="print('hi')", tags=json.dumps(["tag1"]))
        data = client.get(f"/api/cards/{card.id}").json()
        assert data["code_example"] == "print('hi')"
        assert data["tags"] == ["tag1"]

    def test_correct_id_returned(self, client, db):
        card = make_card(db)
        data = client.get(f"/api/cards/{card.id}").json()
        assert data["id"] == card.id


class TestGetCategories:
    def test_returns_categories(self, client, db):
        make_card(db, category="Python")
        make_card(db, category="Django")
        data = client.get("/api/cards/categories").json()
        assert "Python" in data["categories"]
        assert "Django" in data["categories"]

    def test_no_duplicates(self, client, db):
        make_card(db, category="Python")
        make_card(db, category="Python")
        data = client.get("/api/cards/categories").json()
        assert data["categories"].count("Python") == 1
