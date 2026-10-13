#!/usr/bin/env python3
"""Hermes x Bluehost reel (1080x1920) in the Farhan v4 style: SPLIT (B-roll / native graphic top, Farhan zoomed
bottom), full-screen B-roll, full-screen Farhan with titles, native motion graphics, dot-matrix ALL-CAPS captions.
All text tracking -1. Writes editable.json + anim.json (commit, then apply)."""
import json, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from timing import seg_edit, m, ms, DUR, SPEECH, cues, ROOT  # noqa: E402
from beats import BEATS, clip_size, SPLIT_Y, CAP_Y  # noqa: E402

W, H = 1080, 1920
SRC_MS = 39480
DUR_MS, SPEECH_MS = int(round(DUR * 1000)), int(round(SPEECH * 1000))
CLIP_MS = json.load(open(os.path.join(HERE, "clip_ms.json")))
WHITE, INK, CORAL, CORAL_LT = [1, 1, 1, 1], [0.106, 0.102, 0.094, 1], [0.816, 0.412, 0.31, 1], [0.98, 0.56, 0.42, 1]
CREAM, RULE, GREEN = [0.95, 0.93, 0.89, 1], [0.89, 0.86, 0.81, 1], [0.24, 0.75, 0.42, 1]
PLEK = ("FoundryPlekW01-Regular", "Regular")
HB, HR, BI = ("Helvetica", "Bold"), ("Helvetica", "Regular"), ("Baskerville", "Italic")
TR = -1                                   # character spacing on every text layer (user request)
_id, _k, anims = [1], [0], []
LIN = {"type": "linear"}
OUT = {"type": "cubicBezier", "x1": 0.16, "y1": 1, "x2": 0.3, "y2": 1}
GRADE = [{"type": "levels", "inputBlack": 4.0, "inputWhite": 242.0, "gamma": 1.05, "outputBlack": 6.0, "outputWhite": 255.0},
         {"type": "temperatureTint", "temperature": 6, "tint": 0},
         {"type": "vibrance", "vibrance": 8, "saturation": 0}]
SOFT_SH = {"color": [0.16, 0.10, 0.04, 0.35], "blurRadius": 44, "spreadRadius": 0, "blendMode": "normal", "offset": [0, 16]}
TXT_SH = {"color": [0, 0, 0, 0.8], "blurRadius": 30, "spreadRadius": 0, "blendMode": "normal", "offset": [0, 6]}


def nid():
    _id[0] += 1
    return _id[0]


def tf(x=0, y=0, s=100, ax=0, ay=0, op=100, rot=0):
    return {"anchorPoint": [ax, ay], "position": [x, y], "scale": [s, s], "rotation": rot, "opacity": op}


def rng(s, d):
    return {"start": int(s), "duration": int(max(1, d))}


def kf(lid, prop, keys):
    out = []
    for t, v, e in keys:
        _k[0] += 1
        out.append({"id": f"k{_k[0]}", "layerTime": int(t), "value": {"type": "float", "value": v}, "easing": e})
    anims.append({"type": "setFxPropertyKeyframes", "compositionId": "main",
                  "property": {"layerId": lid, "propertyType": prop}, "keyframes": out})


def kfg(L, prop, keys):
    """Keyframes given in beat (parent) time; converted to the layer's own clock."""
    s0 = L["activeRange"]["start"]
    kf(L["id"], prop, [(t - s0, v, e) for t, v, e in keys])


def rect(name, x, y, w, h, fill, st, d, r=0, shadow=None, stroke=None, sw=0):
    R = {"size": [w, h], "fillColor": fill, "roundness": r}
    if stroke:
        R.update(strokeEnabled=True, strokeColor=stroke, strokeWidth=sw)
    L = {"type": "Rect", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d), "transform": tf(x, y),
         "rect": R}
    if shadow:
        L["dropShadow"] = shadow
    return L


def text(name, s, x, y, w, h, size, color, st, d, font, shadow=None, just="center"):
    L = {"type": "Text", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d), "transform": tf(x, y),
         "sourceText": {"text": s, "fontFamily": font[0], "fontStyle": font[1], "fontSize": size, "fillColor": color,
                        "strokeWidth": 0, "justification": just, "boxText": True, "boxPosition": [0, 0],
                        "boxSize": [w, h], "verticalAlign": "center", "tracking": TR}}
    if shadow:
        L["dropShadow"] = shadow
    return L


def shape(name, cmds_pts, x, y, st, d, color=WHITE, sw=7):
    """cmds_pts: list of polylines; each polyline is a list of points."""
    cmds = []
    for pts in cmds_pts:
        cmds += [{"type": "moveTo", "x": pts[0][0], "y": pts[0][1]}] + [{"type": "lineTo", "x": a, "y": b} for a, b in pts[1:]]
    return {"type": "Shape", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d), "transform": tf(x, y),
            "shape": {"path": {"commands": cmds}, "fills": [],
                      "strokes": [{"paint": {"type": "solid", "color": color}, "width": sw, "cap": "round", "join": "round",
                                   "miterLimit": 4, "blendMode": "normal", "opacity": 100}]}}


