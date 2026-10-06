import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


class CardBase(BaseModel):
    question: str
    answer: str
    code_example: str | None = None
    category: str
    tags: list[str] = []
    difficulty: Literal["easy", "normal", "hard"] = "normal"


class CardCreate(CardBase):
    pass


class CardUpdate(BaseModel):
    question: str | None = None
    answer: str | None = None
    code_example: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    difficulty: Literal["easy", "normal", "hard"] | None = None

    # Optional здесь означает - поле можно не передавать.
    # Для code_example null оставлен допустимым.
    @field_validator("question", "answer", "category", "tags", "difficulty")
    @classmethod
    def reject_null(cls, v):
        if v is None:
            raise ValueError("must not be null")
        return v


class CardResponse(CardBase):
    id: int
    created_at: datetime
    updated_at: datetime

    # преобразует JSON строку тегов в список при чтении из БД
    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    model_config = {"from_attributes": True}


class CardListResponse(BaseModel):
    items: list[CardResponse]
    total: int
    page: int
    per_page: int


class LoginRequest(BaseModel):
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CategoriesResponse(BaseModel):
    categories: list[str]
