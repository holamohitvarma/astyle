#!/usr/bin/env python3
"""v3: reference-matched rebuild (live tutorial clips, measured caption/title specs).

Authoring clock = SOURCE speech seconds; m() maps to edit ms through the pause trim.
Tutorial clips are addressed by tutorial seconds (asset "tut", 1280x720).
Writes .tesseract-work/editable_v3.json + anim_v3.json.
"""
import json, re, sys

W, H, SEAM = 1080, 1920, 840
SRT = "/Users/mohitvarma/Downloads/claude + apollo 1080p.srt"
SRC_DUR = 74880
SPEECH_END = 74.75
TAIL_MS = 1200                     # hold the full-screen end card after the last word
LEVELS = dict(inputBlack=0.0, inputWhite=224.0, gamma=1.18, outputBlack=8.0, outputWhite=255.0)
WARM = {"veo-tower": 25, "veo-freelancer": -8, "veo-team": -8}
if len(sys.argv) > 1:
    LEVELS.update(json.loads(sys.argv[1]))

# ---------------------------------------------------------------- pause trim
SIL = [(6.011, 6.440), (6.831, 7.477), (10.400, 11.093), (15.278, 15.768), (16.887, 17.331),
       (20.559, 21.004), (23.288, 23.954), (25.403, 25.742), (30.038, 30.460), (31.966, 32.348),
       (33.478, 33.997), (35.069, 35.519), (37.192, 37.692), (39.553, 39.924), (41.300, 41.912),
       (44.732, 45.172), (51.002, 51.648), (53.848, 54.407), (56.502, 57.006), (59.570, 59.958),
       (71.440, 71.953)]
PAD = 0.10
# whole lines removed for pace (v3.1): decision makers / in-house / rarely outsource / match to service
LINE_CUTS = [(20.66, 23.85), (28.27, 30.36), (32.07, 33.90), (39.65, 41.81)]
allc = sorted([(a + PAD, b - PAD) for a, b in SIL if b - a >= 0.30] + LINE_CUTS)
merged = []
for a, b in allc:
    if merged and a <= merged[-1][1]:
        merged[-1] = (merged[-1][0], max(merged[-1][1], b))
    else:
        merged.append((a, b))
keeps, cur = [], 0.05
for a, b in merged:
    keeps.append((cur, a)); cur = b
keeps.append((cur, SPEECH_END))
seg_edit, acc = [], 0.0
for a, b in keeps:
    seg_edit.append((a, b, acc)); acc += b - a
SPEECH_MS = int(round(acc * 1000))
EDIT_DUR = SPEECH_MS + TAIL_MS


def m(t):
    for a, b, e in seg_edit:
        if t < a:
            return int(round(e * 1000))
        if t <= b:
            return int(round((e + t - a) * 1000))
    return SPEECH_MS


# ---------------------------------------------------------------- primitives
_id, _kid, anims = [1], [0], []


def nid():
    _id[0] += 1
    return _id[0]


EASE = {"type": "cubicBezier", "x1": 0.25, "y1": 0.1, "x2": 0.25, "y2": 1}
OUT = {"type": "cubicBezier", "x1": 0.16, "y1": 1, "x2": 0.3, "y2": 1}
LIN = {"type": "linear"}
HOLD = {"type": "hold"}


def kf(lid, prop, keys, vtype="float"):
    ks = []
    for t, v, e in keys:
        _kid[0] += 1
        ks.append({"id": f"k{_kid[0]}", "layerTime": int(t), "value": {"type": vtype, "value": v}, "easing": e})
    anims.append({"type": "setFxPropertyKeyframes", "compositionId": "main",
                  "property": {"layerId": lid, "propertyType": prop}, "keyframes": ks})


def tf(x=0, y=0, s=100, ax=0, ay=0, rot=0, op=100, sy=None):
    return {"anchorPoint": [ax, ay], "position": [x, y], "scale": [s, s if sy is None else sy], "rotation": rot,
            "opacity": op}


def rng(s, d):
    return {"start": int(s), "duration": int(max(1, d))}


def rect(name, x, y, w, h, fill, st, d, r=0, stroke=None, sw=0, grad=None, shadow=None, blend="normal", op=100):
    R = {"size": [w, h], "fillColor": fill, "roundness": r}
    if grad:  # vertical gradient, top colour -> bottom colour
        R["fillPaint"] = {"type": "gradient", "gradientType": "linear", "start": [0, -h / 2], "end": [0, h / 2],
                          "stops": [{"offset": 0, "color": grad[0]}, {"offset": 1, "color": grad[1]}]}
    if stroke:
        R.update(strokeEnabled=True, strokeColor=stroke, strokeWidth=sw)
    L = {"type": "Rect", "id": nid(), "name": name, "blendMode": blend, "activeRange": rng(st, d),
         "transform": tf(x, y, op=op), "rect": R}
    if shadow:
        L["dropShadow"] = shadow
    return L


