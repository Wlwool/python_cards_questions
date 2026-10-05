import asyncio
import aiohttp
import logging
from typing import Optional
from config import settings

log = logging.getLogger(__name__)

_MAX_ATTEMPTS = 8
_NETWORK_RETRY_DELAY = 5   # пауза после сетевой ошибки, сек
_DEFAULT_RETRY_AFTER = 5   # пауза при 429, если Discord не сказал сколько, сек
_MAX_RETRY_AFTER = 60      # потолок паузы при 429, сек

class DiscordSender:
    def __init__(self, webhook_url: str) -> None:
        if not webhook_url:
            raise ValueError("Discord webhook URL не задан")
        self.webhook_url = webhook_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self) -> None:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.discord_timeout)
        )

    async def stop(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def send(self, messages: list[str]) -> bool:
        if not messages:
            return True

        failed = 0
        total = 0
        for message in messages:
            for chunk in _split_into_chunks(message):
                total += 1
                if not await self._post(chunk):
                    failed += 1

        if failed:
            log.error(f"Discord: не отправлено {failed}/{total} чанков")
            return False

        log.info(f"Discord: отправлено {total} чанков ({len(messages)} сообщений)")
        return True

    async def _post(self, content: str) -> bool:
        """Отправляет один кусок текста через webhook (не более _MAX_ATTEMPTS попыток)."""
        if not self.session or self.session.closed:
            log.error("Discord: сессия не открыта")
            return False

        for attempt in range(1, _MAX_ATTEMPTS + 1):
            delay: float = _NETWORK_RETRY_DELAY
            try:
                async with self.session.post(
                        self.webhook_url, json={"content": content}) as r:
                    if r.status in (200, 204):
                        return True
                    if r.status != 429:
                        log.error(f"Discord: webhook вернул {r.status}: {await r.text()}")
                        return False
                    delay = await _read_retry_after(r)
                    log.warning(
                        f"Discord: rate limit, попытка {attempt}/{_MAX_ATTEMPTS}, "
                        f"повтор через {delay} сек")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                log.warning(
                    f"Discord: ошибка сети, попытка {attempt}/{_MAX_ATTEMPTS}: {e}")

            if attempt < _MAX_ATTEMPTS:
                await asyncio.sleep(delay)

        log.error(f"Discord: не удалось отправить за {_MAX_ATTEMPTS} попыток")
        return False

async def _read_retry_after(r) -> float:
    """Достаёт retry_after из тела ответа 429.
    При любой проблеме берёт значение по умолчанию.
    """
    try:
        value = float((await r.json()).get("retry_after", _DEFAULT_RETRY_AFTER))
    except (aiohttp.ClientError, ValueError, TypeError, AttributeError):
        return _DEFAULT_RETRY_AFTER
    return min(max(value, 0.0), _MAX_RETRY_AFTER)

def _split_into_chunks(text: str) -> list[str]:
    limit = settings.discord_max_length
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    lines = text.split("\n")
    current = ""
    for line in lines:
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) > limit:
            if current:
                chunks.append(current)
            while len(line) > limit:
                chunks.append(line[:limit])
                line = line[limit:]
            current = line
        else:
            current = candidate
    if current:
        chunks.append(current)

    return chunks
