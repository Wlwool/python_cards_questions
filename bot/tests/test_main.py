import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture(scope="module")
def main_module():
    """Импортирует main с подменённым aiogram.Bot: токен не проверяется, сети нет."""
    with patch("aiogram.Bot"):
        import main
    return main


def make_card(card_id: int) -> SimpleNamespace:
    return SimpleNamespace(id=card_id)


class Env:
    """Подменяет всё внешнее в main и записывает, что произошло."""

    def __init__(self, main, monkeypatch) -> None:
        self.main = main
        self.monkeypatch = monkeypatch
        self.saved: list[int] = []
        self.retries: list[int] = []
        self.sleeps: list[float] = []
        self.next_calls: list[int] = []
        self.discord = MagicMock()
        self.discord.send = AsyncMock(return_value=True)
        self.tg = AsyncMock()

        async def fake_sleep(delay):
            self.sleeps.append(delay)

        monkeypatch.setattr(main, "send_lock", asyncio.Lock())
        monkeypatch.setattr(main, "SessionLocal", MagicMock())
        monkeypatch.setattr(main, "load_last_id", lambda: 0)
        monkeypatch.setattr(main, "save_last_id", self.saved.append)
        monkeypatch.setattr(main, "format_card_discord", lambda card: ["текст"])
        monkeypatch.setattr(main, "_send_tg_to_all", self.tg)
        monkeypatch.setattr(
            main, "_schedule_retry", lambda scheduler, discord: self.retries.append(1)
        )
        monkeypatch.setattr(main.settings, "pause_between_cards_seconds", 7)
        monkeypatch.setattr(main.settings, "telegram_enabled", True)
        monkeypatch.setattr(main.asyncio, "sleep", fake_sleep)

    def use_cards(self, cards) -> None:
        def fake_get_next_cards(db, count, last_id):
            self.next_calls.append(last_id)
            return cards

        self.monkeypatch.setattr(self.main, "get_next_cards", fake_get_next_cards)

    async def session(self, cards) -> None:
        self.use_cards(cards)
        await self.main.send_scheduled_cards(MagicMock(), self.discord)

    def run(self, cards) -> None:
        asyncio.run(self.session(cards))


@pytest.fixture
def env(main_module, monkeypatch) -> Env:
    return Env(main_module, monkeypatch)


class TestSendScheduledCards:
    def test_skips_when_session_already_running(self, env):
        async def scenario():
            async with env.main.send_lock:
                await env.session([make_card(1)])

        asyncio.run(scenario())
        assert env.next_calls == []
        assert env.saved == []

    def test_no_cards_does_nothing(self, env):
        env.run([])
        assert env.saved == []
        assert env.discord.send.await_count == 0
        assert env.tg.await_count == 0

    def test_both_channels_send_every_card_and_save_progress(self, env):
        env.run([make_card(1), make_card(2), make_card(3)])
        assert env.saved == [1, 2, 3]
        assert env.discord.send.await_count == 3
        assert env.tg.await_count == 3
        assert env.sleeps == [7, 7]
        assert env.retries == []

    def test_discord_only_mode_skips_telegram(self, env):
        env.monkeypatch.setattr(env.main.settings, "telegram_enabled", False)
        env.run([make_card(1), make_card(2)])
        assert env.saved == [1, 2]
        assert env.discord.send.await_count == 2
        assert env.tg.await_count == 0

    def test_telegram_failure_saves_progress_and_schedules_retry(self, env):
        env.tg.side_effect = [None, RuntimeError("down"), None]
        env.run([make_card(1), make_card(2), make_card(3)])
        assert env.saved == [1, 1]
        assert env.retries == [1]
        assert env.tg.await_count == 2
        assert env.discord.send.await_count == 2
        assert env.sleeps == [7]

    def test_telegram_failure_on_first_card_keeps_old_last_id(self, env):
        env.monkeypatch.setattr(env.main, "load_last_id", lambda: 5)
        env.tg.side_effect = RuntimeError("down")
        env.run([make_card(6), make_card(7)])
        assert env.saved == [5]
        assert env.retries == [1]
        assert env.sleeps == []

    @pytest.mark.parametrize(
        "discord_kwargs",
        [{"return_value": False}, {"side_effect": RuntimeError("boom")}],
    )
    def test_discord_failure_does_not_stop_session(self, env, discord_kwargs):
        env.discord.send = AsyncMock(**discord_kwargs)
        env.run([make_card(1), make_card(2)])
        assert env.saved == [1, 2]
        assert env.tg.await_count == 2
        assert env.retries == []

    def test_discord_only_failure_does_not_stop_session(self, env):
        env.monkeypatch.setattr(env.main.settings, "telegram_enabled", False)
        env.discord.send = AsyncMock(return_value=False)
        env.run([make_card(1), make_card(2)])
        assert env.saved == [1, 2]