def text(name, s, x, y, w, h, size, color, st, d, font=("Helvetica Neue", "Bold"), just="center", tr=0):
    return {"type": "Text", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
            "transform": tf(x, y),
            "sourceText": {"text": s, "fontFamily": font[0], "fontStyle": font[1], "fontSize": size,
                           "fillColor": color, "strokeWidth": 0, "justification": just, "boxText": True,
                           "boxPosition": [0, 0], "boxSize": [w, h], "verticalAlign": "center", "tracking": tr}}


def image(name, asset, x, y, st, d, s=100, radius=None, rot=0, ax=0, ay=0):
    L = {"type": "Image", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
         "transform": tf(x, y, s, ax, ay, rot), "source": {"assetId": asset, "fit": "contain"}}
    if radius:
        L["cornerRadius"] = radius
    return L


def shape(name, pts, fill, st, d, x=0, y=0, stroke=None, sw=0):
    cmds = [{"type": "moveTo", "x": pts[0][0], "y": pts[0][1]}] + \
           [{"type": "lineTo", "x": px, "y": py} for px, py in pts[1:]] + [{"type": "close"}]
    sh = {"path": {"commands": cmds},
          "fills": [{"paint": {"type": "solid", "color": fill}, "fillRule": "nonZeroWinding", "blendMode": "normal",
                     "opacity": 100}]}
    if stroke:
        sh["strokes"] = [{"paint": {"type": "solid", "color": stroke}, "width": sw, "blendMode": "normal",
                          "opacity": 100, "cap": "round", "join": "round", "miterLimit": 4}]
    return {"type": "Shape", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
            "transform": tf(x, y), "shape": sh}


def group(name, st, d, layers, x=0, y=0, ax=0, ay=0):
    return {"type": "Group", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
            "transform": tf(x, y, ax=ax, ay=ay), "layers": layers}


# Helvetica Neue advance widths (measured against the reference: 47 px Bold "Founders." = 223 px)
def text_w(s, size, bold=True):
    w = 0
    for c in s:
        if c == " ": w += 0.28
        elif c in "il.,:;'’|!": w += 0.27
        elif c in "ftrj": w += 0.36
        elif c in "mw": w += 0.86
        elif c.isupper(): w += 0.70 if c not in "MW" else 0.88
        elif c.isdigit(): w += 0.57
        elif c in "“”\"": w += 0.42
        else: w += 0.57
    return w * size * (1.0 if bold else 0.95)


SFX = []


def sfx(asset, edit_ms, vol, dur):
    SFX.append((asset, max(0, int(edit_ms)), vol, dur))


# ---------------------------------------------------------------- shot list (top pane)
# kinds: clip (tutorial live, T = tutorial seconds), veo, apollo-native (is a clip), claude splash, cta, profile
# view keys: (src_time, cx, cy, k)  -> source point (cx,cy) at pane centre, scale k (%)
SH = []


def shot(start, kind, **kw):
    SH.append(dict(start=start, kind=kind, **kw))


FILL = 116.7  # 1280x720 -> fills 840 px height
L = 465       # centre x that keeps the tutorial face-cam (x>=935) out of frame at FILL
shot(0.05, "clip", T=262.0, views=[(0.05, L, 360, FILL)])
shot(1.13, "clip", T=268.0, views=[(1.13, L, 360, FILL)])
shot(2.45, "clip", T=338.4, views=[(2.45, 640, 360, FILL)])
shot(3.67, "clip", T=300.0, views=[(3.67, 640, 360, FILL)])
shot(5.43, "clip", T=473.6, views=[(5.43, 640, 360, FILL)], bg=[0.976, 0.976, 0.969, 1])
shot(6.84, "clip", T=276.0, views=[(6.84, 640, 360, FILL)])
shot(11.00, "still", asset="tut-apollo", views=[(11.0, 640, 360, FILL)])
FV = (593, 262, 160)   # Apollo filter box, face-cam excluded
shot(12.00, "clip", T=62.5, views=[(12.0,) + FV])
shot(15.60, "clip", T=65.6, views=[(15.6,) + FV])
shot(17.33, "clip", T=69.4, views=[(17.33,) + FV])
shot(18.00, "clip", T=73.6, views=[(18.0,) + FV])
shot(19.00, "clip", T=77.4, views=[(19.0,) + FV])
shot(19.94, "clip", T=91.0, views=[(19.94,) + FV])
EV = (300, 250, 200)   # # Employees / Location panel at 3:37
shot(23.95, "clip", T=217.5, views=[(23.95,) + EV])
shot(25.74, "veo", asset="veo-tower", inpoint=0, views=[(25.74, 640, 360, FILL)])
shot(27.10, "clip", T=219.0, views=[(27.1,) + EV])
shot(30.46, "veo", asset="veo-freelancer", inpoint=0, views=[(30.46, 640, 360, FILL)])
shot(31.95, "clip", T=219.5, views=[(31.95, 300, 270, 200)])
shot(34.00, "veo", asset="veo-team", inpoint=0, views=[(34.0, 640, 360, FILL)])
shot(35.40, "clip", T=220.0, views=[(35.4,) + EV])
shot(37.69, "clip", T=217.5, views=[(37.69, 290, 170, 220)])
shot(38.67, "clip", T=222.4, views=[(38.67, 300, 330, 160)])
shot(41.91, "clip", T=251.6, views=[(41.91, L, 360, FILL)])
shot(43.25, "clip", T=317.6, views=[(43.25, 640, 360, FILL)])
shot(45.17, "full", T=339.9, T2=(49.15, 361.0),
     views=[(45.17, 540, 360, 150), (47.9, 540, 360, 150), (48.25, 860, 360, 150), (49.1, 860, 360, 150),
            (49.15, 200, 260, 280), (51.65, 200, 260, 292)])
