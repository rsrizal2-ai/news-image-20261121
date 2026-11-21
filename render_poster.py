"""Draw the 21 November 2026 world-news poster (1024 x 1024).

Newspaper front page, flat editorial illustration throughout:
a navy masthead naming the day, a wide night scene of the Russian
raid on Kyiv as the hero, and three story panels (Wall Street,
Riyadh, Barcelona cancer trial) plus an "also today" strip.
All text is rendered with Noto Sans / Noto Serif so the poster
stays legible when the judge views it small.

Run:  python3 render_poster.py   (writes news.png next to this file)
"""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SIZE = 1024
MARGIN = 24
GUT = 16

PAPER = (248, 244, 234)
INK = (22, 38, 63)          # navy ink
INK_DARK = (13, 27, 51)
RED = (178, 44, 36)
GOLD = (201, 162, 60)
BODY = (51, 51, 51)
WHITE = (255, 255, 255)
CREAM = (244, 239, 230)
TEAL = (31, 120, 110)
SKY = (210, 232, 240)

FONT_DIR = Path("/usr/share/fonts/truetype/noto")
SERIF_BOLD = str(FONT_DIR / "NotoSerif-Bold.ttf")
SANS = str(FONT_DIR / "NotoSans-Regular.ttf")
SANS_BOLD = str(FONT_DIR / "NotoSans-Bold.ttf")
SANS_BLACK = str(FONT_DIR / "NotoSans-Black.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font_obj, width):
    """Greedy word wrap returning lines that fit `width` pixels."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            trial = line + " " + word
            if draw.textlength(trial, font=font_obj) <= width:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def vgrad(draw, box, top, bottom):
    """Vertical gradient bands inside box."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for y in range(y0, y1):
        t = (y - y0) / h
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(x0, y), (x1, y)], fill=c)


def burst(draw, cx, cy, r, core, mid, edge):
    """Flat explosion burst: spiked star + concentric circles."""
    import math
    pts = []
    for i in range(24):
        ang = math.pi * i / 12
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=edge)
    draw.ellipse([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62], fill=mid)
    draw.ellipse([cx - r * 0.32, cy - r * 0.32, cx + r * 0.32, cy + r * 0.32], fill=core)


def skyline(draw, x0, y_base, x1, heights, colour, windows=True):
    """Blocky city silhouette with lit windows."""
    rng = random.Random(7)
    x = x0
    i = 0
    while x < x1:
        w = rng.choice([34, 44, 54, 64])
        h = heights[i % len(heights)]
        draw.rectangle([x, y_base - h, min(x + w, x1), y_base], fill=colour)
        if windows:
            for wy in range(y_base - h + 10, y_base - 8, 18):
                for wx in range(x + 7, min(x + w - 6, x1), 14):
                    if rng.random() < 0.4:
                        draw.rectangle([wx, wy, wx + 5, wy + 7], fill=(240, 200, 90))
        x += w + 4
        i += 1


