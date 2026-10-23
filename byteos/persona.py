"""Who the dog is. Mounted read-only from byteos/persona.json,
overridden by $BYTE_HOME/persona.json if you've run `byte init`."""

import json
import os
from pathlib import Path

PACKAGED = Path(__file__).with_name("persona.json")


def home():
    return Path(os.environ.get("BYTE_HOME", Path.home() / ".byteos"))


def load():
    base = json.loads(PACKAGED.read_text())
    user = home() / "persona.json"
    if user.exists():
        try:
            override = json.loads(user.read_text())
        except json.JSONDecodeError:
            override = {}
        for k, v in override.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                base[k] = {**base[k], **v}
            else:
                base[k] = v
    return base


def init():
    """Copy the default persona into $BYTE_HOME so you can make your own."""
    dst = home() / "persona.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return dst, False
    dst.write_text(PACKAGED.read_text())
    return dst, True
