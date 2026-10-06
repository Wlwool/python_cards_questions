import json
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Card
from app.schemas import CardListResponse, CardResponse, CategoriesResponse

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.get("", response_model=CardListResponse)
def get_cards(
    search: str | None = Query(None),
    category: str | None = Query(None),
    difficulty: Literal["easy", "normal", "hard"] | None = Query(None),
    tags: str | None = Query(None),  # через запятую: "list,dict"
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Card)

    if search:
        term = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.py_lower(Card.question).like(term),
                func.py_lower(Card.answer).like(term),
            )
        )

    if category:
        query = query.filter(Card.category == category)

    if difficulty:
        query = query.filter(Card.difficulty == difficulty)

    if tags:
        # фильтрует карточки содержащие хотя бы один из переданных тегов;
        # тег ищет вместе с кавычками ("set"), чтобы не находить "subset";
        # autoescape отключает спецсимволы LIKE (% и _) внутри тега
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            query = query.filter(
                or_(
                    *(
                        Card.tags.contains(
                            json.dumps(t, ensure_ascii=False), autoescape=True
                        )
                        for t in tag_list
                    )
                )
            )

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return CardListResponse(items=items, total=total, page=page, per_page=per_page)


@router.get("/categories", response_model=CategoriesResponse)
def get_categories(db: Session = Depends(get_db)):
    rows = db.query(Card.category).distinct().order_by(Card.category).all()
    return CategoriesResponse(categories=[r[0] for r in rows])


@router.get("/{card_id}", response_model=CardResponse)
def get_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card
