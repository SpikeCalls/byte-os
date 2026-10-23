"""Render assets/live.gif — `byte live` as a looping GIF for the README.

dev-only. needs Pillow (the package itself has zero dependencies).
    pip install pillow && python scripts/render_live_gif.py
"""

import os
import random
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("BYTE_HOME", tempfile.mkdtemp())
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image, ImageDraw, ImageFont, ImageFilter  # noqa: E402

from byteos.art import frame  # noqa: E402
from byteos.brain import DRIVES, Brain  # noqa: E402

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT = ImageFont.truetype(FONT_PATH, 15)
BOLD = ImageFont.truetype(FONT_PATH.replace(".ttf", "-Bold.ttf"), 15)
CW, LH = FONT.getlength("a"), 19
MINT, PINK, DIM, BG = (150, 245, 200), (255, 120, 150), (70, 120, 100), (0, 0, 0)
W, H = 1000, 520


def bar(v):
    v = max(0, min(100, int(v)))
    return "█" * (v // 10) + "░" * (10 - v // 10)


def render(art, panel, cursor):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    x0, y0 = 28, 26
    d.text((x0, y0 - 2), "~ $ byte live", font=FONT, fill=DIM)
    y0 += LH + 6
    for r, line in enumerate(art):
        y = y0 + r * LH
        if 12 <= r <= 16 and line.count(":") >= 2:
            a, b = line.index(":"), line.rindex(":")
            d.text((x0, y), line[: a + 1], font=FONT, fill=MINT)
            d.text((x0 + (a + 1) * CW, y), line[a + 1 : b], font=FONT, fill=PINK)
            d.text((x0 + b * CW, y), line[b:], font=FONT, fill=MINT)
        else:
            d.text((x0, y), line, font=FONT, fill=MINT)
    px = x0 + 37 * CW
    for r, (txt, col, f) in enumerate(panel):
        d.text((px, y0 + (r + 4) * LH), txt, font=f, fill=col)
    glow = img.filter(ImageFilter.GaussianBlur(3))
    return Image.blend(img, glow, 0.35).point(lambda v: min(255, int(v * 1.5)))


def main(out="assets/live.gif", n=72):
    rng = random.Random(4)
    b = Brain(hunger=48, boredom=58, love=62, energy=55, curiosity=50, last_seen=0)
    thoughts = [b.thought(rng) for _ in range(3)]
    wants = [b.wants(1, rng)[0][2] for _ in range(3)]
    frames = []
    for i in range(n):
        b.catch_up(now=b.last_seen + 150)
        if i == 40:
            b.act("fetch")
        eyes = "blink" if i % 30 in (0, 1) else ("happy" if 40 <= i < 52 else b.mood()[1])
        art = frame(eyes=eyes, tail=i // (1 if 40 <= i < 52 else 2))
        panel = [(f"byte · {b.mood()[0]}", MINT, BOLD), ("", MINT, FONT)]
        for k in DRIVES:
            v = getattr(b, k)
            panel.append((f"{k:<10} {bar(v)} {round(v):>3}", MINT, FONT))
        panel.append(("", MINT, FONT))
        if 40 <= i < 52:
            panel.append(("♥ ball returned. slightly wetter.", PINK, FONT))
        else:
            panel.append((f"→ {wants[(i // 24) % 3]}", MINT, FONT))
        panel += [("", MINT, FONT), (f"··· {thoughts[(i // 24) % 3]}"[:62], DIM, FONT)]
        frames.append(render(art, panel, i))
    Path(out).parent.mkdir(exist_ok=True)
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=120, loop=0, optimize=True)
    print(out)


if __name__ == "__main__":
    main(*sys.argv[1:])
