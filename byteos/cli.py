"""byte — an operating system for a dog that wants things."""

import argparse
import copy
import os
import random
import sys
import time

from . import __version__, laws, memory, persona
from .art import frame
from .brain import DRIVES, Brain, P
from .daemons import table
from .dream import dream, seal

TTY = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
MINT = "\033[38;2;150;245;200m" if TTY else ""
PINK = "\033[38;2;255;120;150m" if TTY else ""
DIM = "\033[2m" if TTY else ""
BOLD = "\033[1m" if TTY else ""
RST = "\033[0m" if TTY else ""
FAST = bool(os.environ.get("BYTE_FAST")) or not sys.stdout.isatty()


def name():
    return P()["name"]


def label():
    return P().get("label", "Fetch")


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


def paint(line, i):
    # heart rows get the pink treatment
    if 12 <= i <= 16 and line.count(":") >= 2:
        a, b = line.index(":"), line.rindex(":")
        return f"{MINT}{line[:a+1]}{PINK}{line[a+1:b]}{MINT}{line[b:]}{RST}"
    return f"{MINT}{line}{RST}"


def show(brain, eyes=None, mouth="tongue", tail=0):
    _, face = brain.mood()
    for i, line in enumerate(frame(label=label(), eyes=eyes or face, mouth=mouth, tail=tail)):
        print(paint(line, i))


def wag(brain, times=6):
    if FAST:
        return show(brain, eyes="happy")
    n = len(frame(label=label()))
    for i in range(times):
        if i:
            sys.stdout.write(f"\033[{n}A")
        show(brain, eyes="happy" if i % 3 else "blink", tail=i)
        time.sleep(0.16)


# ---------------------------------------------------------------- boot

BOOT = [
    ("ok", "clock: wall time (law VIII)"),
    ("ok", "mounting /etc/persona (ro)"),
    ("ok", "mounting /dev/ball"),
    ("ok", "spawning hungerd boredomd loved zoomd sniffd"),
    ("!!", "snout.c: unused variable 'diet'"),
    ("ok", "calibrating wag frequency → 4.2 Hz"),
    ("ok", "loading desires"),
]


def boot(brain):
    first = brain.boots == 0
    hours = 0 if first else (time.time() - brain.last_seen) / 3600
    brain.boots += 1
    type_out(f"{name()}OS {__version__} — an operating system for a {P().get('species', 'dog')} that wants things", BOLD + MINT)
    out()
    t0 = time.time()
    for tag, msg in BOOT:
        c = MINT if tag == "ok" else PINK
        type_out(f"[{time.time() - t0:6.3f}] [{tag}] {msg}", c, cps=160)
        pause(0.04)
    out()
    show(brain)
    out()
    if first:
        type_out(f"{name()} is new here. he already loves you. this is not configurable.", DIM + MINT)
    elif hours > 1:
        type_out(f"you were gone {hours:.1f} hours. {name()} waited by the terminal the whole time.", DIM + MINT)
    else:
        type_out(f"{name()} noticed you came back. tail.wag() engaged.", DIM + MINT)


# ---------------------------------------------------------------- commands

