"""byte — an operating system for a dog that wants things."""

import argparse
import os
import random
import sys
import time

from . import __version__
from .art import frame
from .brain import Brain

TTY = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
MINT = "\033[38;2;150;245;200m" if TTY else ""
PINK = "\033[38;2;255;120;150m" if TTY else ""
DIM = "\033[2m" if TTY else ""
BOLD = "\033[1m" if TTY else ""
RST = "\033[0m" if TTY else ""
FAST = os.environ.get("BYTE_FAST") or not TTY


def out(s="", c=MINT):
    print(f"{c}{s}{RST}")


def type_out(s, c=MINT, cps=60):
    if FAST:
        return out(s, c)
    sys.stdout.write(c)
    for ch in s:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(1 / cps)
    sys.stdout.write(RST + "\n")


def pause(s):
    if not FAST:
        time.sleep(s)


def draw(lines, label="Fetch"):
    for i, line in enumerate(lines):
        # heart rows get the pink treatment
        if 12 <= i <= 16 and ":" in line:
            a, b = line.index(":"), line.rindex(":")
            print(f"{MINT}{line[:a+1]}{PINK}{line[a+1:b]}{MINT}{line[b:]}{RST}")
        else:
            out(line)


def show(brain, label="Fetch", eyes=None, mouth="tongue", tail=0):
    _, face = brain.mood()
    draw(frame(label=label, eyes=eyes or face, mouth=mouth, tail=tail), label)


def wag(brain, label="Fetch", times=6):
    if FAST:
        return show(brain, label, eyes="happy")
    n = len(frame(label=label))
    for i in range(times):
        if i:
            sys.stdout.write(f"\033[{n}A")
        show(brain, label, eyes="happy" if i % 3 else "blink", tail=i)
        time.sleep(0.16)


BOOT = [
    ("ok", "resolving dependencies · 1 good boy found"),
    ("ok", "mounting /dev/ball"),
    ("ok", "loading bones.json"),
    ("ok", "compiling tail.rs"),
    ("!!", "snout.c: unused variable 'diet'"),
    ("ok", "calibrating wag frequency → 4.2 Hz"),
    ("ok", "loading desires"),
]


def boot(brain):
    hours = brain.boots and (time.time() - brain.last_seen) / 3600
    brain.boots += 1
    type_out(f"byteOS {__version__} — an operating system for a dog that wants things", BOLD + MINT)
    out()
    for tag, msg in BOOT:
        c = MINT if tag == "ok" else PINK
        type_out(f"[{tag}] {msg}", c, cps=140)
        pause(0.05)
    out()
    show(brain)
    out()
    if brain.boots == 1:
        type_out("byte is new here. he already loves you. this is not configurable.", DIM + MINT)
    elif hours and hours > 1:
        type_out(f"you were gone {hours:.1f} hours. byte waited by the terminal the whole time.", DIM + MINT)
    else:
        type_out("byte noticed you came back. tail.wag() engaged.", DIM + MINT)


def cmd_wants(brain):
    mood, _ = brain.mood()
    out(f"byte status: {BOLD}{mood}{RST}")
    for k, v, w in brain.wants():
        bar = "█" * (v // 10) + "░" * (10 - v // 10)
        out(f"  {k:<10} {bar} {v:>3}  → {w}")


def cmd_status(brain):
    age = (time.time() - brain.born) / 86400
    rows = [
        ("uptime", f"{age:.1f} days"),
        ("boots", brain.boots),
        ("good boy points", brain.good_boy_points),
        ("treats eaten", brain.treats_eaten),
        ("balls fetched", brain.balls_fetched),
        ("errors", 0),
        ("dogs", 1),
    ]
    for k, v in rows:
        out(f"  {k:<16} {v}")


JOKES = {
    "git push": "byte refuses to push. throw the ball first.",
    "git pull": "byte pulled. on the leash. you are now in the park.",
    "git fetch": "byte has been waiting his entire life for this command.",
    "git blame": "it was the cat.",
    "git commit": "byte committed. to you. forever. no rebase.",
    "sudo": "byte is not in the sudoers file. this incident will be reported to the cat.",
    "rm -rf": "byte ate the command. sorry. good boy points unchanged.",
    "cat": "where",
    "ls": "bones/  ball/  your_socks/  .secret_treats/",
    "whoami": "you're my person.",
    "top": "PID 1  byte  CPU 100%  wanting",
    "kill": "no.",
    "exit": None,
}

HELP = """commands:
  wants        what byte wants right now (the whole point)
  pet          pet byte
  feed | treat give a treat
  fetch        throw the ball
  walk         go outside
  sit | stay | roll
  sleep        nap
  think        byte shares a thought
  status       uptime, treats, balls
  look         see byte
  help | exit
also understands some git. try it."""


def handle(brain, line):
    line = line.strip()
    if not line:
        return True
    low = line.lower()
    if low in ("exit", "quit", "logout", ":q"):
        type_out("byte watches you leave. he'll be right here.", DIM + MINT)
        return False
    if low == "help":
        out(HELP)
    elif low == "wants":
        cmd_wants(brain)
    elif low == "status":
        cmd_status(brain)
    elif low == "think":
        type_out(f"💭 {brain.thought()}")
    elif low == "look":
        show(brain)
    else:
        for k, v in JOKES.items():
            if low.startswith(k):
                type_out(v)
                break
        else:
            res = brain.act(low.split()[0])
            if res is None:
                type_out(f"byte tilts head at '{line}'. try 'help'.", DIM + MINT)
            else:
                if low.split()[0] in ("pet", "pat", "boop"):
                    wag(brain)
                type_out(f"♥ {res}", PINK)
    brain.save()
    return True


def shell(brain):
    boot(brain)
    brain.save()
    out()
    out("type 'wants' to see what byte wants. 'help' for everything.", DIM + MINT)
    while True:
        try:
            line = input(f"{MINT}byte> {RST}")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not handle(brain, line):
            break
    brain.save()


def main(argv=None):
    p = argparse.ArgumentParser(prog="byte", description=__doc__)
    p.add_argument("command", nargs="*", help="wants | pet | feed | fetch | walk | think | status | look | boot")
    p.add_argument("--version", action="version", version=f"byteOS {__version__}")
    a = p.parse_args(argv)
    brain = Brain.load()
    if not a.command:
        return shell(brain)
    cmd = " ".join(a.command)
    if cmd == "boot":
        boot(brain)
        brain.save()
        return
    handle(brain, cmd)


if __name__ == "__main__":
    main()
