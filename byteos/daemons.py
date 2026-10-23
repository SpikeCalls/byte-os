"""The process table. Each drive is a daemon that never exits."""

DAEMONS = [
    # pid, name,       drive,       tick,   what it does
    (1, "byte", None, "—", "the dog. PID 1. parent of everything"),
    (7, "hungerd", "hunger", "6m40s", "watches the bowl. +9/h"),
    (12, "boredomd", "boredom", "5m", "counts seconds since the last ball. +12/h"),
    (21, "loved", "love", "8m30s", "misses you. -7/h, floor 12 (law II)"),
    (33, "zoomd", "energy", "10m", "stores zoomies for later. +6/h"),
    (42, "sniffd", "curiosity", "6m", "indexes every new smell and commit. +10/h"),
    (99, "dreamd", None, "on sleep", "runs sealed dreams (law VII)"),
]


def table(brain):
    d = brain.drives()
    rows = []
    for pid, name, drive, tick, desc in DAEMONS:
        if drive:
            v = round(d[drive])
            state = "WANT" if v >= 70 else "RUN" if v >= 35 else "IDLE"
        elif name == "byte":
            v, state = round(max(d.values())), "WAG"
        else:
            v, state = 0, "SLEEP"
        rows.append((pid, name, v, state, tick, desc))
    return rows