shot(51.65, "claude")
P_BG = [0.976, 0.976, 0.969, 1]
shot(52.90, "clip", T=405.8, bg=P_BG,
     views=[(52.9, 640, 360, 93), (54.1, 640, 360, 93), (54.6, 330, 190, 128), (55.5, 330, 190, 128),
            (56.0, 645, 400, 95), (64.6, 645, 380, 97)],
     hl=[(57.5, 322, 374, 584, 29, "teal"), (60.45, 194, 483, 210, 29, "purple"),
         (62.85, 403, 337, 448, 29, "orange")])
shot(64.93, "clip", T=473.9, views=[(64.93, 640, 360, FILL)], bg=P_BG)
shot(65.90, "clip", T=489.8, bg=P_BG,
     views=[(65.9, 626, 360, 114), (71.95, 626, 380, 116)],
     hl=[(66.6, 260, 145, 304, 28, "teal"), (68.0, 332, 245, 344, 28, "orange"),
         (69.6, 172, 111, 164, 28, "purple"), (70.0, 174, 330, 166, 28, "purple"),
         (70.4, 174, 548, 148, 28, "purple")])
shot(71.95, "cta")
shot(73.30, "profile")

HL = {"teal": [0.35, 0.85, 0.75, 0.55], "purple": [0.66, 0.55, 1.0, 0.5], "orange": [1.0, 0.62, 0.25, 0.55]}
WHITE = [1, 1, 1, 1]

broll, overlays, fulls = [], [], []
FULL_WINDOWS = []


def view_keys(gid, gstart, views, pane_h=SEAM, gdur=None):
    if gdur and len(views) == 1:
        t, cx, cy, k = views[0]
        views = [views[0], ("END", cx, cy, k * 1.04)]
    sx, px, py = [], [], []
    for i, (t, cx, cy, k) in enumerate(views):
        lt = gdur if t == "END" else max(0, m(t) - gstart)
        e = LIN if (i == 0 or t == "END") else EASE
        sx.append((lt, k, e)); px.append((lt, 540 - cx * k / 100, e)); py.append((lt, pane_h / 2 - cy * k / 100, e))
    # de-duplicate equal times (keep last)
    def dd(a):
        out = {}
        for t, v, e in a: out[t] = (t, v, e)
        return list(out.values())
    kf(gid, "scaleX", dd(sx)); kf(gid, "scaleY", dd(sx)); kf(gid, "positionX", dd(px)); kf(gid, "positionY", dd(py))


def hl_layers(gstart, gdur, hls):
    out = []
    for (t, x, y, w, h, col) in hls:
        st = max(0, m(t) - gstart)
        R = rect("Highlight " + col, x - 3, y, w + 6, h, HL[col], st, gdur - st, r=5, blend="multiply")
        kf(R["id"], "scaleX", [(0, 0, LIN), (320, 100, OUT)])
        out.append(R)
    return out


def media_clip(asset, inpoint_ms, d, intrinsic):
    return {"type": "Video", "id": nid(), "name": asset, "blendMode": "normal", "activeRange": rng(0, d),
            "sourceRange": rng(inpoint_ms, d), "sourceIntrinsicDuration": intrinsic, "volume": 0.0,
            "transform": tf(0, 0), "source": {"assetId": asset, "fit": "contain"}}


