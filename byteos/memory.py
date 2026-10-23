"""Long-term memory. An append-only log, recalled by word overlap.
No embeddings. Dogs don't do vectors."""

import re
import time

from .persona import home

STOP = {"the", "a", "an", "to", "of", "and", "is", "in", "it", "i", "you", "my", "me"}


def path():
    return home() / "memory.log"


def remember(line):
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {line}\n")


def lines():
    try:
        return path().read_text().splitlines()
    except FileNotFoundError:
        return []


def words(s):
    return {w for w in re.findall(r"[a-z']+", s.lower()) if w not in STOP}


def recall(query="", n=5):
    log = lines()
    if not query:
        return log[-n:]
    q = words(query)
    scored = [(len(q & words(l)), i, l) for i, l in enumerate(log)]
    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda s: (-s[0], -s[1]))
    return [l for _, _, l in scored[:n]]
