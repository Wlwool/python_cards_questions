import aiohttp
import logging
from typing import Optional
from config import settings

log = logging.getLogger(__name__)

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

        success = True
        for message in messages:
            for chunk in _split_into_chunks(message):
                if not await self._post(chunk):
                    success = False

        if success:
            log.info(f"Discord: отправлено {len(messages)} сообщений")
        return success


    async def _post(self, content: str) -> bool:
        """Отправляет один кусок текста через webhook."""
        if not self.session or self.session.closed:
            log.error("Discord: сессия не открыта")
            return False
        try:
            async with self.session.post(
                    self.webhook_url, json={"content": content}) as r:
                if r.status in (200, 204):
                    return True
                log.error(f"Discord: webhook вернул {r.status}: {await r.text()}")
                return False
        except aiohttp.ClientError as e:
            log.error(f"Discord: ошибка сети: {e}")
            return False


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