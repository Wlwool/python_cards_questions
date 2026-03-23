import asyncio
import logging

from datetime import datetime, timedelta, timezone
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
send_lock = asyncio.Lock()

RETRY_DELAYS = [30, 60, 90]


async def send_card_messages(chat_id: int, card) -> None:
    """Отправляет карточку одному пользователю, разбивая на части если нужно.
    Паузы при сетевой ошибке.
    """
    parts = format_card(card)
    for part in parts:
        for attempt, delay in enumerate(RETRY_DELAYS, start=1):
            try:
                await bot.send_message(chat_id, part, parse_mode="HTML")
                break
            except Exception as e:
                if attempt == len(RETRY_DELAYS):
                    raise
                log.warning(f"Попытка {attempt}/{len(RETRY_DELAYS)} не удалась"
                            f"(карточка id = {card.id}), чат {chat_id}: {e})."
                            f"Повтор через {delay} сек.")
                await asyncio.sleep(delay)


async def send_scheduled_cards(scheduler: AsyncIOScheduler) -> None:
    """Отправляет серию карточек по расписанию всем пользователям.
    При провале повторно отправляет через 15 минут.
    """
    if send_lock.locked():
        log.info("Сессия выполняется, пропускается запуск")
        return
    async with send_lock:
        db = SessionLocal()
        try:
            last_id = load_last_id()
            cards = get_next_cards(db, settings.cards_per_session, last_id)
            if not cards:
                log.warning("Нет карточек в БД")
                return

            last_sent_id = last_id

            for chat_id in settings.admin_ids:
                for i, card in enumerate(cards):
                    try:
                        await send_card_messages(chat_id, card)
                        last_sent_id = card.id
                    except Exception as e:
                        log.error(
                            f"Все попытки исчерпаны для карточки id={card.id} "
                            f"в чат {chat_id}: {e}. "
                            f"Повтор сессии через 15 минут."
                        )
                        save_last_id(last_sent_id)
                        _schedule_retry(scheduler)
                        return

                    if i < len(cards) - 1:
                        await asyncio.sleep(settings.pause_between_cards_seconds)

            save_last_id(cards[-1].id)
            log.info(f"Отправлено {len(cards)} карточек, последний id: {cards[-1].id}")
        finally:
            db.close()

def _schedule_retry(scheduler: AsyncIOScheduler) -> None:
    """Планирует повторную попытку отправки через 15 мин."""
    run_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    scheduler.add_job(
        send_scheduled_cards,
        trigger="date",
        run_date=run_at,
        args=[scheduler],
        id="retry_send",
        replace_existing=True,
    )
    log.info(f"Повторная попытка запланирована на {run_at.strftime('%H:%M:%S')}")


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
        "Бот для изучения Python по карточкам\\.\n\n"
        "/card — случайная карточка прямо сейчас",
    )


async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_scheduled_cards,
        trigger="interval",
        hours=settings.schedule_interval_hours,
        args=[scheduler],
    )
    scheduler.add_job(send_scheduled_cards, trigger="date", args=[scheduler])
    scheduler.start()
    log.info(f"Scheduler запущен, интервал: {settings.schedule_interval_hours}ч")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