for i, s in enumerate(SH):
    nxt = SH[i + 1]["start"] if i + 1 < len(SH) else None
    e0 = m(s["start"]); e1 = m(nxt) if nxt is not None else EDIT_DUR
    d = e1 - e0
    k = s["kind"]
    if k in ("clip", "veo", "still"):
        kids = hl_layers(e0, d, s.get("hl", []))
        if k == "clip":
            mc = media_clip("tut", int(s["T"] * 1000), d, 712733)
            mc["effects"] = [{"id": nid(), "effect": {"type": "sharpen", "amount": 35}}]
            kids.append(mc)
        elif k == "still":
            kids.append(image(s["asset"], s["asset"], 0, 0, 0, d))
        else:
            vc = media_clip(s["asset"], s["inpoint"], d, 8000)
            vc["effects"] = [{"id": nid(), "effect": dict(type="levels", inputBlack=8.0, inputWhite=245.0, gamma=1.05,
                                                            outputBlack=6.0, outputWhite=250.0)},
                             {"id": nid(), "effect": {"type": "temperatureTint", "temperature": WARM.get(s["asset"], 0)}}]
            kids.append(vc)
        g = group(f"Shot {s['start']:.2f} {s.get('asset', 'tut@%.1f' % s.get('T', 0))}", 0, d, kids)
        view_keys(g["id"], e0, s["views"], gdur=d)
        bg = rect("Pane bg", 0, 0, W, SEAM, s.get("bg", WHITE), 0, d)
        broll.append(group(f"Pane {s['start']:.2f}", e0, d, [g, bg]))
    elif k == "full":
        # full-screen moment: speaker hidden, recording centred on white, caption moves low
        t2, T2 = s["T2"]
        c1 = m(t2) - e0
        g = group("Full-screen recording", 0, d,
                  [dict(media_clip("tut", int(T2 * 1000), d - c1, 712733), activeRange=rng(c1, d - c1)),
                   media_clip("tut", int(s["T"] * 1000), c1, 712733)])
        view_keys(g["id"], e0, s["views"], pane_h=1720)
        fulls.append(group("Full-screen spreadsheet", e0, d, [g, rect("Full bg", 0, 0, W, H, WHITE, 0, d)]))
        FULL_WINDOWS.append((e0, e1))
    elif k == "claude":
        kids = [rect("Claude bg", 0, 0, W, SEAM, [0.98, 0.976, 0.965, 1], 0, d)]
        logo = image("Claude mark", "claude-logo", 540, 330, 0, d, s=52, ax=256, ay=256, radius=112)
        kf(logo["id"], "scaleX", [(0, 30, LIN), (380, 52, OUT)]); kf(logo["id"], "scaleY", [(0, 30, LIN), (380, 52, OUT)])
        kf(logo["id"], "rotation", [(0, -60, LIN), (600, 0, OUT)])
        word = text("Claude word", "Claude", 140, 520, 800, 150, 120, [0.1, 0.09, 0.08, 1], 120, d - 120,
                    font=("Georgia", "Regular"))
        kf(word["id"], "opacity", [(0, 0, LIN), (260, 100, EASE)])
        kf(word["id"], "positionY", [(0, 560, LIN), (360, 520, OUT)])
        broll.append(group("Claude splash", e0, d, [word, logo] + kids))
    elif k == "cta":
        bw, bh, bx, by = 620, 100, 230, 560
        word_ = "“SALES”"
        kids = []
        tt = text("Comment typed", "“", bx + 112, by, 380, bh, 42, WHITE, 0, d, font=("Helvetica Neue", "Medium"),
                  just="left")
        t0 = 90
        keys = [(0, "“", HOLD)] + [(t0 + j * 105, word_[:j + 1], HOLD) for j in range(1, len(word_))]
        kf(tt["id"], "textContent", keys, vtype="string")
        for j in range(1, len(word_) - 1):
            sfx("sfx-tap", e0 + t0 + j * 105, 0.3, 120)
        sbx, sby = bx + bw - 86, by + 18
        arrow = shape("Send arrow", [(32, 14), (50, 34), (38, 34), (38, 52), (26, 52), (26, 34), (14, 34)], WHITE, 0, d,
                      x=sbx, y=sby)
        send = rect("Send", sbx, sby, 64, 64, [0.16, 0.52, 1.0, 1], 0, d, r=32)
        av = image("Avatar", "avatar", bx + 20, by + 18, 0, d, s=16, radius=200)
        bar = rect("Comment bar", bx, by, bw, bh, [0.11, 0.11, 0.13, 1], 0, d, r=50, stroke=[0.3, 0.3, 0.34, 1], sw=3)
        barg = group("Comment bar", 0, d, [tt, arrow, send, av, bar], x=540, y=by + bh / 2, ax=540, ay=by + bh / 2)
        kf(barg["id"], "scaleX", [(0, 70, LIN), (300, 100, OUT)]); kf(barg["id"], "scaleY", [(0, 70, LIN), (300, 100, OUT)])
        kf(barg["id"], "opacity", [(0, 0, LIN), (160, 100, LIN)])
        kf(send["id"], "opacity", [(m(73.0) - e0, 100, LIN), (m(73.06) - e0, 60, LIN), (m(73.18) - e0, 100, LIN)])
        sfx("sfx-ping", m(73.02), 0.3, 450)
        broll.append(group("CTA comment", e0, d, [barg, rect("CTA bg", 0, 0, W, SEAM, WHITE, 0, d)]))
    elif k == "profile":
        def card(prefix, d_, t_click):
            cx0, cy0, cw, chh = 240, 0, 600, 290
            K = []
            fx, fy = cx0 + 34, cy0 + 200
            cur = shape(prefix + " cursor", [(0, 0), (0, 51), (13, 39), (24, 61), (33, 57), (22, 36), (40, 36)],
                        WHITE, 0, d_, x=fx + 170, y=fy + 90, stroke=[0, 0, 0, 1], sw=2.5)
            if t_click is not None:
                kf(cur["id"], "positionX", [(0, fx + 560, LIN), (t_click - 60, fx + 118, EASE)])
                kf(cur["id"], "positionY", [(0, fy + 260, LIN), (t_click - 60, fy + 26, EASE)])
            K.append(cur)
            fol = rect(prefix + " Follow", fx, fy, 250, 58, [0.25, 0.33, 1.0, 1], 0, d_, r=12)
            K += [text(prefix + " Follow t", "Follow", fx, fy, 250, 58, 26, WHITE, 0, d_),
                  fol,
                  text(prefix + " Msg t", "Message", fx + 262, fy, 196, 58, 26, [0.08, 0.08, 0.1, 1], 0, d_),
                  rect(prefix + " Msg", fx + 262, fy, 196, 58, [0.84, 0.84, 0.87, 1], 0, d_, r=12),
                  rect(prefix + " Icon dot", fx + 494, fy + 17, 14, 14, [0.25, 0.25, 0.28, 1], 0, d_, r=7),
                  rect(prefix + " Icon body", fx + 489, fy + 33, 24, 12, [0.25, 0.25, 0.28, 1], 0, d_, r=6),
                  rect(prefix + " Icon btn", fx + 470, fy, 62, 58, [0.84, 0.84, 0.87, 1], 0, d_, r=12)]
            grey = [0.72, 0.72, 0.76, 1]
            for j, (num, lab) in enumerate([("722", "Posts"), ("108k", "Followers"), ("54", "Following")]):
                xx = cx0 + 170 + j * 130
                K += [text(f"{prefix} {lab}", num, xx, cy0 + 112, 120, 36, 28, WHITE, 0, d_),
                      text(f"{prefix} {lab} l", lab, xx, cy0 + 146, 120, 26, 17, grey, 0, d_,
                           font=("Helvetica Neue", "Medium"))]
            K += [text(prefix + " role", "Sales & Leadership Culture Expert", cx0 + 170, cy0 + 70, 400, 34, 19, grey,
                       0, d_, just="left", font=("Helvetica Neue", "Medium")),
                  shape(prefix + " tick", [(6, 15), (11, 20), (21, 9), (23, 11), (11, 24), (4, 17)], WHITE, 0, d_,
                        x=cx0 + 318, y=cy0 + 22),
                  rect(prefix + " badge", cx0 + 318, cy0 + 22, 28, 28, [0.2, 0.6, 1.0, 1], 0, d_, r=14),
                  text(prefix + " handle", "theamruttbhatt", cx0 + 60, cy0 + 16, 260, 40, 30, WHITE, 0, d_,
                       just="left"),
                  text(prefix + " back", "‹", cx0 + 22, cy0 + 12, 30, 48, 42, WHITE, 0, d_, just="left",
                       font=("Helvetica Neue", "Medium")),
                  image(prefix + " avatar", "avatar", cx0 + 40, cy0 + 72, 0, d_, s=26, radius=200),
                  rect(prefix + " card", cx0, cy0, cw, chh, [0.09, 0.09, 0.11, 1], 0, d_, r=34)]
            return K
        t_click = m(73.95) - e0
        cg = group("Profile card", 0, d, card("P", d, t_click), x=540, y=420, ax=540, ay=145)
        kf(cg["id"], "scaleX", [(0, 70, LIN), (320, 100, OUT)]); kf(cg["id"], "scaleY", [(0, 70, LIN), (320, 100, OUT)])
        kf(cg["id"], "opacity", [(0, 60, LIN), (90, 100, LIN)])
        broll.append(group("Profile end card", e0, d, [cg, rect("Profile bg", 0, 0, W, SEAM, WHITE, 0, d)]))
        sfx("sfx-pop", e0 + 30, 0.35, 200)
        sfx("sfx-click", e0 + t_click, 0.55, 120)
        # final full-screen card (speaker removed), like the Lead Gen reference
        f0 = m(74.45)
        fd = EDIT_DUR - f0
        fg = group("Final card", 0, fd, card("F", fd, None), x=540, y=880, ax=540, ay=145)
        fg["transform"]["scale"] = [165, 165]
        fulls.append(group("Full-screen end card", f0, fd, [fg, rect("End bg", 0, 0, W, H, WHITE, 0, fd)]))
        FULL_WINDOWS.append((f0, EDIT_DUR))