def group(name, st, d, layers, x=0, y=0, ax=0, ay=0):
    return {"type": "Group", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
            "transform": tf(x, y, 100, ax, ay), "layers": layers}


def rr_mask(x0, y0, x1, y1, r):
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    cmds = [{"type": "moveTo", "x": pts[0][0], "y": pts[0][1], "cornerRadius": r}] + \
           [{"type": "lineTo", "x": px, "y": py, "cornerRadius": r} for px, py in pts[1:]] + [{"type": "close"}]
    return [{"id": nid(), "mode": "add", "opacity": 100, "inverted": False, "path": {"commands": cmds}}]


def fvideo(name, st, d, src_ms, x, y, s, masks=None, ax=0, ay=0, asset="aroll", intrinsic=SRC_MS):
    L = {"type": "Video", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
         "sourceRange": rng(src_ms, d), "sourceIntrinsicDuration": intrinsic, "volume": 0.0,
         "transform": tf(x, y, s, ax, ay), "source": {"assetId": asset, "fit": "contain"},
         "effects": [{"id": nid(), "effect": dict(e)} for e in GRADE]}
    if masks:
        L["masks"] = masks
    return L


def bvideo(name, asset, st, d, x, y, w, h, push=2.0, radius=None):
    """B-roll clip (pre-cut to w x h), centred anchor, slow push-in."""
    L = {"type": "Video", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
         "sourceRange": rng(0, min(d, CLIP_MS[asset])), "sourceIntrinsicDuration": CLIP_MS[asset], "volume": 0.0,
         "transform": tf(x + w / 2, y + h / 2, 100, w / 2, h / 2), "source": {"assetId": asset, "fit": "contain"}}
    if radius:
        L["masks"] = rr_mask(0, 0, w, h, radius)
    for p in ("scaleX", "scaleY"):
        kf(L["id"], p, [(0, 100, LIN), (d, 100 + push, LIN)])
    return L


def rise(L, d=260, dy=40, at=0):
    y0 = L["transform"]["position"][1]
    at = max(at, L["activeRange"]["start"])
    kfg(L, "opacity", [(at, 0, LIN), (at + int(d * 0.6), 100, LIN)])
    kfg(L, "positionY", [(at, y0 + dy, LIN), (at + d, y0, OUT)])


def pop(L, at=0, s0=125, d=260):
    """Scale-in from s0 around the layer's centre (box text / rect), with a fade."""
    if L["type"] == "Text":
        w_, h_ = L["sourceText"]["boxSize"]
    else:
        w_, h_ = L["rect"]["size"]
    x_, y_ = L["transform"]["position"]
    L["transform"]["anchorPoint"] = [w_ / 2, h_ / 2]
    L["transform"]["position"] = [x_ + w_ / 2, y_ + h_ / 2]
    at = max(at, L["activeRange"]["start"])
    for p in ("scaleX", "scaleY"):
        kfg(L, p, [(at, s0, LIN), (at + d, 100, OUT)])
    kfg(L, "opacity", [(at, 0, LIN), (at + 120, 100, LIN)])


def wipe_x(L, at, d=240):
    """Grow a horizontal bar from its left edge."""
    L["transform"]["anchorPoint"] = [0, L["rect"]["size"][1] / 2]
    L["transform"]["position"][1] += L["rect"]["size"][1] / 2
    kfg(L, "scaleX", [(at, 0, LIN), (at + d, 100, OUT)])


EYE = (895, 450)                 # Farhan's eye midpoint in the 1920x1080 source
segi = {(a, b): j for j, (a, b, e) in enumerate(seg_edit)}
FS = 185                         # full-frame scale


def farhan(fa, fb, g0, mode, **kw):
    """Farhan video layers for source window [fa,fb], times relative to the beat group start g0.
    Jump cuts (pause trims) alternate framing so every trim reads as a deliberate punch."""
    out = []
    span = ms(fb) - g0
    for a, b, e in seg_edit:
        lo, hi = max(a, fa), min(b, fb)
        if hi - lo <= 0.01:
            continue
        j = segi[(a, b)]
        st, d, src = ms(lo) - g0, int(round((hi - lo) * 1000)), int(round(lo * 1000))
        if mode == "split":      # zoomed-in Farhan, eyes held at (540, 1290)
            s = 1.25 if j % 2 == 0 else 1.36
            x, y = 540 - EYE[0] * s, 1290 - EYE[1] * s
            L = fvideo("Farhan (split)", st, d, src, x, y, s * 100,
                       rr_mask(-x / s, (SPLIT_Y - y) / s, (W - x) / s, (H - y) / s, 0))
        else:                    # full-screen, eyes at (540, 774), slow push-in (hook: zoom-out reveal)
            base = FS + (12 if (j % 2 and not kw.get("hook")) else 0) + kw.get("extra", 0)
            L = fvideo("Farhan (full)", st, d, src, 540, 774, base, ax=EYE[0], ay=EYE[1])
            if kw.get("hook") and st == 0:
                keys = [(0, 225, LIN), (560, base, OUT), (d, base + 4 * d / span, LIN)]
            else:
                keys = [(0, base + 5 * st / span, LIN), (d, base + 5 * (st + d) / span, LIN)]
            for p in ("scaleX", "scaleY"):
                kf(L["id"], p, keys)
        out.append(L)
    return out


