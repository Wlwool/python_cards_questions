import json
import os

STATE_FILE = "data/bot_state.json"


def load_last_id() -> int:
    if not os.path.exists(STATE_FILE):
        return 0
    with open(STATE_FILE) as f:
        return json.load(f).get("last_id", 0)


def save_last_id(last_id: int):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"last_id": last_id}, f)