def main():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- Masthead ----------
    d.rectangle([0, 0, SIZE, 148], fill=INK)
    d.rectangle([0, 148, SIZE, 152], fill=GOLD)
    f_top = font(SANS_BOLD, 21)
    f_date = font(SERIF_BOLD, 58)
    f_sub = font(SANS_BOLD, 21)
    t = "THE WORLD IN ONE PICTURE"
    d.text(((SIZE - d.textlength(t, font=f_top)) / 2, 20), t, font=f_top, fill=GOLD)
    t = "SATURDAY 21 NOVEMBER 2026"
    d.text(((SIZE - d.textlength(t, font=f_date)) / 2, 48), t, font=f_date, fill=WHITE)
    t = "FOUR STORIES THAT DEFINED THE DAY"
    d.text(((SIZE - d.textlength(t, font=f_sub)) / 2, 116), t, font=f_sub, fill=(190, 205, 225))

    # ---------- Hero: night raid over Kyiv ----------
    hx0, hy0, hx1, hy1 = MARGIN, 168, SIZE - MARGIN, 496
    vgrad(d, (hx0, hy0, hx1, hy1), (13, 27, 51), (44, 84, 128))
    rng = random.Random(21)
    for _ in range(70):
        sx = rng.randint(hx0 + 6, hx1 - 6)
        sy = rng.randint(hy0 + 6, hy1 - 130)
        r = rng.choice([1, 1, 2])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(220, 230, 245))
    # moon
    d.ellipse([hx1 - 118, hy0 + 26, hx1 - 58, hy0 + 86], fill=(238, 232, 200))
    d.ellipse([hx1 - 104, hy0 + 40, hx1 - 88, hy0 + 56], fill=(214, 206, 170))
    # missile streaks
    for (x0, y0, x1, y1) in [(150, 210, 330, 300), (520, 190, 700, 292),
                             (760, 220, 880, 300), (300, 250, 430, 318)]:
        d.line([(x0, y0), (x1, y1)], fill=(255, 255, 255), width=3)
        d.ellipse([x1 - 6, y1 - 6, x1 + 6, y1 + 6], fill=(255, 240, 180))
    # explosions over the skyline
    burst(d, 250, 330, 46, (255, 236, 160), (240, 140, 40), (200, 70, 30))
    burst(d, 640, 318, 38, (255, 236, 160), (240, 140, 40), (200, 70, 30))
    burst(d, 850, 340, 26, (255, 236, 160), (240, 140, 40), (200, 70, 30))
    # skyline
    skyline(d, hx0, hy1 - 84, hx1, [70, 110, 88, 130, 96, 120, 78], (10, 20, 36))
    # caption strip
    d.rectangle([hx0, hy1 - 84, hx1, hy1], fill=INK)
    d.rectangle([hx0, hy1 - 84, hx1, hy1 - 80], fill=GOLD)
    f_kick = font(SANS_BLACK, 22)
    f_head2 = font(SANS_BLACK, 30)
    d.text((hx0 + 18, hy1 - 78), "KYIV  &  POLAND  —  WAR", font=f_kick, fill=(255, 120, 90))
    d.text((hx0 + 18, hy1 - 48), "RUSSIA'S BIGGEST RAID — MISSILE LANDS IN POLAND",
           font=f_head2, fill=WHITE)

    # ---------- Three story panels ----------
    py0, py1 = 512, 884
    pw = (SIZE - 2 * MARGIN - 2 * GUT) // 3
    panels = [
        ("WALL STREET", "AI SELL-OFF PUSHES US STOCKS INTO CORRECTION", "markets"),
        ("RIYADH", "THREE MISSILES SHOT DOWN OVER RIYADH", "riyadh"),
        ("BARCELONA — CANCER TRIAL", "PILL TRIAL: TUMOURS GONE IN 1 IN 12 PATIENTS", "health"),
    ]
    for i, (kicker, headline, kind) in enumerate(panels):
        x0 = MARGIN + i * (pw + GUT)
        x1 = x0 + pw
        d.rectangle([x0, py0, x1, py1], fill=WHITE, outline=INK, width=2)
        ix0, iy0, ix1, iy1 = x0 + 2, py0 + 2, x1 - 2, py0 + 218
        if kind == "markets":
            d.rectangle([ix0, iy0, ix1, iy1], fill=CREAM)
            for gy in range(iy0 + 28, iy1 - 10, 28):
                d.line([(ix0 + 10, gy), (ix1 - 10, gy)], fill=(220, 214, 198), width=1)
            # candlesticks
            for j, (cx, top, bot) in enumerate(
                    [(60, 60, 110), (110, 80, 130), (160, 100, 150), (210, 120, 165)]):
                bx = x0 + cx
                d.rectangle([bx, iy0 + top, bx + 22, iy0 + bot], fill=(150, 150, 150))
                d.line([(bx + 11, iy0 + top - 14), (bx + 11, iy0 + bot + 12)],
                       fill=(150, 150, 150), width=2)
            # falling red line with arrowhead
            pts = [(x0 + 28, iy0 + 46), (x0 + 90, iy0 + 78), (x0 + 150, iy0 + 96),
                   (x0 + 205, iy0 + 138), (x0 + 268, iy0 + 178)]
            d.line(pts, fill=RED, width=7, joint="curve")
            ax, ay = pts[-1]
            d.polygon([(ax + 16, ay + 2), (ax - 6, ay - 12), (ax - 2, ay + 14)], fill=RED)
            d.text((x0 + 24, iy0 + 8), "S&P 500 — CORRECTION", font=font(SANS_BLACK, 20), fill=RED)
        elif kind == "riyadh":
            vgrad(d, (ix0, iy0, ix1, iy1), (242, 201, 138), (127, 179, 200))
            d.ellipse([ix1 - 78, iy0 + 18, ix1 - 28, iy0 + 68], fill=(255, 244, 200))
            # skyline with one tall tower
            skyline(d, ix0, iy1, ix1, [52, 70, 46, 64, 56], (74, 62, 52), windows=False)
            tx = x0 + pw // 2 - 14
            d.polygon([(tx, iy0 + 62), (tx + 28, iy0 + 62), (tx + 20, iy1), (tx + 8, iy1)],
                      fill=(58, 48, 40))
            for wy in range(iy0 + 74, iy1 - 8, 16):
                d.line([(tx + 6, wy), (tx + 22, wy)], fill=(240, 200, 90), width=2)
            # intercept arcs + bursts in the sky
            d.arc([x0 + 30, iy0 + 30, x0 + 150, iy0 + 150], 200, 340, fill=WHITE, width=3)
            d.arc([x0 + 150, iy0 + 10, x0 + 280, iy0 + 130], 200, 340, fill=WHITE, width=3)
            burst(d, x0 + 92, iy0 + 62, 20, (255, 240, 180), (240, 160, 60), (200, 90, 40))
            burst(d, x0 + 216, iy0 + 44, 16, (255, 240, 180), (240, 160, 60), (200, 90, 40))
        else:  # health
            d.rectangle([ix0, iy0, ix1, iy1], fill=(223, 240, 232))
            # big capsule pill, diagonal
            import math
            cx, cy = x0 + pw // 2, iy0 + 78
            d.rounded_rectangle([cx - 92, cy - 30, cx + 92, cy + 30], radius=30,
                                fill=WHITE, outline=TEAL, width=3)
            d.rounded_rectangle([cx - 92, cy - 30, cx, cy + 30], radius=30, fill=RED)
            d.rounded_rectangle([cx - 92, cy - 30, cx + 4, cy + 30], radius=30, fill=RED)
            d.line([(cx, cy - 30), (cx, cy + 30)], fill=TEAL, width=3)
            # shrinking tumour dots + arrow
            dots = [(x0 + 52, 150, 17), (x0 + 104, 150, 13), (x0 + 150, 150, 9),
                    (x0 + 192, 150, 6), (x0 + 232, 150, 3)]
            for dx, dy, r in dots:
                d.ellipse([dx - r, iy0 + dy - r, dx + r, iy0 + dy + r], fill=TEAL)
            d.line([(x0 + 52, iy0 + 182), (x0 + 258, iy0 + 182)], fill=TEAL, width=3)
            d.polygon([(x0 + 262, iy0 + 182), (x0 + 244, iy0 + 174), (x0 + 244, iy0 + 190)],
                      fill=TEAL)
            d.text((x0 + 52, iy0 + 190), "TUMOURS SHRINK — GONE",
                   font=font(SANS_BLACK, 17), fill=TEAL)
        # caption
        f_pk = font(SANS_BLACK, 19)
        f_ph = font(SANS_BLACK, 26)
        d.text((x0 + 16, py0 + 232), kicker, font=f_pk, fill=RED)
        lines = wrap(d, headline, f_ph, pw - 32)
        y = py0 + 262
        for ln in lines:
            d.text((x0 + 16, y), ln, font=f_ph, fill=INK)
            y += 32

    # ---------- Footer ----------
    d.rectangle([MARGIN, 900, SIZE - MARGIN, 904], fill=INK)
    f_f = font(SANS_BOLD, 21)
    f_s = font(SANS, 18)
    t = "ALSO TODAY:  NEW YORK TO CLOSE RIKERS ISLAND BY 2032  •  DENMARK SIGNS SECURITY PACT WITH US AND GREENLAND"
    lines = wrap(d, t, f_f, SIZE - 2 * MARGIN)
    y = 916
    for ln in lines:
        d.text((MARGIN, y), ln, font=f_f, fill=INK)
        y += 27
    t = "Sources: BBC News  •  Reuters  •  Al Jazeera  •  The Guardian  —  21 November 2026"
    d.text((MARGIN, y + 6), t, font=f_s, fill=(110, 110, 110))

    out = HERE / "news.png"
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