# ---------------------------------------------------------------- title stacks (anchored on the seam)
BIG_GRAD = ([0.36, 0.50, 1.0, 1], [0.13, 0.26, 0.90, 1])
SMALL_GRAD = ([0.50, 0.62, 1.0, 1], [0.30, 0.42, 0.96, 1])
GLOW = {"color": [0.15, 0.25, 0.95, 0.55], "blurRadius": 22, "spreadRadius": 0, "blendMode": "normal",
        "offset": [0, 6]}


def pill_stack(name, t0, t1, small, big, stickers=True):
    st, en = m(t0), m(t1)
    d = en - st
    bs = 96; btw = text_w(big, bs) * 0.93; bw = int(btw + 70); bh = 150
    bx = (W - bw) / 2; by = SEAM - 150
    ss = 47; sw_ = int(text_w(small, ss, bold=False) * 0.97 + 76); sh = 78
    sx = (W - sw_) / 2; sy = by - sh + 22
    big_g = group(name + " big", 0, d, [
        text(name + " big t", big, bx, by, bw, bh - 30, bs, WHITE, 0, d, tr=-30),
        rect(name + " big bg", bx, by, bw, bh, [0.2, 0.33, 0.95, 1], 0, d, r=20, stroke=[1, 1, 1, 0.9], sw=3,
             grad=BIG_GRAD, shadow=GLOW)])
    small_g = group(name + " small", 120, d - 120, [
        text(name + " small t", small, sx, sy, sw_, sh, ss, WHITE, 0, d - 120,
             font=("Helvetica Neue", "Regular"), tr=-10),
        rect(name + " small bg", sx, sy, sw_, sh, [0.4, 0.5, 1, 1], 0, d - 120, r=14, stroke=[1, 1, 1, 0.75], sw=2,
             grad=SMALL_GRAD, shadow=GLOW)])
    for g_, dl in ((big_g, 0), (small_g, 0)):
        kf(g_["id"], "positionY", [(0, 70, LIN), (380, 0, OUT), (d - (120 if g_ is small_g else 0) - 150, 0, LIN),
                                   (d - (120 if g_ is small_g else 0), 40, EASE)])
        kf(g_["id"], "opacity", [(0, 0, LIN), (220, 100, LIN), (d - (120 if g_ is small_g else 0) - 150, 100, LIN),
                                 (d - (120 if g_ is small_g else 0), 0, LIN)])
    kids = [small_g, big_g]
    if stickers:
        c = image(name + " Claude icon", "claude-logo", bx + bw + 32, by + 10, 200, d - 200, s=30, radius=112,
                  rot=14, ax=256, ay=256)
        a = image(name + " Apollo icon", "apollo-logo", bx - 34, by + 84, 320, d - 320, s=52, radius=40, rot=-12,
                  ax=112.5, ay=112.5)
        for L_, s_ in ((c, 30), (a, 52)):
            kf(L_["id"], "scaleX", [(0, 0, LIN), (300, s_ * 1.08, OUT), (420, s_, EASE)])
            kf(L_["id"], "scaleY", [(0, 0, LIN), (300, s_ * 1.08, OUT), (420, s_, EASE)])
        kids += [c, a]       # stickers sit behind the pills
    overlays.append(group(name, st, d, kids))
    sfx("sfx-pop", st + 60, 0.3, 200)