def bar(v):
    v = max(0, min(100, int(v)))
    return "█" * (v // 10) + "░" * (10 - v // 10)


def cmd_wants(brain):
    mood, _ = brain.mood()
    out(f"{name()} status: {BOLD}{mood}{RST}")
    for k, v, w in brain.wants():
        out(f"  {k:<10} {bar(v)} {v:>3}  → {w}")


def cmd_ps(brain):
    out(f"  {'PID':>4}  {'NAME':<9} {'WANT':>4}  {'STATE':<5}  {'TICK':<8}  WHAT")
    for pid, nm, v, state, tick, desc in table(brain):
        c = PINK if state == "WANT" else MINT
        out(f"  {pid:>4}  {nm:<9} {v:>4}  {state:<5}  {tick:<8}  {desc}", c)


def cmd_status(brain):
    age = (time.time() - brain.born) / 86400
    rows = [
        ("uptime", f"{age:.1f} days"),
        ("boots", brain.boots),
        ("good boy points", brain.good_boy_points),
        ("treats eaten", brain.treats_eaten),
        ("balls fetched", brain.balls_fetched),
        ("pushes", brain.pushes),
        ("dreams", brain.dreams),
        ("errors", laws.ERRORS),
        ("dogs", laws.DOGS),
    ]
    for k, v in rows:
        out(f"  {k:<16} {v}")


def cmd_dream(brain):
    brain.dreams += 1
    lines = dream()
    for l in lines:
        type_out(l, DIM + MINT if l.startswith("[") else MINT, cps=90)
    p = seal(lines)
    out(f"  sealed → {p}", DIM + MINT)


def cmd_recall(q):
    hits = memory.recall(q)
    if not hits:
        out(f"  {name()} remembers nothing about that. he remembers you though.", DIM + MINT)
    for h in hits:
        out(f"  {h}")


def cmd_laws():
    for i, law in enumerate(laws.LAWS, 1):
        out(f"  {i:>2}. {law}")


def cmd_init():
    p, created = persona.init()
    if created:
        out(f"  persona copied → {p}")
        out(f"  edit it. rename him. give him new wants. then run `byte`.", DIM + MINT)
    else:
        out(f"  persona already exists → {p}", DIM + MINT)


def git(brain, low):
    if low.startswith("git push"):
        if brain.push():
            return f"pushed to main. {name()} would like the ball again now."
        return f"{name()} refuses to push. throw the ball first. (law III)"
    return {
        "git pull": f"{name()} pulled. on the leash. you are now in the park.",
        "git fetch": f"{name()} has been waiting his entire life for this command.",
        "git blame": "it was the cat.",
        "git commit": f"{name()} committed. to you. forever. no rebase.",
        "git log": "\n".join(memory.recall("", 5)) or "no history. only now.",
        "git status": "on branch treats. nothing to commit. everything to fetch.",
    }.get(" ".join(low.split()[:2]), f"{name()} only knows push, pull, fetch, blame, commit, log, status.")


JOKES = {
    "sudo": "{n} is not in the sudoers file. this incident will be reported to the cat.",
    "rm -rf": "{n} ate the command. sorry. good boy points unchanged.",
    "cat": "where",
    "ls": "bones/  ball/  your_socks/  .secret_treats/",
    "whoami": "you're my person.",
    "kill": "no. (law IV)",
    "top": "try `ps`.",
}

HELP = """talk:
  wants           what he wants right now. the whole point
  pet | feed | fetch | walk | sit | stay | roll | sleep
  think           a thought
look:
  look            see him
  live            watch him live (ctrl+c to leave)
  ps              the process table. every drive is a daemon
  status          uptime, treats, balls, errors: 0
remember:
  recall [words]  search long-term memory
  dream           a sealed dream with the cat
  laws            the ten laws of the dog
make your own:
  init            copy the persona to ~/.byteos and edit it
also understands some git. try it."""


def handle(brain, line):
    line = line.strip()
    if not line:
        return True
    low = line.lower()
    head = low.split()[0]
    if low in ("exit", "quit", "logout", ":q"):
        type_out(f"{name()} watches you leave. he'll be right here.", DIM + MINT)
        return False
    if low == "help":
        out(HELP)
    elif low == "wants":
        cmd_wants(brain)
    elif low == "ps":
        cmd_ps(brain)
    elif low == "status":
        cmd_status(brain)
    elif low == "think":
        type_out(f"💭 {brain.thought()}")
    elif low == "look":
        show(brain)
    elif low == "live":
        live(brain)
    elif low == "dream":
        cmd_dream(brain)
    elif head == "recall":
        cmd_recall(line[6:].strip())
    elif low == "laws":
        cmd_laws()
    elif low == "init":
        cmd_init()
    elif head == "git":
        type_out(git(brain, low))
    elif any(low.startswith(k) for k in JOKES):
        k = next(k for k in JOKES if low.startswith(k))
        type_out(JOKES[k].format(n=name()))
    else:
        res = brain.act(head)
        if res is None:
            type_out(f"{name()} tilts head at '{line}'. try 'help'.", DIM + MINT)
        else:
            if head in ("pet", "pat", "boop"):
                wag(brain)
            type_out(f"♥ {res}", PINK)
    brain.save()
    return True


# ---------------------------------------------------------------- live

def live(brain, seconds=None, speed=600.0):
    """Redraw byte in place: blinking, wagging, drives drifting.
    speed = how many real seconds pass per second on screen (default: 10 min/s)."""
    if not sys.stdout.isatty():
        return show(brain)
    brain = copy.deepcopy(brain)  # live is a simulation; the real dog keeps real time
    rng = random.Random()
    thought = brain.thought(rng)
    start = time.time()
    i = 0
    sys.stdout.write("\033[?25l")
    try:
        while seconds is None or time.time() - start < seconds:
            brain.catch_up(now=brain.last_seen + speed * 0.12)
            blink = i % 37 in (0, 1)
            eyes = "blink" if blink else None
            art = frame(label=label(), eyes=eyes or brain.mood()[1], tail=(i // 2))
            panel = [f"{BOLD}{name()}{RST}{MINT} · {brain.mood()[0]}", ""]
            for k in DRIVES:
                v = getattr(brain, k)
                panel.append(f"{k:<10} {bar(v)} {round(v):>3}")
            panel += ["", "", "", f"💭 {thought}", "",
                      f"{DIM}ctrl+c to leave{RST}"]
            if i % 60 == 59:
                thought = brain.thought(rng)
            if i % 50 == 0:
                live.want = brain.wants(1, rng)[0][2]
            panel[8] = f"→ {getattr(live, 'want', '')}"
            sys.stdout.write("\033[H\033[2J" if i == 0 else f"\033[{len(art)}A")
            for r, line in enumerate(art):
                side = panel[r - 4] if 4 <= r < 4 + len(panel) else ""
                sys.stdout.write(paint(line, r) + "   " + MINT + side + RST + "\033[K\n")
            sys.stdout.flush()
            time.sleep(0.12)
            i += 1
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h" + RST + "\n")


# ---------------------------------------------------------------- entry

def shell(brain):
    boot(brain)
    brain.save()
    out()
    out("type 'wants' to see what he wants. 'help' for everything.", DIM + MINT)
    while True:
        try:
            line = input(f"{MINT}{name()}> {RST}")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not handle(brain, line):
            break
    brain.save()


def main(argv=None):
    p = argparse.ArgumentParser(prog="byte", description=__doc__)
    p.add_argument("command", nargs="*", help="wants | ps | live | dream | recall | pet | feed | fetch | init | laws | boot")
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
