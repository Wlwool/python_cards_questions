import json
import logging
import os

log = logging.getLogger(__name__)

STATE_FILE = "data/bot_state.json"


def load_last_id() -> int:
    """Возвращает id последней отправленной карточки.
    Если файла нет или он повреждён, возвращает 0 (рассылка начнётся сначала).
    """
    if not os.path.exists(STATE_FILE):
        return 0
    try:
        with open(STATE_FILE) as f:
            data = json.load(f)
        last_id = data["last_id"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        log.warning(f"Файл состояния {STATE_FILE} не прочитан ({e!r}), начинаю с 0")
        return 0
    if not isinstance(last_id, int):
        log.warning(f"В {STATE_FILE} last_id не число ({last_id!r}), начинаю с 0")
        return 0
    return last_id


def save_last_id(last_id: int) -> None:
    """Записывает состояние атомарно: во временный файл, затем os.replace."""
    os.makedirs(os.path.dirname(STATE_FILE) or ".", exist_ok=True)
    tmp_path = f"{STATE_FILE}.tmp"
    try:
        with open(tmp_path, "w") as f:
            json.dump({"last_id": last_id}, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, STATE_FILE)
    except BaseException:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