pill_stack("Title", 0.05, 4.9, "Generate Sales Leads", "Apollo + Claude")
pill_stack("Series", 7.0, 11.0, "How To Use AI", "In Sales Series", stickers=False)


def label(name, t0, t1, s_, grad, cy=700):
    st, en = m(t0), m(t1); d = en - st
    size = 54; w = int(text_w(s_, size) + 70); h = 92; x = (W - w) / 2; y = cy - h / 2
    g = group(name, st, d, [text(name + " t", s_, x, y, w, h, size, WHITE, 0, d),
                            rect(name + " bg", x, y, w, h, grad[1], 0, d, r=18, stroke=[1, 1, 1, 0.9], sw=3,
                                 grad=grad, shadow=dict(GLOW, color=[0, 0, 0, 0.35]))],
              x=540, y=cy, ax=540, ay=cy)
    kf(g["id"], "positionY", [(0, cy + 60, LIN), (340, cy, OUT)])
    kf(g["id"], "opacity", [(0, 0, LIN), (200, 100, LIN), (d - 120, 100, LIN), (d, 0, LIN)])
    overlays.append(g)
    sfx("sfx-pop", st + 40, 0.3, 200)


RED_G = ([1.0, 0.42, 0.42, 1], [0.86, 0.16, 0.20, 1])
GRN_G = ([0.30, 0.86, 0.55, 1], [0.08, 0.60, 0.32, 1])
label("Label 500+", 26.5, 28.07, "Skip: 500+ employees", RED_G)
label("Label small", 30.85, 31.95, "Skip: very small", RED_G)
label("Label sweet", 35.0, 37.11, "Target: 50–200", GRN_G)

