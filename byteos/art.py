"""Byte's body. Monospace only. No vectors were harmed."""

DOG = [
    r"      _____________      ",
    r"  ___/             \___  ",
    r" /   |             |   \ ",
    r" |   |   {e}     {e}   |   | ",
    r" |   |      _      |   | ",
    r" |   | ,,  (_)  ,, |   | ",
    r"  \  |    {m}    |  /  ",
    r"   \/ \___________/ \/   ",
    r"     /[=====o=====]\     ",
    r"    /  :         :  \    ",
    r"   /   :  _   _  :   \   ",
    r"  /    : (  V  ) :    \  ",
    r" (o)   :  \   /  :   (o) ",
    r"  |    :   \ /   :    |  ",
    r"  |    :    V    :{t}|  ",
    r"       :_________:       ",
    r"        ||     ||        ",
    r"        ||     ||        ",
    r"       [__]   [__]       ",
]

EYES = {"open": "0", "blink": "-", "happy": "^", "sleep": "u", "want": "O"}
MOUTH = {"tongue": r"\_U_/", "smile": r"\___/", "flat": r"_____", "open": r"\_O_/"}
TAIL = [" \\  ", "  | ", "  / ", "  ~ "]

HEART_ROWS = range(10, 15)


def render(eyes="open", mouth="tongue", tail=0):
    e = EYES.get(eyes, eyes)
    m = MOUTH.get(mouth, mouth)
    t = TAIL[tail % len(TAIL)]
    return [row.format(e=e, m=m, t=t).rstrip().ljust(25) for row in DOG]


def frame(label="Fetch", width=33, **kw):
    """The dog inside the bracket frame, label at the bottom. Same as the logo."""
    body = render(**kw)
    inner = width - 4
    out = ["┌─" + " " * (inner) + "─┐", "│" + " " * (width - 2) + "│"]
    for row in body:
        out.append("│ " + row.center(width - 4) + " │")
    out.append("│" + " " * (width - 2) + "│")
    pad = width - 2 - len(label) - 2
    left = pad // 2
    out.append("├" + "─" * left + " " + label + " " + "─" * (pad - left) + "┤")
    return out
