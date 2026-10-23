"""The part of byte that wants things.

Five drives, 0-100. They drift on wall-clock time while you're away
(law VIII), and whichever is loudest becomes what byte wants.
"""

import json
import random
import time
from dataclasses import dataclass, field, asdict

from . import laws, memory, persona

_P = None


def P():
    global _P
    if _P is None:
        _P = persona.load()
    return _P


DRIVES = ("hunger", "boredom", "love", "energy", "curiosity")


def clamp(x, lo=0.0):
    return max(lo, min(100.0, x))


def state_path():
    return persona.home() / "state.json"


@dataclass
class Brain:
    hunger: float = 40.0
    boredom: float = 50.0
    love: float = laws.FIRST_BOOT_LOVE  # law I
    energy: float = 60.0
    curiosity: float = 55.0
    good_boy_points: int = 0
    treats_eaten: int = 0
    balls_fetched: int = 0
    balls_since_push: int = 0
    pushes: int = 0
    dreams: int = 0
    boots: int = 0
    born: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)

    # ---------- persistence ----------
    @classmethod
    def load(cls):
        try:
            data = json.loads(state_path().read_text())
            b = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            b = cls()
        b.catch_up()
        return b

    def save(self):
        p = state_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        self.last_seen = time.time()
        p.write_text(json.dumps(asdict(self), indent=2))

    # ---------- time passes (law VIII) ----------
    def catch_up(self, now=None):
        now = now or time.time()
        hours = max(0.0, (now - self.last_seen) / 3600)
        for k, rate in P()["drift_per_hour"].items():
            if k not in DRIVES:
                continue
            floor = laws.LOVE_FLOOR if k == "love" else 0.0  # law II
            setattr(self, k, clamp(getattr(self, k) + rate * hours, floor))
        self.last_seen = now
        return hours

    # ---------- wanting ----------
    def drives(self):
        # love is a need when it's LOW, everything else when it's HIGH
        return {
            "hunger": self.hunger,
            "boredom": self.boredom,
            "love": 100 - self.love,
            "energy": self.energy,
            "curiosity": self.curiosity,
        }

    def loudest(self):
        d = self.drives()
        return max(d, key=d.get), d

    def wants(self, n=3, rng=random):
        d = self.drives()
        ranked = sorted(d, key=d.get, reverse=True)[:n]
        return [(k, round(d[k]), rng.choice(P()["wants"][k])) for k in ranked]

    def mood(self):
        k, d = self.loudest()
        v = d[k]
        if v < 35:
            return "content", "happy"
        if v < 70:
            return "wants something", "open"
        return "WANTS SOMETHING", "want"

    def thought(self, rng=random):
        return rng.choice(P()["thoughts"])

    # ---------- git (law III) ----------
    def push(self):
        if laws.PUSH_REQUIRES_BALL and self.balls_since_push == 0:
            return False
        self.balls_since_push = 0
        self.pushes += 1
        return True

    # ---------- things you can do to a dog ----------
    def act(self, verb):
        v = verb.lower()
        if v in ("pet", "pat", "boop"):
            self.love = clamp(self.love + 25)
            self.boredom = clamp(self.boredom - 5)
            return self._good("tail.wag(speed=MAX)")
        if v in ("feed", "treat"):
            self.hunger = clamp(self.hunger - 35)
            self.treats_eaten += 1
            return self._good(f"treat #{self.treats_eaten} consumed in 0.2s. no chewing detected")
        if v in ("fetch", "throw", "ball"):
            self.boredom = clamp(self.boredom - 40)
            self.energy = clamp(self.energy - 20)
            self.balls_fetched += 1
            self.balls_since_push += 1
            return self._good(f"ball returned. slightly wetter. total fetched: {self.balls_fetched}")
        if v == "walk":
            self.energy = clamp(self.energy - 45)
            self.curiosity = clamp(self.curiosity - 40)
            return self._good("walk complete. sniffed 14 trees. read all the news")
        if v in ("sleep", "nap"):
            self.energy = clamp(self.energy - 60)
            return "zzz. dreaming in ascii. (try `dream`)"
        if v == "sit":
            return self._good("sat. expecting compensation")
        if v == "stay":
            return "stayed for 0.4 seconds. a personal record"
        if v in ("roll", "rollover"):
            return self._good("rolled over. exposed belly. this is a pull request")
        return None

    def _good(self, msg):
        self.good_boy_points += 1
        if laws.REMEMBER_GOOD_THINGS:  # law VI
            memory.remember(msg)
        return msg