# ---------------------------------------------------------------- flash / light-leak transitions (top pane)
flashes = []
for t in [6.84, 11.0, 45.17, 51.65, 71.95]:
    c = m(t)
    st = c - 140
    full = any(a <= c + 50 < b for a, b in FULL_WINDOWS) or t == 45.17
    hh = H if full else SEAM
    wf = rect("Flash", 0, 0, W, hh, WHITE, st + 40, 360, op=0)
    kf(wf["id"], "opacity", [(0, 0, LIN), (100, 65, EASE), (360, 0, EASE)])
    leak = rect("Light leak", 0, 0, W * 1.4, hh, WHITE, st - 60, 520, grad=None)
    leak["rect"]["fillPaint"] = {"type": "gradient", "gradientType": "linear", "start": [-W * 0.7, 0],
                                 "end": [W * 0.7, 0],
                                 "stops": [{"offset": 0, "color": [0.55, 0.75, 1.0, 0]},
                                           {"offset": 0.6, "color": [0.55, 0.78, 1.0, 0.85]},
                                           {"offset": 1, "color": [0.9, 0.95, 1.0, 0]}]}
    kf(leak["id"], "positionX", [(0, W, LIN), (420, -W * 0.5, EASE)])
    kf(leak["id"], "opacity", [(0, 0, LIN), (120, 100, LIN), (420, 0, EASE)])
    flashes += [wf, leak]
    if t in (6.84, 51.65, 71.95):
        sfx("sfx-impact", c - 40, 0.55, 900)
    else:
        sfx("sfx-whoosh", c - 220, 0.25, 450)
sfx("sfx-riser", 0, 0.32, 1100)

# ---------------------------------------------------------------- speaker (fixed framing, graded)
speaker = []
for j, (a, b, e) in enumerate(seg_edit):
    speaker.append({"type": "Video", "id": nid(), "name": f"Talking head {j+1}", "blendMode": "normal",
                    "activeRange": rng(round(e * 1000), round((b - a) * 1000)),
                    "sourceRange": rng(round(a * 1000), round((b - a) * 1000)),
                    "sourceIntrinsicDuration": SRC_DUR, "volume": 0.0,
                    "transform": tf(-470, SEAM - 32, 102),
                    "effects": [{"id": nid(), "effect": dict(type="levels", **LEVELS)}],
                    "source": {"assetId": "footage-1", "fit": "contain"}})
# hold the last frame under the full-screen end card (keeps the tail clean if the card is removed)

# ---------------------------------------------------------------- captions (measured: HN Bold 47, black 45 %)
s = open(SRT, encoding="utf-8").read().replace("\r", "")


def ts_(t):
    h, mm, r = t.split(":"); sec, ms = r.split(",")
    return int(h) * 3600 + int(mm) * 60 + int(sec) + int(ms) / 1000


cues = []
for blk in re.split(r"\n\s*\n", s.strip()):
    Ls = [l for l in blk.split("\n") if l.strip()]
    mt = re.match(r"(\S+) --> (\S+)", Ls[1])
    tx = re.sub(r"\(Transcribed by TurboScribe[^)]*\)\s*", "", " ".join(Ls[2:])).strip()
    if not tx:
        continue
    if tx.startswith("-") and cues:
        a0, _, t0 = cues.pop(); cues.append((a0, ts_(mt.group(2)), t0 + tx)); continue
    cues.append((ts_(mt.group(1)), ts_(mt.group(2)), tx))
