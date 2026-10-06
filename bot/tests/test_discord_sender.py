import asyncio
import logging
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from discord_sender import _MAX_ATTEMPTS, DiscordSender


class FakeResponse:
    """Подменяет ответ aiohttp: статус, json() и text()."""

    def __init__(self, status, body=None, json_error=False):
        self.status = status
        self._body = body if body is not None else {}
        self._json_error = json_error

    async def json(self):
        if self._json_error:
            raise ValueError("не JSON")
        return self._body

    async def text(self):
        return str(self._body)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class FakeSession:
    """Отдаёт ответы по очереди; последний повторяется бесконечно."""

    closed = False

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = 0

    def post(self, url, json):
        self.calls += 1
        if len(self._responses) > 1:
            return self._responses.pop(0)
        return self._responses[0]


def make_sender(responses) -> DiscordSender:
    sender = DiscordSender("https://example.test/webhook")
    sender.session = FakeSession(responses)
    return sender


@pytest.fixture
def sleeps(monkeypatch):
    """Не спит по-настоящему, записывает паузы. Лишние паузы означают бесконечный цикл."""
    calls = []

    async def fake_sleep(delay):
        calls.append(delay)
        if len(calls) > _MAX_ATTEMPTS + 5:
            raise RuntimeError("бесконечный повтор")

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    return calls


class TestPostRateLimit:
    def test_constant_rate_limit_gives_up(self, sleeps):
        sender = make_sender([FakeResponse(429, {"retry_after": 1})])
        assert asyncio.run(sender._post("x")) is False
        assert sender.session.calls == _MAX_ATTEMPTS

    def test_rate_limit_then_ok(self, sleeps):
        sender = make_sender([FakeResponse(429, {"retry_after": 2}), FakeResponse(204)])
        assert asyncio.run(sender._post("x")) is True
        assert sleeps == [2]

    def test_rate_limit_with_unreadable_body_uses_default_pause(self, sleeps):
        sender = make_sender([FakeResponse(429, json_error=True), FakeResponse(204)])
        assert asyncio.run(sender._post("x")) is True
        assert sleeps == [5]


class TestWithoutWebhook:
    def test_empty_url_does_not_raise(self):
        sender = DiscordSender("")
        assert sender.enabled is False

    def test_send_without_webhook_is_noop(self):
        sender = DiscordSender("")
        assert asyncio.run(sender.send(["текст"])) is True

    def test_start_without_webhook_warns_and_opens_no_session(self, caplog):
        sender = DiscordSender("")
        with caplog.at_level(logging.WARNING):
            asyncio.run(sender.start())
        assert sender.session is None
        assert "DISCORD_WEBHOOK_URL" in caplog.text
