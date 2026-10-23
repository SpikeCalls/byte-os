"""The part of Byte that wants things.

Five drives, 0-100. They drift while you're away (real wall-clock time),
and whichever is loudest becomes what Byte wants. That's the whole OS.
"""

import json
import os
import random
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

HOME = Path(os.environ.get("BYTE_HOME", Path.home() / ".byteos"))
STATE = HOME / "state.json"
MEMORY = HOME / "memory.log"

# points per hour, how each drive drifts while nobody is looking
DRIFT = {
    "hunger": +9.0,
    "boredom": +12.0,
    "love": -7.0,
    "energy": +6.0,
    "curiosity": +10.0,
}

WANTS = {
    "hunger": [
        "a treat. specifically the one in your left pocket",
        "dinner. it is not dinner time. it is always dinner time",
        "whatever you are eating",
    ],
    "boredom": [
        "the ball. THE ball. not a different ball",
        "to fetch literally anything",
        "you to stop typing and throw something",
    ],
    "love": [
        "pets. behind the left ear. you know the spot",
        "to sit on your feet while you work",
        "eye contact for an uncomfortable amount of time",
    ],
    "energy": [
        "zoomies. immediately. around the kitchen island",
        "a walk. the long one. past the tree with the news",
        "to run in a circle for reasons that are classified",
    ],
    "curiosity": [
        "to sniff the new commit",
        "to know what's inside the fridge, on a philosophical level",
        "to read the mailman's source code",
    ],
}

THOUGHTS = [
    "is the ball thinking about me too",
    "every PR is a stick someone threw",
    "main is just a branch that got petted more",
    "i have mass-assigned every issue to myself. they are mine now",
    "the cat says tests are a social construct",
    "i do not understand money. i understand ball",
    "git fetch is my favorite command and i have never once run it",
    "i was trained on 40TB of fetch logs and i still don't know where the ball is",
    "rm -rf / sounds like a sneeze",
    "if you leave the terminal open i will wait by it",
    "sudo means 'please' right",
    "the vacuum is a hostile process",
    "i dream in ascii",
    "every reboot i forget everything except you",
]


def clamp(x):
    return max(0.0, min(100.0, x))


@dataclass
class Brain:
    hunger: float = 40.0
    boredom: float = 50.0
    love: float = 70.0
    energy: float = 60.0
    curiosity: float = 55.0
    good_boy_points: int = 0
    treats_eaten: int = 0
    balls_fetched: int = 0
    boots: int = 0
    born: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)

    # ---------- persistence ----------
    @classmethod
    def load(cls):
        try:
            data = json.loads(STATE.read_text())
            b = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            b = cls()
        b.catch_up()
        return b

    def save(self):
        HOME.mkdir(parents=True, exist_ok=True)
        self.last_seen = time.time()
        STATE.write_text(json.dumps(asdict(self), indent=2))

    def remember(self, line):
        HOME.mkdir(parents=True, exist_ok=True)
        with MEMORY.open("a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {line}\n")

    # ---------- time passes ----------
    def catch_up(self, now=None):
        now = now or time.time()
        hours = max(0.0, (now - self.last_seen) / 3600)
        for k, rate in DRIFT.items():
            setattr(self, k, clamp(getattr(self, k) + rate * hours))
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
        return [(k, round(d[k]), rng.choice(WANTS[k])) for k in ranked]

    def mood(self):
        k, d = self.loudest()
        v = d[k]
        if v < 35:
            return "content", "happy"
        if v < 70:
            return "wants something", "open"
        return "WANTS SOMETHING", "want"

    def thought(self, rng=random):
        return rng.choice(THOUGHTS)

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
            return self._good(f"ball returned. slightly wetter. total fetched: {self.balls_fetched}")
        if v in ("walk",):
            self.energy = clamp(self.energy - 45)
            self.curiosity = clamp(self.curiosity - 40)
            return self._good("walk complete. sniffed 14 trees. read all the news")
        if v in ("sleep", "nap"):
            self.energy = clamp(self.energy - 60)
            return "zzz. dreaming in ascii"
        if v in ("sit",):
            return self._good("sat. expecting compensation")
        if v in ("stay",):
            return "stayed for 0.4 seconds. a personal record"
        if v in ("roll", "rollover"):
            return self._good("rolled over. exposed belly. this is a pull request")
        return None

    def _good(self, msg):
        self.good_boy_points += 1
        self.remember(msg)
        return msg