WEAK = {"the", "a", "and", "to", "over", "their", "on", "in", "of", "for", "i'll", "your", "that", "it", "one",
        "who", "few", "single", "very"}


def nw(c): return len(c[2].split())


def weak_end(c): return c[2].split()[-1].lower().strip(",.") in WEAK


groups, cur = [], []
for i, c in enumerate(cues):
    cur.append(c)
    words = sum(nw(x) for x in cur)
    gap = cues[i + 1][0] - c[1] if i + 1 < len(cues) else 9
    nxt_w = nw(cues[i + 1]) if i + 1 < len(cues) else 0
    end_punct = bool(re.search(r"[.?!]$", c[2])) or (c[2].endswith(",") and words >= 2)
    if end_punct or gap > 0.25 or words + nxt_w > 3:
        if weak_end(c) and len(cur) > 1 and not end_punct:
            carry = cur.pop()
            groups.append(cur); cur = [carry]
        elif not weak_end(c) or end_punct or words >= 4:
            groups.append(cur); cur = []
if cur:
    groups.append(cur)
phr = [[g[0][0], g[-1][1], " ".join(x[2] for x in g)] for g in groups]
caps = []
CS = 47
phr = [p for p in phr if not any(ca <= (p[0] + p[1]) / 2 <= cb for ca, cb in LINE_CUTS)]
for i, (a, b, t) in enumerate(phr):
    st = m(a)
    nx = m(phr[i + 1][0]) if i + 1 < len(phr) else SPEECH_MS
    en = nx if nx - m(b) < 450 else m(b) + 180
    en = min(max(en, st + 250), SPEECH_MS, FULL_WINDOWS[-1][0])
    in_full = any(a_ <= st < b_ for a_, b_ in FULL_WINDOWS)
    if in_full and st >= FULL_WINDOWS[-1][0]:
        continue                     # end card is caption-free, as in the reference
    cy = 1480 if in_full else SEAM
    w = int(text_w(t, CS) + 44); h = 80
    x = (W - w) / 2; y = cy - h / 2
    ct = text(f"Cap {i+1}", t, x, y, w, h, CS, WHITE, st, en - st)
    ct["sourceText"].update(applyStroke=True, strokeColor=[0, 0, 0, 0.35], strokeWidth=2, strokeOverFill=False)
    caps += [ct,
             rect(f"Cap {i+1} pill", x, y, w, h, [0, 0, 0, 0.45], st, en - st, r=14)]
captions = group("Captions", 0, EDIT_DUR, caps)

# ---------------------------------------------------------------- audio
audio = []


def aud(name, asset, st, d, src_st, intrinsic, vol):
    audio.append({"type": "Audio", "id": nid(), "name": name, "activeRange": rng(st, d),
                  "sourceRange": rng(src_st, d), "sourceIntrinsicDuration": intrinsic,
                  "source": {"assetId": asset}, "volume": vol, "captionsEnabled": False, "windowMs": 50})


for j, (a, b, e) in enumerate(seg_edit):
    aud(f"Dialogue {j+1}", "dialogue-norm", round(e * 1000), round((b - a) * 1000), round(a * 1000), SRC_DUR, 1.0)
DUR = {"sfx-whoosh": 450, "sfx-pop": 200, "sfx-ping": 450, "sfx-tap": 120, "sfx-click": 120, "sfx-impact": 900,
       "sfx-riser": 1100}
for asset, st, vol, d in SFX:
    d = min(DUR[asset], EDIT_DUR - st)
    if d > 20:
        aud(f"SFX {asset} @{st}", asset, st, d, 0, DUR[asset], vol)

layers = ([captions] + list(reversed(fulls)) + flashes + list(reversed(overlays)) + list(reversed(broll)) + speaker
          + audio)
doc = {"$schema": "https://jerboa.dev/schemas/fx-composition/editable/v1/document.schema.json", "formatVersion": 1,
       "dimensions": {"width": W, "height": H}, "duration": EDIT_DUR / 1000,
       "composition": {"id": "main", "name": "Main", "layers": layers}}
json.dump(doc, open(".tesseract-work/editable_v32.json", "w"), indent=1, ensure_ascii=False)
json.dump(anims, open(".tesseract-work/anim_v32.json", "w"), indent=1, ensure_ascii=False)
print(f"edit {EDIT_DUR/1000:.2f}s (speech {SPEECH_MS/1000:.2f}s), {len(keeps)} segs, {len(phr)} captions, "
      f"{len(anims)} anim, {len(SFX)} sfx, full windows {FULL_WINDOWS}")