def grid(d):
    """Cream page with a faint 72 px grid (top pane)."""
    lines = [[(x, 0), (x, SPLIT_Y)] for x in range(36, W, 72)] + [[(0, y), (W, y)] for y in range(48, SPLIT_Y, 72)]
    g = shape("Grid", lines, 0, 0, 0, d, color=[0.55, 0.45, 0.35, 0.10], sw=2)
    return [g, rect("Cream page", 0, 0, W, SPLIT_Y, CREAM, 0, d)]


def card(name, x, y, w, h, st, d, r=30):
    return rect(name, x, y, w, h, WHITE, st, d, r=r, shadow=SOFT_SH, stroke=RULE, sw=3)


SFX = []          # (edit ms, preset, volume)


def at_(t, g0):
    return max(0, ms(t) - g0)


# ------------------------------------------------------------------ native top-pane graphics
def g_loop(g0, d):
    """learns -> every task -> own skills: a self-improvement loop around HERMES."""
    L = []
    nodes = [("LEARNS", 540, 190, 7.00), ("EVERY TASK", 820, 640, 8.20), ("OWN SKILLS", 260, 640, 9.40)]
    for k, (lab, cx, cy, t) in enumerate(nodes):
        a = at_(t, g0)
        c = card(f"Node {lab}", cx - 180, cy - 64, 360, 128, a, d - a, r=64)
        n = text(f"Node {lab} num", f"0{k + 1}", cx - 160, cy - 64, 90, 128, 40, CORAL, a, d - a, PLEK, just="left")
        t_ = text(f"Node {lab} label", lab, cx - 90, cy - 64, 250, 128, 40, INK, a, d - a, PLEK, just="left")
        for X in (c, n, t_):
            rise(X, 300, 30, a)
        L = [n, t_, c] + L
        SFX.append((g0 + a, "soft-pop", 0.18))
    # arrows between nodes (drawn as they become relevant)
    arrows = [((690, 270), (800, 560), 8.20), ((640, 640), (440, 640), 9.40), ((300, 560), (420, 270), 9.90)]
    for k, ((x0, y0), (x1, y1), t) in enumerate(arrows):
        a = at_(t, g0) + 80
        import math
        ang = math.atan2(y1 - y0, x1 - x0)
        hx = [(x1 - 26 * math.cos(ang - 0.5), y1 - 26 * math.sin(ang - 0.5)), (x1, y1),
              (x1 - 26 * math.cos(ang + 0.5), y1 - 26 * math.sin(ang + 0.5))]
        ar = shape(f"Arrow {k + 1}", [[(x0, y0), (x1, y1)], hx], 0, 0, a, d - a, color=CORAL, sw=7)
        kfg(ar, "opacity", [(a, 0, LIN), (a + 180, 100, LIN)])
        L.insert(0, ar)
    hub = text("Hub", "Hermes", 340, 400, 400, 140, 96, CORAL, 0, d, BI)
    pop(hub, 0, 115)
    a = at_(10.00, g0)
    plus = rect("+1 skill pill", 120, 760, 280, 84, CORAL, a, d - a, r=42)
    plus_t = text("+1 skill", "+1 SKILL", 120, 760, 280, 84, 40, WHITE, a, d - a, PLEK)
    pop(plus, a); pop(plus_t, a)
    SFX.append((g0 + a, "clear-ping", 0.22))
    return [plus_t, plus] + L + [hub]


def g_nosub(g0, d):
    """Claude plan included / other subscription struck through -> $0 extra."""
    L = []
    c = card("Plan card", 110, 170, 860, 400, 0, d)
    rise(c)
    r1 = text("Row 1", "CLAUDE PLAN", 160, 200, 560, 150, 52, INK, 0, d, PLEK, just="left")
    ok = rect("Row 1 tick bg", 820, 235, 90, 80, GREEN, 120, d - 120, r=40)
    tick = shape("Row 1 tick", [[(842, 276), (858, 292), (888, 258)]], 0, 0, 120, d - 120, color=WHITE, sw=8)
    for X in (r1,):
        rise(X, 300, 24)
    pop(ok, 120); kfg(tick, "opacity", [(120, 0, LIN), (260, 100, LIN)])
    rule = rect("Row rule", 160, 368, 760, 3, RULE, 0, d)
    a2 = at_(14.52, g0)
    r2 = text("Row 2", "OTHER SUBSCRIPTION", 160, 390, 760, 150, 52, INK, a2, d - a2, PLEK, just="left")
    rise(r2, 300, 24, a2)
    a3 = at_(14.95, g0)
    strike = rect("Strike", 150, 459, 780, 10, CORAL, a3, d - a3, r=5)
    wipe_x(strike, a3, 260)
    SFX.append((g0 + a3, "dry-click", 0.24))
    a4 = at_(15.15, g0)
    zero = text("$0 extra", "$0 EXTRA", 40, 620, 1000, 220, 150, CORAL, a4, d - a4, PLEK, shadow=None)
    pop(zero, a4, 130)
    SFX.append((g0 + a4, "soft-impact", 0.30))
    SFX.append((g0 + 40, "soft-pop", 0.18))
    return [zero, strike, tick, ok, r2, r1, rule, c]


