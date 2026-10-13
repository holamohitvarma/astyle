#!/usr/bin/env python3
"""Farhan - 10 Claude skills reel, PYNK reference layout.
Writes .tesseract-work/editable.json + anim.json."""
import json

W, H = 1080, 1920
DUR = 33800
S = [0.0, 2.85, 5.53, 8.67, 11.73, 14.39, 17.09, 19.69, 22.21, 24.99, 27.17]
NAMES = ["Product-Ad", "Paper-Cut", "AI-UGC", "Director", "Animation", "Content", "Studio", "Ad", "Visual",
         "Creative-Ad"]
ms = lambda t: int(round(t * 1000))
CARDS_END = ms(S[-1])

# measured from the reference (1080x1920): bar 683x228, badge ~150, card 378x677 at (352,1193)
BAR_X, BAR_Y, BAR_W, BAR_H = 200, 340, 683, 228
CARD_X, CARD_Y, CARD_SCALE = 352, 1193, 101.6

_id, _k, anims = [1], [0], []


def nid():
    _id[0] += 1
    return _id[0]


def tf(x=0, y=0, s=100, ax=0, ay=0):
    return {"anchorPoint": [ax, ay], "position": [x, y], "scale": [s, s], "rotation": 0, "opacity": 100}


def rng(s, d):
    return {"start": int(s), "duration": int(d)}


LIN = {"type": "linear"}
OUT = {"type": "cubicBezier", "x1": 0.16, "y1": 1, "x2": 0.3, "y2": 1}
EASE = {"type": "cubicBezier", "x1": 0.25, "y1": 0.1, "x2": 0.25, "y2": 1}


def kf(lid, prop, keys):
    out = []
    for t, v, e in keys:
        _k[0] += 1
        out.append({"id": f"k{_k[0]}", "layerTime": int(t), "value": {"type": "float", "value": v}, "easing": e})
    anims.append({"type": "setFxPropertyKeyframes", "compositionId": "main",
                  "property": {"layerId": lid, "propertyType": prop}, "keyframes": out})


def rect(name, x, y, w, h, fill, st, d, r=0, stroke=None, sw=0):
    R = {"size": [w, h], "fillColor": fill, "roundness": r}
    if stroke:
        R.update(strokeEnabled=True, strokeColor=stroke, strokeWidth=sw, fillEnabled=False)
    return {"type": "Rect", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
            "transform": tf(x, y), "rect": R}


def text(name, s, x, y, w, h, size, color, st, d, font=("Helvetica", "Bold"), just="center"):
    return {"type": "Text", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
            "transform": tf(x, y),
            "sourceText": {"text": s, "fontFamily": font[0], "fontStyle": font[1], "fontSize": size, "tracking": TRACK,
                           "fillColor": color, "strokeWidth": 0, "justification": just, "boxText": True,
                           "boxPosition": [0, 0], "boxSize": [w, h], "verticalAlign": "center", "tracking": -1}}


def shape(name, pts, st, d, x, y, stroke, sw, closed=True):
    cmds = [{"type": "moveTo", "x": pts[0][0], "y": pts[0][1]}] + \
           [{"type": "lineTo", "x": a, "y": b} for a, b in pts[1:]] + ([{"type": "close"}] if closed else [])
    return {"type": "Shape", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
            "transform": tf(x, y),
            "shape": {"path": {"commands": cmds}, "fills": [],
                      "strokes": [{"paint": {"type": "solid", "color": stroke}, "width": sw, "cap": "round",
                                   "join": "round", "miterLimit": 4, "blendMode": "normal", "opacity": 100}]}}


def group(name, st, d, layers, x=0, y=0, ax=0, ay=0):
    return {"type": "Group", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
            "transform": tf(x, y, ax=ax, ay=ay), "layers": layers}


TRACK = -10  # -1% of font size (Tesseract tracking is in 1/1000 em)
GREY = [0.62, 0.62, 0.66, 1]
WHITE = [1, 1, 1, 1]

# ---------------------------------------------------------------- title bar (persistent) + per-skill titles
titles = []
for i, n in enumerate(NAMES):
    st, en = ms(S[i]), ms(S[i + 1])
    titles.append(text(f"Title {n}", f"{n} Skill", BAR_X + 20, BAR_Y + 26, BAR_W - 80, 104, 60, WHITE, st, en - st))
