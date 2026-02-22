import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_token, verify_token
from app.config import settings
from app.database import get_db
from app.models import Card
from app.schemas import CardCreate, CardResponse, CardUpdate, LoginRequest, TokenResponse

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    if body.password != settings.admin_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong password")
    return TokenResponse(access_token=create_token())


@router.post("/cards", response_model=CardResponse, dependencies=[Depends(verify_token)])
def create_card(body: CardCreate, db: Session = Depends(get_db)):
    card = Card(
        question=body.question,
        answer=body.answer,
        code_example=body.code_example,
        category=body.category,
        tags=json.dumps(body.tags, ensure_ascii=False),
        difficulty=body.difficulty,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@router.put("/cards/{card_id}", response_model=CardResponse, dependencies=[Depends(verify_token)])
def update_card(card_id: int, body: CardUpdate, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        if field == "tags":
            setattr(card, field, json.dumps(value, ensure_ascii=False))
        else:
            setattr(card, field, value)

    db.commit()
    db.refresh(card)
    return card


@router.delete("/cards/{card_id}", dependencies=[Depends(verify_token)])
def delete_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    db.delete(card)
    db.commit()
    return {"ok": True}