def g_skills(g0, d):
    """Repeat asks pile up, then collapse into one saved skill (fetch_job, as seen in the Telegram B-roll)."""
    L = []
    times = [31.56, 32.10, 32.52]
    for k, t in enumerate(times):
        a = at_(t, g0)
        y = 110 + k * 118
        b = rect(f"Ask {k + 1}", 470, y, 520, 96, [0.88, 0.96, 0.82, 1], a, d - a, r=26, shadow=SOFT_SH)
        tx = text(f"Ask {k + 1} text", "Find me new AI jobs", 500, y, 470, 96, 40, INK, a, d - a, HR, just="left")
        for X in (b, tx):
            rise(X, 260, 30, a)
        fade = at_(34.30, g0)
        for X in (b, tx):
            kfg(X, "opacity", [(a, 0, LIN), (a + 160, 100, LIN), (fade, 100, LIN), (fade + 250, 30, LIN)])
        L = [tx, b] + L
        SFX.append((g0 + a, "soft-tap", 0.18))
    a = at_(33.14, g0)
    x3 = text("Repeat x3", "x3", 120, 160, 300, 260, 200, CORAL, a, d - a, PLEK)
    pop(x3, a, 140)
    lab = text("Repeat label", "REPEAT", 120, 380, 300, 70, 40, INK, a, d - a, PLEK)
    rise(lab, 260, 20, a)
    SFX.append((g0 + a, "soft-impact", 0.26))
    a = at_(34.58, g0)
    sc = card("Skill card", 120, 560, 840, 250, a, d - a, r=36)
    icon = rect("Skill icon", 160, 610, 150, 150, CORAL, a, d - a, r=34)
    icon_t = text("Skill icon text", "fx", 160, 610, 150, 150, 84, WHITE, a, d - a, BI)
    k1 = text("Skill kicker", "SKILL SAVED", 350, 600, 560, 70, 38, CORAL, a, d - a, PLEK, just="left")
    k2 = text("Skill name", "fetch_job", 350, 660, 580, 110, 76, INK, a, d - a, HB, just="left")
    for X in (sc, icon, icon_t, k1, k2):
        rise(X, 320, 40, a)
    SFX.append((g0 + a, "clear-ping", 0.24))
    return [k2, k1, icon_t, icon, sc, lab, x3] + L


def g_nodocker(g0, d):
    """Over full-frame Farhan: DOCKER / SSL SETUP pills, each struck through as he says it."""
    L = []
    for k, (lab, t, ts) in enumerate([("DOCKER", 23.32, 23.80), ("SSL SETUP", 24.14, 24.95)]):
        a, s_ = at_(t, g0), at_(ts, g0)
        x = 70 + k * 480
        p = rect(f"Pill {lab}", x, 150, 460, 130, WHITE, a, d - a, r=65, shadow=SOFT_SH)
        tx = text(f"Pill {lab} text", lab, x, 150, 460, 130, 52, INK, a, d - a, PLEK)
        pop(p, a, 120); pop(tx, a, 120)
        st = rect(f"Strike {lab}", x + 30, 210, 400, 10, CORAL, s_, d - s_, r=5)
        wipe_x(st, s_, 220)
        L = [st, tx, p] + L
        SFX.extend([(g0 + a, "soft-pop", 0.20), (g0 + s_, "dry-click", 0.26)])
    no = text("No", "No setup.", 40, 300, 1000, 170, 120, CORAL_LT, at_(24.95, g0), d - at_(24.95, g0), BI, TXT_SH)
    rise(no, 280, 30, at_(24.95, g0))
    return [no] + L


GRAPHICS = {"loop": g_loop, "nosub": g_nosub, "skills": g_skills, "nodocker": g_nodocker}