row_y = BAR_Y + 142
bar_layers = titles + [
    text("Skill.md", "Skill.md", BAR_X + 140, row_y, 300, 70, 44, GREY, 0, CARDS_END,
         font=("Helvetica", "Regular"), just="left"),
    shape("Folder icon", [(0, 6), (12, 6), (17, 12), (40, 12), (40, 34), (0, 34)], 0, CARDS_END,
          BAR_X + 84, row_y + 17, GREY, 3.2),
    shape("Chevron", [(0, 0), (10, 11), (0, 22)], 0, CARDS_END, BAR_X + 34, row_y + 24, GREY, 3.6, closed=False),
    rect("Title bar", BAR_X, BAR_Y, BAR_W, BAR_H, [0.075, 0.075, 0.09, 1], 0, CARDS_END),
]
badge = {"type": "Image", "id": nid(), "name": "Claude badge", "blendMode": "normal",
         "activeRange": rng(0, CARDS_END), "transform": tf(BAR_X + BAR_W - 37, BAR_Y + 2, 29.5, 256, 256),
         "source": {"assetId": "claude-logo", "fit": "contain"}, "cornerRadius": 34}
title_group = group("Skill title card", 0, CARDS_END, [badge] + bar_layers)

# ---------------------------------------------------------------- example cards (cropped from the reference)
cards = []
for i, n in enumerate(NAMES):
    st, en = ms(S[i]), ms(S[i + 1])
    cards.append({"type": "Video", "id": nid(), "name": f"Card {i+1} {n}", "blendMode": "normal",
                  "activeRange": rng(st, en - st), "sourceRange": rng(st, en - st), "sourceIntrinsicDuration": 27166,
                  "volume": 0.0, "transform": tf(CARD_X, CARD_Y, CARD_SCALE),
                  "source": {"assetId": "cards", "fit": "contain"}})
card_group = group("Skill example cards", 0, CARDS_END, list(reversed(cards)))

# ---------------------------------------------------------------- CTA keyword
c0, c1 = ms(30.45), ms(32.75)
kw = text("SKILLS keyword", "SKILLS", 40, 340, 1000, 220, 196, WHITE, 0, c1 - c0,
          font=("Helvetica", "Bold"))
kw["dropShadow"] = {"color": [0, 0, 0, 0.6], "blurRadius": 28, "spreadRadius": 0, "blendMode": "normal", "offset": [0, 8]}
kwg = group("CTA keyword", c0, c1 - c0, [kw], x=540, y=450, ax=540, ay=450)
kf(kwg["id"], "scaleX", [(0, 60, LIN), (220, 108, OUT), (340, 100, EASE)])
kf(kwg["id"], "scaleY", [(0, 60, LIN), (220, 108, OUT), (340, 100, EASE)])
kf(kwg["id"], "opacity", [(0, 0, LIN), (90, 100, LIN), (c1 - c0 - 120, 100, LIN), (c1 - c0, 0, LIN)])

# ---------------------------------------------------------------- A-roll + audio
aroll = {"type": "Video", "id": nid(), "name": "Farhan A-roll", "blendMode": "normal", "activeRange": rng(0, DUR),
         "sourceRange": rng(0, DUR), "sourceIntrinsicDuration": DUR, "volume": 0.0, "transform": tf(0, 0),
         "source": {"assetId": "aroll", "fit": "contain"}}
audio = []


def aud(name, asset, st, d, intrinsic, vol):
    audio.append({"type": "Audio", "id": nid(), "name": name, "activeRange": rng(st, d), "sourceRange": rng(0, d),
                  "sourceIntrinsicDuration": intrinsic, "source": {"assetId": asset}, "volume": vol,
                  "captionsEnabled": False, "windowMs": 50})


aud("Dialogue (normalized)", "dialogue-norm", 0, DUR, 33800, 1.0)
for t in S[1:-1]:
    aud(f"Pop {t}s", "pop", ms(t) - 15, 200, 200, 0.22)
aud("Ping keyword", "ping", c0 - 10, 450, 450, 0.3)

doc = {"$schema": "https://jerboa.dev/schemas/fx-composition/editable/v1/document.schema.json", "formatVersion": 1,
       "dimensions": {"width": W, "height": H}, "duration": DUR / 1000,
       "composition": {"id": "main", "name": "Main", "layers": [kwg, title_group, card_group, aroll] + audio}}
json.dump(doc, open(".tesseract-work/editable.json", "w"), indent=1, ensure_ascii=False)
json.dump(anims, open(".tesseract-work/anim.json", "w"), indent=1)
print("ok", len(anims), "anim")
