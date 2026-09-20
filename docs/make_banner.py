#!/usr/bin/env python3
"""Draw the repo banner. Pure PIL, no generated imagery — RyanAI Lab house style.

Concept: a measured 13-point agentic-tool gap that closes once you match the
official measurement setting. Left = wordmark. Right = a gate threshold with a
bar rising from 81.7 (fail) to 93.3 (pass) and a single orange marker on the pass
run — the one-number story this cookbook tells.
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont
# Requires Pillow:  pip install pillow
# Fonts fall back to ImageFont.load_default() if the system .ttc paths below are absent.

W, H = 1280, 640
BG = (10, 10, 10)
WHITE = (245, 245, 245)
GREY = (140, 140, 140)
DIM = (70, 70, 70)
ORANGE = (255, 122, 26)
OUT = pathlib.Path(__file__).resolve().parents[1] / "docs/assets/banner.png"

HN = "/System/Library/Fonts/HelveticaNeue.ttc"
MENLO = "/System/Library/Fonts/Menlo.ttc"

def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()

f_title = font(HN, 88, 7)     # Light
f_tag = font(HN, 30, 7)
f_mono = font(MENLO, 17)
f_label = font(MENLO, 15)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# crosshair corners
for cx, cy in ((40, 40), (W - 40, H - 40)):
    d.line([(cx - 11, cy), (cx + 11, cy)], fill=DIM, width=1)
    d.line([(cx, cy - 11), (cx, cy + 11)], fill=DIM, width=1)

# 5x3 dot lattices
for ox, oy in ((72, 78), (1150, 536)):
    for r in range(3):
        for c in range(5):
            x, y = ox + c * 15, oy + r * 12
            d.ellipse([x, y, x + 1.6, y + 1.6], fill=DIM)

# wordmark
d.text((80, 196), "AGENTIC", font=f_title, fill=WHITE)
d.text((80, 288), "GAP", font=f_title, fill=WHITE)
d.text((82, 414), "Thinking mode closes c7-agentic-if 81.7 to 93.3.", font=f_tag, fill=WHITE)
d.text((82, 462), "VLLM · QWEN3.8-FLASH-NEXT · MTP · NO-ASYNC-SCHEDULING · MEASURED", font=f_mono, fill=GREY)

# right: a gate threshold with two bars (fail -> pass) and the orange pass marker
SX, SY = 860, 150
bar_w, bar_gap = 70, 60
# bars drawn from a fixed floor up to their score height (0..100 -> 0..220 px)
floor_y = SY + 260
def bar_height(score):
    return (score / 100.0) * 220
# gate drawn at the correct fraction of the bar height (85/100)
gate_y = floor_y - bar_height(85)
arms = [("81.7", 81.7, (150, 150, 150)), ("93.3", 93.3, ORANGE)]
for i, (label, score, color) in enumerate(arms):
    x = SX + 20 + i * (bar_w + bar_gap)
    top = floor_y - bar_height(score)
    d.rectangle([x, top, x + bar_w - 1, floor_y], outline=color, width=2)
    d.text((x + 8, top - 26), label, font=f_label, fill=color)

# threshold line + label
d.line([(SX - 10, gate_y), (SX + 40 + 2 * bar_w + bar_gap, gate_y)], fill=DIM, width=1)
d.text((SX - 10, gate_y - 26), "gate >= 85", font=f_label, fill=DIM)

# orange dot marking the pass bar (the closing run)
mx = SX + 20 + 1 * (bar_w + bar_gap) + bar_w // 2
my = floor_y - bar_height(93.3) - 12
d.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=ORANGE)

# footer rule + labels
d.line([(80, 560), (W - 80, 560)], fill=(40, 40, 40), width=1)
d.text((80, 576), "RYANAI LAB", font=f_label, fill=GREY)
d.text((W - 80 - 250, 576), "DELL PRO MAX WITH GB10", font=f_label, fill=GREY)

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT)
print("wrote", OUT)
