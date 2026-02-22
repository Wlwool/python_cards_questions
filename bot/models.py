from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    code_example = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    tags = Column(Text, default="[]")
    difficulty = Column(String(10), nullable=False, default="normal")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
