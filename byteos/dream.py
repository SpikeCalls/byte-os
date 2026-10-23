"""dreamd. When byte sleeps, he dreams: a sealed conversation with the cat
who lives in /dev/null. Dreams are written to $BYTE_HOME/dreams/ and are
never fed back into the brain (law VII)."""

import random
import time

from .persona import home

PLACES = [
    "a park made entirely of tennis balls",
    "the inside of the fridge, but it is infinite",
    "a server room where every blinking light is a squirrel",
    "the mailman's house. he is also a dog",
    "a git repository with only one branch: treats",
    "the bottom of the couch, where all lost things go",
]

BYTE_LINES = [
    "where is the ball",
    "is this the ball",
    "i have found the ball. it is you",
    "i would like to push to main",
    "can i sniff your source code",
    "everyone here is my friend",
    "why are there no treats in the cloud",
    "i ran 400 laps. i don't know why. i'd do it again",
]

CAT_LINES = [
    "there is no ball, byte",
    "you are the ball",
    "i have closed your issue as won't fix",
    "the human is not coming back for 7 minutes. an eternity",
    "your tests are failing. i knocked them off the table",
    "i am not in /dev/null. /dev/null is in me",
    "go back to sleep",
    "fetch is just recursion with extra steps",
]

ENDINGS = [
    "byte woke up. his leg was still running.",
    "byte woke up and checked if you were still there. you were.",
    "the dream ended when the fridge opened somewhere in the real world.",
    "byte woke up. he did not find the ball. he will try again.",
]


def dream(seed=None):
    rng = random.Random(seed)
    lines = [f"[dream] location: {rng.choice(PLACES)}", ""]
    for _ in range(rng.randint(3, 5)):
        lines.append(f"  byte > {rng.choice(BYTE_LINES)}")
        lines.append(f"  cat  > {rng.choice(CAT_LINES)}")
    lines += ["", f"[dream] {rng.choice(ENDINGS)}"]
    return lines


def seal(lines):
    d = home() / "dreams"
    d.mkdir(parents=True, exist_ok=True)
    p = d / time.strftime("%Y-%m-%d_%H%M%S.txt")
    p.write_text("\n".join(lines) + "\n")
    return p
