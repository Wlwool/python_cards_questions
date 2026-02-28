import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from cards import format_card, get_next_cards, get_random_card
from config import settings
from database import SessionLocal
from state import load_last_id, save_last_id

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

bot = Bot(token=settings.bot_token)
dp = Dispatcher()
router = Router()
dp.include_router(router)


async def send_card_messages(chat_id: int, card) -> None:
    """Отправляет карточку одному пользователю, разбивая на части если нужно."""
    parts = format_card(card)
    for part in parts:
        await bot.send_message(chat_id, part, parse_mode="HTML")


async def send_scheduled_cards() -> None:
    """Отправляет серию карточек по расписанию всем пользователям."""
    db = SessionLocal()
    try:
        last_id = load_last_id()
        cards = get_next_cards(db, settings.cards_per_session, last_id)
        if not cards:
            log.warning("Нет карточек в БД")
            return
        last_sent_id = last_id  # сохранение на случай ошибок

        for chat_id in settings.admin_ids:
            for i, card in enumerate(cards):
                try:
                    await send_card_messages(chat_id, card)
                    last_sent_id = card.id
                except Exception as e:
                    log.error(
                        f"Ошибка при отпарвке карточки id={card.id} в чат {chat_id}: {e}"
                    )
                    save_last_id(last_sent_id)
                # пауза между карточками кроме последней
                if i < len(cards) - 1:
                    await asyncio.sleep(settings.pause_between_cards_seconds)


        # сохраняет id последней отправленной карточки
        save_last_id(cards[-1].id)
        log.info(f"Отправлено {len(cards)} карточек, последний id: {cards[-1].id}")
    finally:
        db.close()


@router.message(Command("card"))
async def cmd_card(message: Message) -> None:
    if message.from_user.id not in settings.admin_ids:
        return

    db = SessionLocal()
    try:
        card = get_random_card(db)
        if not card:
            await message.answer("База карточек пуста.")
            return
        await send_card_messages(message.chat.id, card)
    finally:
        db.close()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    if message.from_user.id not in settings.admin_ids:
        return
    await message.answer(
        "Бот для изучения Python карточек\\.\n\n"
        "/card — случайная карточка прямо сейчас",
    )


async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_scheduled_cards,
        trigger="interval",
        hours=settings.schedule_interval_hours,
    )
    scheduler.add_job(send_scheduled_cards, trigger="date")
    scheduler.start()
    log.info(f"Scheduler запущен, интервал: {settings.schedule_interval_hours}ч")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