# ------------------------------------------------------------------ beats
ALIAS = {"b08": "b08r", "b09": "b09r"}
beat_groups, cap_y_ranges, cap_off = [], [], []
for bi, (fa, fb, lay, clip, opt) in enumerate(BEATS):
    fb = min(fb, 39.40)
    g0 = ms(fa)
    g1 = DUR_MS if bi == len(BEATS) - 1 else ms(fb)
    d = g1 - g0
    L, top = [], []
    asset = f"b{bi:02d}" if clip else None
    if asset in ALIAS:                      # re-cut clips imported under a new asset id
        CLIP_MS[ALIAS[asset]] = CLIP_MS[asset]
        asset = ALIAS[asset]
    cap_y_ranges.append((g0, g1, CAP_Y[lay]))
    if "title" in opt or "punch" in opt or opt.get("graphic") == "nodocker":
        cap_off.append((g0, g1))
    if bi:
        SFX.append((g0 - 180, "air-whoosh", 0.16) if bi % 2 else (g0, "soft-tap", 0.14))
    if lay == "SPLIT":
        pane = []
        if clip:
            fit = clip[3]
            w, h = clip_size(fit, clip[2])
            if fit == "cover":
                pane.append(bvideo("B-roll top", asset, 0, d, 0, 0, w, h, push=2))
            else:
                wx, wy = (W - w) / 2, (SPLIT_Y - h) / 2
                win = bvideo("Window", asset, 0, d, wx, wy, w, h, push=1.5, radius=26)
                frame = rect("Window frame", wx - 3, wy - 3, w + 6, h + 6, WHITE, 0, d, r=29, shadow=SOFT_SH)
                for X in (win, frame):
                    rise(X)
                pane += [win, frame]
                SFX.append((g0 + 40, "soft-pop", 0.18))
        if "graphic" in opt:
            pane = GRAPHICS[opt["graphic"]](g0, d) + pane
        for (hx, hy, hw, hh), t in opt.get("hl", []):
            a_ = at_(t, g0)
            hl = rect("Highlight", hx, hy, hw, hh, [1, 1, 1, 0], a_, d - a_, r=14, stroke=CORAL, sw=6)
            kfg(hl, "opacity", [(a_, 0, LIN), (a_ + 150, 100, LIN)])
            top.append(hl)
            SFX.append((g0 + a_, "dry-click", 0.2))
        if "stamp" in opt:
            lab, t = opt["stamp"]
            a_ = at_(t, g0)
            dim = rect("Dim", 0, 0, W, SPLIT_Y, [0, 0, 0, 0.5], a_, d - a_)
            kfg(dim, "opacity", [(a_, 0, LIN), (a_ + 150, 100, LIN)])
            box = rect("Stamp box", 290, 360, 500, 220, [1, 1, 1, 0], a_, d - a_, r=24, stroke=CORAL_LT, sw=10)
            st_t = text("Stamp", lab, 290, 360, 500, 220, 150, CORAL_LT, a_, d - a_, PLEK)
            for X in (box, st_t):
                pop(X, a_, 150, 220)
                X["transform"]["rotation"] = -7
            top += [st_t, box, dim]
            SFX.append((g0 + a_, "soft-impact", 0.34))
        if "badge" in opt:
            lab, t = opt["badge"]
            a_ = at_(t, g0)
            b_ = rect("Badge", 640, 640, 360, 170, CORAL, a_, d - a_, r=85, shadow=SOFT_SH)
            b_t = text("Badge text", lab, 640, 640, 360, 170, 104, WHITE, a_, d - a_, PLEK)
            pop(b_, a_, 140); pop(b_t, a_, 140)
            top += [b_t, b_]
            SFX.append((g0 + a_, "soft-impact", 0.30))
        L += top + [rect("Seam", 0, SPLIT_Y - 2, W, 4, CREAM, 0, d)] + farhan(fa, fb, g0, "split") + pane + grid(d) + \
            [rect("Black", 0, 0, W, H, [0, 0, 0, 1], 0, d)]
    elif lay == "BROLL":
        if "live" in opt:
            a_ = at_(opt["live"], g0)
            pill = rect("Live pill", 360, 230, 360, 110, WHITE, a_, d - a_, r=55, shadow=SOFT_SH)
            dot = rect("Live dot", 400, 263, 44, 44, GREEN, a_, d - a_, r=22)
            lt = text("Live text", "LIVE", 450, 230, 240, 110, 56, INK, a_, d - a_, PLEK)
            for X in (pill, dot, lt):
                pop(X, a_, 130)
            kfg(dot, "opacity", [(a_, 0, LIN), (a_ + 120, 100, LIN), (a_ + 600, 35, LIN), (a_ + 1000, 100, LIN)])
            top += [lt, dot, pill]
            SFX.append((g0 + a_, "clear-ping", 0.24))
        L += top + [bvideo("B-roll full", asset, 0, d, 0, 0, 1080, 1920, push=2)]
        SFX.append((g0 + 60, "soft-pop", 0.16))
    elif lay == "FULL":
        L += farhan(fa, fb, g0, "full", hook=opt.get("hook", False), extra=18 if "punch" in opt else 0)
        if "graphic" in opt:
            top += GRAPHICS[opt["graphic"]](g0, d)
        if "title" in opt:
            l1, l2, t1, t2 = opt["title"]
            a1, a2 = at_(t1, g0), at_(t2, g0)
            T1 = text("Title line 1", l1, 40, 200, 1000, 100, 70, WHITE, a1, d - a1, HB, TXT_SH)
            T2 = text("Title line 2", l2, 20, 290, 1040, 190, 140 if len(l2) <= 14 else 124, CORAL_LT, a2, d - a2, BI, TXT_SH)
            rise(T1, at=a1); rise(T2, at=a2)
            top += [T1, T2]
            SFX.append((g0 + a2, "soft-impact", 0.32))
        if "punch" in opt:
            lab, t = opt["punch"]
            a_ = at_(t, g0)
            P = text("Punch", lab, 20, 250, 1040, 200, 150, WHITE, a_, d - a_, BI, TXT_SH)
            pop(P, a_, 120)
            top.append(P)
            SFX.append((g0 + a_, "soft-impact", 0.30))
        if top:
            shade = rect("Top shade", 0, 0, W, 900, [0, 0, 0, 1], 0, d)
            shade["rect"]["fillPaint"] = {"type": "gradient", "gradientType": "linear", "start": [0, 0], "end": [0, 900],
                                          "stops": [{"offset": 0, "color": [0, 0, 0, 0.5]}, {"offset": 1, "color": [0, 0, 0, 0]}]}
            top.append(shade)
        L = top + L
    else:  # CTA: Farhan full + comment box typing DEPLOY, Farhan held on the last frame through the tail
        fl = farhan(fa, fb, g0, "full")
        last = fl[-1]
        t0_ = last["activeRange"]["start"] + last["activeRange"]["duration"]
        tail = fvideo("Farhan (tail hold)", t0_, d - t0_, 0, 540, 774, last["transform"]["scale"][0], ax=EYE[0], ay=EYE[1],
                      asset="aroll-tail", intrinsic=CLIP_MS["aroll-tail"])
        fl.append(tail)
        a1, a2 = at_(37.24, g0), at_(37.62, g0)
        t0 = at_(37.95, g0)
        click = at_(38.95, g0)
        c1 = text("CTA line 1", "Comment", 40, 120, 1000, 100, 70, WHITE, a1, d - a1, HB, TXT_SH)
        c2 = text("CTA line 2", "“Deploy”", 20, 200, 1040, 180, 140, CORAL_LT, a2, d - a2, BI, TXT_SH)
        rise(c1, at=a1); rise(c2, at=a2)
        box = rect("Comment box", 110, 410, 860, 116, WHITE, a2 + 150, d - a2 - 150, r=58, shadow=SOFT_SH, stroke=RULE, sw=3)
        rise(box, at=a2 + 150)
        ph = text("Placeholder", "Add a comment...", 155, 410, 600, 116, 38, [0.64, 0.61, 0.56, 1], a2 + 150, t0 - a2 - 150,
                  HR, just="left")
        word = "DEPLOY"
        typed = [text(f"Typed {k}", word[:k], 155, 412, 600, 116, 50, INK, t0 + (k - 1) * 90,
                      (t0 + k * 90 if k < len(word) else d) - (t0 + (k - 1) * 90), PLEK, just="left")
                 for k in range(1, len(word) + 1)]
        send = rect("Send", 870, 427, 82, 82, CORAL, a2 + 150, click + 160 - a2 - 150, r=41)
        arrow = shape("Send arrow", [[(41, 60), (41, 22)], [(25, 38), (41, 22), (57, 38)]], 870, 427, a2 + 150,
                      click + 160 - a2 - 150)
        done = rect("Sent", 870, 427, 82, 82, GREEN, click + 160, d - click - 160, r=41)
        tick = shape("Sent tick", [[(24, 42), (36, 54), (58, 29)]], 870, 427, click + 160, d - click - 160)
        for X in (done, tick):
            kfg(X, "opacity", [(click + 160, 0, LIN), (click + 280, 100, LIN)])
        cur_pts = [(0, 0), (0, 44), (11, 34), (19, 52), (27, 48), (19, 31), (33, 31), (0, 0)]
        cur = shape("Cursor", [cur_pts], 0, 0, click - 700, 900, color=INK, sw=4)
        curf = {"type": "Shape", "id": nid(), "name": "Cursor fill", "blendMode": "normal", "activeRange": rng(click - 700, 900),
                "transform": tf(0, 0), "shape": {"path": json.loads(json.dumps(cur["shape"]["path"])),
                "fills": [{"paint": {"type": "solid", "color": WHITE}, "fillRule": "nonZeroWinding", "blendMode": "normal",
                           "opacity": 100}], "strokes": []}}
        for X in (cur, curf):
            kfg(X, "positionX", [(click - 700, 1010, LIN), (click - 100, 918, OUT)])
            kfg(X, "positionY", [(click - 700, 700, LIN), (click - 100, 472, OUT)])
            kfg(X, "opacity", [(click - 700, 0, LIN), (click - 580, 100, LIN), (click + 80, 100, LIN), (click + 200, 0, LIN)])
            kfg(X, "scaleX", [(click - 10, 100, LIN), (click + 40, 82, LIN), (click + 100, 100, LIN)])
            kfg(X, "scaleY", [(click - 10, 100, LIN), (click + 40, 82, LIN), (click + 100, 100, LIN)])
        shade = rect("Top shade", 0, 0, W, 900, [0, 0, 0, 1], 0, d)
        shade["rect"]["fillPaint"] = {"type": "gradient", "gradientType": "linear", "start": [0, 0], "end": [0, 900],
                                      "stops": [{"offset": 0, "color": [0, 0, 0, 0.5]}, {"offset": 1, "color": [0, 0, 0, 0]}]}
        L = [cur, curf, tick, done, arrow, send] + typed + [ph, box, c1, c2, shade] + fl
        for k in range(len(word)):
            SFX.append((g0 + t0 + k * 90, "dry-click", 0.16))
        SFX += [(g0 + a2 + 150, "soft-pop", 0.22), (g0 + click, "dry-click", 0.3), (g0 + click + 150, "clear-ping", 0.26)]
    beat_groups.append(group(f"Beat {bi + 1:02d} {lay}" + (f" {opt['graphic']}" if 'graphic' in opt else ""), g0, d, L))


