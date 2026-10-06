import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import state


@pytest.fixture(autouse=True)
def state_file(tmp_path, monkeypatch):
    """Каждый тест работает со своим файлом состояния во временном каталоге."""
    path = str(tmp_path / "data" / "bot_state.json")
    monkeypatch.setattr(state, "STATE_FILE", path)
    return path


class TestLoadLastId:
    def test_missing_file_returns_zero(self):
        assert state.load_last_id() == 0

    @pytest.mark.parametrize(
        "content",
        ["", "{broken", "[1, 2]", '{"last_id": "abc"}', "null"],
    )
    def test_invalid_file_returns_zero(self, state_file, content):
        os.makedirs(os.path.dirname(state_file))
        with open(state_file, "w") as f:
            f.write(content)
        assert state.load_last_id() == 0


class TestSaveLastId:
    def test_save_then_load(self):
        state.save_last_id(7)
        assert state.load_last_id() == 7

    def test_creates_directory(self, state_file):
        state.save_last_id(1)
        assert os.path.exists(state_file)

    def test_failed_write_keeps_previous_state(self, state_file, monkeypatch):
        state.save_last_id(5)

        def boom(*args, **kwargs):
            raise OSError("диск переполнен")

        monkeypatch.setattr(state.json, "dump", boom)
        with pytest.raises(OSError):
            state.save_last_id(9)

        assert state.load_last_id() == 5
        assert not os.path.exists(state_file + ".tmp")
