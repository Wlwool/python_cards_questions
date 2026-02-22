import json
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import validates

from app.database import Base


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    code_example = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    # хранит список тегов как JSON строку: ["list", "dict"]
    tags = Column(Text, default="[]")
    difficulty = Column(String(10), nullable=False, default="normal")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    @validates("difficulty")
    def validate_difficulty(self, key, value):
        allowed = {"easy", "normal", "hard"}
        if value not in allowed:
            raise ValueError(f"difficulty must be one of {allowed}")
        return value

    @property
    def tags_list(self) -> list:
        return json.loads(self.tags or "[]")

    @tags_list.setter
    def tags_list(self, value: list):
        self.tags = json.dumps(value, ensure_ascii=False)