# ------------------------------------------------------------------ captions (dot-matrix, ALL CAPS, white on black 55 %, coral keys)
def plek_advances():
    d = open(os.path.join(ROOT, "Assets", "fonts", "Foundry Plek W01 Regular.ttf"), "rb").read()
    T = {}
    for i in range(struct.unpack(">H", d[4:6])[0]):
        t, c, o, l = struct.unpack(">4sIII", d[12 + 16 * i:28 + 16 * i]); T[t] = o
    co = T[b"cmap"]
    for i in range(struct.unpack(">H", d[co + 2:co + 4])[0]):
        pid, eid, off = struct.unpack(">HHI", d[co + 4 + 8 * i:co + 12 + 8 * i])
        if pid == 3 and eid == 1:
            so = co + off
    n2 = struct.unpack(">H", d[so + 6:so + 8])[0]; n = n2 // 2
    ends = struct.unpack(f">{n}H", d[so + 14:so + 14 + n2]); p = so + 16 + n2
    starts = struct.unpack(f">{n}H", d[p:p + n2]); p += n2
    deltas = struct.unpack(f">{n}h", d[p:p + n2]); ro = p + n2
    ranges = struct.unpack(f">{n}H", d[ro:ro + n2])

    def gid(ch):
        c = ord(ch)
        for k in range(n):
            if starts[k] <= c <= ends[k]:
                if ranges[k] == 0:
                    return (c + deltas[k]) & 0xFFFF
                a = ro + 2 * k + ranges[k] + 2 * (c - starts[k]); g = struct.unpack(">H", d[a:a + 2])[0]
                return (g + deltas[k]) & 0xFFFF if g else 0
        return 0
    ho = T[b"hmtx"]
    return lambda ch: struct.unpack(">H", d[ho + 4 * gid(ch):ho + 4 * gid(ch) + 2])[0] / 1000 + TR / 1000


