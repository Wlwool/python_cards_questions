import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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
