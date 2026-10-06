import pytest

import config


class TestRequire:
    def test_returns_value(self, monkeypatch):
        monkeypatch.setenv("TEST_REQUIRED_VAR", "abc")
        assert config._require("TEST_REQUIRED_VAR") == "abc"

    def test_missing_variable_names_it(self, monkeypatch):
        monkeypatch.delenv("TEST_REQUIRED_VAR", raising=False)
        with pytest.raises(RuntimeError, match="TEST_REQUIRED_VAR"):
            config._require("TEST_REQUIRED_VAR")

    def test_empty_variable_rejected(self, monkeypatch):
        monkeypatch.setenv("TEST_REQUIRED_VAR", "  ")
        with pytest.raises(RuntimeError, match="TEST_REQUIRED_VAR"):
            config._require("TEST_REQUIRED_VAR")


class TestParseAdminIds:
    def test_valid_list(self):
        assert config._parse_admin_ids("1, 22,333") == [1, 22, 333]

    def test_skips_empty_items(self):
        assert config._parse_admin_ids("1,2,") == [1, 2]

    @pytest.mark.parametrize("raw", ["", " ", ",", "1,abc"])
    def test_invalid_rejected_with_name(self, raw):
        with pytest.raises(RuntimeError, match="ADMIN_IDS"):
            config._parse_admin_ids(raw)


class TestCheckDeliveryChannels:
    def test_telegram_only_ok(self):
        config._check_delivery_channels(True, "")

    def test_discord_only_ok(self):
        config._check_delivery_channels(False, "https://example.test/webhook")

    def test_both_ok(self):
        config._check_delivery_channels(True, "https://example.test/webhook")

    @pytest.mark.parametrize("url", ["", "   "])
    def test_no_channels_rejected(self, url):
        with pytest.raises(RuntimeError, match="DISCORD_WEBHOOK_URL"):
            config._check_delivery_channels(False, url)