ADV = plek_advances()
CHUNKS = ["Setting up a server", "for an AI agent", "is where", "most people quit.", "Watch this.", "Hermes is",
          "an open -source agent", "that learns", "from every task", "and builds", "its own skills.", "It runs entirely",
          "within the Cloud plan,", "so you don't", "need to purchase", "any other subscription.", "A Bluehost VPS",
          "keeps it running", "24x7.", "Agent Hosting", "Hermes agent.", "Deploy.", "In a few clicks.", "No Docker,",
          "no SSL setup.", "Connect Telegram.", "Send it a message.", "It answers.", "It's live.", "Then it improves.",
          "It remembers", "what you ask", "and turns", "repeat tasks", "into skills.", "You stop", "re-prompting it.",
          "Comment deploy", "and I'll send it", "in your DM."]
FIX = [(" -source", "-source"), ("Cloud plan", "Claude plan"), ("24x7", "24/7")]
KEY = ["AI AGENT", "QUIT.", "HERMES", "OPEN-SOURCE", "LEARNS", "SKILLS.", "CLAUDE PLAN,", "SUBSCRIPTION.", "BLUEHOST VPS",
       "24/7.", "AGENT HOSTING", "DEPLOY.", "FEW CLICKS.", "TELEGRAM.", "LIVE.", "REMEMBERS", "REPEAT TASKS",
       "RE-PROMPTING", "DEPLOY", "DM."]

words = []
for a, b, tx in cues():
    ws = tx.split()
    for k, w_ in enumerate(ws):
        words.append((a + (b - a) * k / len(ws), a + (b - a) * (k + 1) / len(ws), w_))
chunks, wi_ = [], 0
for c in CHUNKS:
    n = len(c.split())
    assert " ".join(w_[2] for w_ in words[wi_:wi_ + n]) == c, (c, [w_[2] for w_ in words[wi_:wi_ + n]])
    chunks.append((words[wi_][0], words[wi_ + n - 1][1], c))
    wi_ += n
assert wi_ == len(words)
CS, CH = 50, 82
caps = []
for i, (a, b, tx) in enumerate(chunks):
    for f_, t_ in FIX:
        tx = tx.replace(f_, t_)
    tx = tx.upper()
    st, en0 = ms(a), ms(b)
    if any(f0 - 30 <= (st + en0) / 2 < f1 for f0, f1 in cap_off):
        continue
    for f0, f1 in cap_off:
        if f0 <= st < f1:
            st = f1
    nx = ms(chunks[i + 1][0]) if i + 1 < len(chunks) else SPEECH_MS
    en = min(max(nx if nx - en0 < 450 else en0 + 200, st + 250), SPEECH_MS + 600)
    for f0, f1 in cap_off:
        if st < f0 < en:
            en = f0
    # split at layout boundaries so the caption sits at the right height for each layout
    pieces = []
    for g0_, g1_, cy in cap_y_ranges:
        lo, hi = max(st, g0_), min(en, g1_)
        if hi - lo > 40:
            pieces.append((lo, hi, cy))
    marks = [False] * len(tx)
    for kw in sorted(KEY, key=len, reverse=True):
        for mt in re.finditer(re.escape(kw), tx):
            if not any(marks[mt.start():mt.end()]) and (mt.start() == 0 or tx[mt.start() - 1] == " "):
                marks[mt.start():mt.end()] = [True] * (mt.end() - mt.start())
    segs, cur = [], ""
    for k, ch in enumerate(tx):
        if k and marks[k] != marks[k - 1]:
            segs.append((cur, marks[k - 1])); cur = ""
        cur += ch
    segs.append((cur, marks[-1]))
    pad = 30
    bw = int(sum(ADV(ch) for ch in tx) * CS + 2 * pad)
    for p_, (lo, hi, cy) in enumerate(pieces):
        bx, by = (W - bw) / 2, cy - CH / 2
        x = bx + pad
        for sg, hot in segs:
            sw = sum(ADV(ch) for ch in sg) * CS
            if sg.strip():
                caps.append(text(f"Cap {i + 1}" + (" key" if hot else ""), sg, x, by + 3, sw + 24, CH, CS,
                                 CORAL_LT if hot else WHITE, lo, hi - lo, PLEK, just="left"))
            x += sw
        caps.append(rect(f"Cap {i + 1} box", bx, by, bw, CH, [0, 0, 0, 0.55], lo, hi - lo, r=12))
captions = group("Captions", 0, DUR_MS, caps)

# ------------------------------------------------------------------ audio
SFXD = {"soft-pop": 200, "soft-tap": 120, "dry-click": 110, "clear-ping": 450, "air-whoosh": 450, "short-riser": 900,
        "downlifter": 700, "soft-impact": 800}
SFX.append((0, "short-riser", 0.16))
audio = [{"type": "Audio", "id": nid(), "name": "Dialogue (edited, 10 ms fades at cuts, cleaned)", "activeRange": rng(0, DUR_MS),
          "sourceRange": rng(0, DUR_MS), "sourceIntrinsicDuration": DUR_MS, "source": {"assetId": "dialogue-edit"},
          "volume": 1.0, "captionsEnabled": False, "windowMs": 50}]
for st, p, v in sorted(SFX):
    st = max(0, int(st))
    dd = min(SFXD[p], DUR_MS - st)
    audio.append({"type": "Audio", "id": nid(), "name": f"SFX {p} @{st / 1000:.2f}", "activeRange": rng(st, dd),
                  "sourceRange": rng(0, dd), "sourceIntrinsicDuration": SFXD[p], "source": {"assetId": f"sfx-{p}"},
                  "volume": v, "captionsEnabled": False, "windowMs": 50})

doc = {"$schema": "https://jerboa.dev/schemas/fx-composition/editable/v1/document.schema.json", "formatVersion": 1,
       "dimensions": {"width": W, "height": H}, "duration": DUR,
       "composition": {"id": "main", "name": "Main", "layers": [captions] + list(reversed(beat_groups)) + audio}}
json.dump(doc, open(os.path.join(HERE, "editable.json"), "w"), indent=1, ensure_ascii=False)
_last = {}
for a_ in anims:                       # a later keyframe set on the same layer property replaces the earlier one
    _last[(a_["property"]["layerId"], a_["property"]["propertyType"])] = a_
anims = list(_last.values())
json.dump(anims, open(os.path.join(HERE, "anim.json"), "w"), indent=1)
print(f"{len(BEATS)} beats, {len(chunks)} captions, {len(SFX)} sfx, {DUR:.2f}s, {len(anims)} animated props")
