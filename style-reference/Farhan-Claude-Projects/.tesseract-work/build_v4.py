#!/usr/bin/env python3
"""Farhan - Claude Code Projects reel v4 (1080x1920): rotating layouts, real B-roll, fixed centre caption.
Writes editable_v3.json + anim_v3.json. Clip durations are read from clip_ms.json (written at import)."""
import json, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from timing import seg_edit, m, ms, DUR, SPEECH, SRC_DUR, cues  # noqa: E402
from beats_v4 import BEATS, clip_size, SPLIT_Y, WIN_W, FLOAT_TOP, CAPTION_OFF  # noqa: E402

W, H = 1080, 1920
DUR_MS, SPEECH_MS = int(round(DUR * 1000)), int(round(SPEECH * 1000))
CLIP_MS = json.load(open(os.path.join(HERE, "clip_ms_v4.json")))
WHITE, INK, CORAL, CORAL_LT = [1, 1, 1, 1], [0.106, 0.102, 0.094, 1], [0.816, 0.412, 0.31, 1], [0.98, 0.56, 0.42, 1]
PLEK = ("FoundryPlekW01-Regular", "Regular")
HB, BI = ("Helvetica", "Bold"), ("Baskerville", "Italic")
_id, _k, anims = [1], [0], []
LIN = {"type": "linear"}
OUT = {"type": "cubicBezier", "x1": 0.16, "y1": 1, "x2": 0.3, "y2": 1}
BACK = {"type": "cubicBezier", "x1": 0.34, "y1": 1.4, "x2": 0.64, "y2": 1}
GRADE = [{"type": "levels", "inputBlack": 4.0, "inputWhite": 242.0, "gamma": 1.05, "outputBlack": 6.0, "outputWhite": 255.0},
         {"type": "temperatureTint", "temperature": 12, "tint": 0},
         {"type": "vibrance", "vibrance": 8, "saturation": 0}]
COVER_COL = [0.106, 0.106, 0.098, 1]
SOFT_SH = {"color": [0.16, 0.10, 0.04, 0.35], "blurRadius": 44, "spreadRadius": 0, "blendMode": "normal", "offset": [0, 16]}
TXT_SH = {"color": [0, 0, 0, 0.8], "blurRadius": 30, "spreadRadius": 0, "blendMode": "normal", "offset": [0, 6]}


def nid():
    _id[0] += 1
    return _id[0]


def tf(x=0, y=0, s=100, ax=0, ay=0, op=100):
    return {"anchorPoint": [ax, ay], "position": [x, y], "scale": [s, s], "rotation": 0, "opacity": op}


def rng(s, d):
    return {"start": int(s), "duration": int(max(1, d))}


def kf(lid, prop, keys):
    out = []
    for t, v, e in keys:
        _k[0] += 1
        out.append({"id": f"k{_k[0]}", "layerTime": int(t), "value": {"type": "float", "value": v}, "easing": e})
    anims.append({"type": "setFxPropertyKeyframes", "compositionId": "main",
                  "property": {"layerId": lid, "propertyType": prop}, "keyframes": out})


def rect(name, x, y, w, h, fill, st, d, r=0, shadow=None, stroke=None, sw=0):
    R = {"size": [w, h], "fillColor": fill, "roundness": r}
    if stroke:
        R.update(strokeEnabled=True, strokeColor=stroke, strokeWidth=sw)
    L = {"type": "Rect", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d), "transform": tf(x, y),
         "rect": R}
    if shadow:
        L["dropShadow"] = shadow
    return L


def text(name, s, x, y, w, h, size, color, st, d, font, tr=0, shadow=None, just="center"):
    L = {"type": "Text", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d), "transform": tf(x, y),
         "sourceText": {"text": s, "fontFamily": font[0], "fontStyle": font[1], "fontSize": size, "fillColor": color,
                        "strokeWidth": 0, "justification": just, "boxText": True, "boxPosition": [0, 0],
                        "boxSize": [w, h], "verticalAlign": "center", "tracking": tr}}
    if shadow:
        L["dropShadow"] = shadow
    return L


def stroke_shape(name, pts, x, y, st, d, color=WHITE, sw=7):
    cmds = [{"type": "moveTo", "x": pts[0][0], "y": pts[0][1]}] + [{"type": "lineTo", "x": a, "y": b} for a, b in pts[1:]]
    return {"type": "Shape", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d), "transform": tf(x, y),
            "shape": {"path": {"commands": cmds}, "fills": [],
                      "strokes": [{"paint": {"type": "solid", "color": color}, "width": sw, "cap": "round", "join": "round",
                                   "miterLimit": 4, "blendMode": "normal", "opacity": 100}]}}


def image(name, asset, x, y, st, d):
    return {"type": "Image", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
            "transform": tf(x, y), "source": {"assetId": asset, "fit": "contain"}}


def group(name, st, d, layers):
    return {"type": "Group", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
            "transform": tf(), "layers": layers}


def rr_mask(x0, y0, x1, y1, r):
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    cmds = [{"type": "moveTo", "x": pts[0][0], "y": pts[0][1], "cornerRadius": r}] + \
           [{"type": "lineTo", "x": px, "y": py, "cornerRadius": r} for px, py in pts[1:]] + [{"type": "close"}]
    return [{"id": nid(), "mode": "add", "opacity": 100, "inverted": False, "path": {"commands": cmds}}]


def fvideo(name, st, d, src_ms, x, y, s, masks=None, ax=0, ay=0):
    L = {"type": "Video", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(st, d),
         "sourceRange": rng(src_ms, d), "sourceIntrinsicDuration": int(SRC_DUR * 1000), "volume": 0.0,
         "transform": tf(x, y, s, ax, ay), "source": {"assetId": "aroll", "fit": "contain"},
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
        L["cornerRadius"] = radius
    for p in ("scaleX", "scaleY"):
        kf(L["id"], p, [(0, 100, LIN), (d, 100 + push, LIN)])
    return L


EYE = (920, 440)
segi = {}
for j, (a, b, e) in enumerate(seg_edit):
    segi[(a, b)] = j


def farhan(fa, fb, g0, mode, **kw):
    """Farhan video layers for source window [fa,fb], times relative to the beat group start g0."""
    out = []
    for a, b, e in seg_edit:
        lo, hi = max(a, fa), min(b, fb)
        if hi - lo <= 0.01:
            continue
        j = segi[(a, b)]
        st, d, src = ms(lo) - g0, int(round((hi - lo) * 1000)), int(round(lo * 1000))
        if mode == "split":
            s = 1.00 if j % 2 == 0 else 1.08
            x, y = 540 - EYE[0] * s, 1280 - EYE[1] * s
            L = fvideo("Farhan (split)", st, d, src, x, y, s * 100,
                       rr_mask(-x / s, (SPLIT_Y - y) / s, (W - x) / s, (H - y) / s, 0))
        elif mode == "card":
            c = kw["card"]
            s = 1.00 if j % 2 == 0 else 1.08
            x, y = 540 - EYE[0] * s, kw["eye_y"] - EYE[1] * s
            L = fvideo("Farhan (card)", st, d, src, x, y, s * 100,
                       rr_mask((c[0] - x) / s, (c[1] - y) / s, (c[2] - x) / s, (c[3] - y) / s, 46 / s))
        elif mode == "circle":
            s, cx, r = 0.8, 890, 150
            cy = 232 if kw.get("top") else 1650
            fc = (920, 470)
            x, y = cx - fc[0] * s, cy - fc[1] * s
            L = fvideo("Farhan (circle)", st, d, src, x, y, s * 100,
                       rr_mask(fc[0] - r / s, fc[1] - r / s, fc[0] + r / s, fc[1] + r / s, r / s))
        else:  # full-screen, slow push-in over the beat (hook: fast zoom-out reveal first)
            FS = 185
            L = fvideo("Farhan (full)", st, d, src, 540, 774, FS, ax=EYE[0], ay=EYE[1])
            span = ms(fb) - g0
            if kw.get("hook") and st == 0:
                keys = [(0, 215, LIN), (520, FS, OUT), (d, FS + 4 * d / span, LIN)]
            else:
                keys = [(0, FS + 6 * st / span, LIN), (d, FS + 6 * (st + d) / span, LIN)]
            for p in ("scaleX", "scaleY"):
                kf(L["id"], p, keys)
        out.append(L)
    return out


def rise(L, d=260, dy=40):
    y0 = L["transform"]["position"][1]
    kf(L["id"], "opacity", [(0, 0, LIN), (int(d * 0.6), 100, LIN)])
    kf(L["id"], "positionY", [(0, y0 + dy, LIN), (d, y0, OUT)])


# ------------------------------------------------------------------ beats
SFX = []          # (edit ms, preset, volume)
beat_groups = []
for bi, (fa, fb, lay, clip, opt) in enumerate(BEATS):
    fb = min(fb, 68.62)
    g0 = ms(fa)
    g1 = DUR_MS if bi == len(BEATS) - 1 else ms(fb)
    d = g1 - g0
    L = []
    asset = f"v4b{bi:02d}" if clip else None
    if asset in CLIP_MS.get("_alias", {}):
        CLIP_MS[CLIP_MS["_alias"][asset]] = CLIP_MS[asset]
        asset = CLIP_MS["_alias"][asset]
    if bi:   # whoosh on every other layout change, a soft tap on the rest
        SFX.append((g0 - 180, "air-whoosh", 0.17) if bi % 2 else (g0, "soft-tap", 0.14))
    if lay == "SPLIT":
        # front -> back: seam, Farhan bottom (covers the B-roll push-in overflow), B-roll top, black base
        for (cx_, cy_, cw_, ch_) in opt.get("cover", []):     # hide a misleading UI label (bg-matched patch)
            L.append(rect("Cover", cx_, cy_, cw_, ch_, COVER_COL, 0, d))
        for (hx, hy, hw, hh), at in opt.get("shl", []):
            a_ = ms(at) - g0
            hl = rect("Highlight", hx, hy, hw, hh, [1, 1, 1, 0], a_, d - a_, r=12, stroke=CORAL, sw=5)
            kf(hl["id"], "opacity", [(0, 0, LIN), (150, 100, LIN)])
            L.insert(0, hl)
            SFX.append((ms(at), "dry-click", 0.2))
        L += ([rect("Seam", 0, SPLIT_Y - 2, W, 4, [0.95, 0.93, 0.89, 1], 0, d)] + farhan(fa, fb, g0, "split")
              + [bvideo("B-roll top", asset, 0, d, 0, 0, 1080, 960, push=2), rect("Black", 0, 0, W, H, [0, 0, 0, 1], 0, d)])
    elif lay == "BROLL":
        ccy = 232 if opt.get("circle_top") else 1650
        ring = rect("Circle ring", 890 - 156, ccy - 156, 312, 312, [1, 1, 1, 0], 0, d, r=156, stroke=WHITE, sw=6,
                    shadow=SOFT_SH)
        circ = farhan(fa, fb, g0, "circle", top=opt.get("circle_top", False))
        for c_ in circ[:1] + [ring]:
            kf(c_["id"], "opacity", [(0, 0, LIN), (180, 100, LIN)])
        L += [ring] + circ + [bvideo("B-roll full", asset, 0, d, 0, 0, 1080, 1920, push=2)]
        SFX.append((g0 + 60, "soft-pop", 0.16))
    elif lay in ("FLOAT", "DESK"):
        w, h = clip_size(lay, clip[2]) if clip else (WIN_W, 0)
        wx = (W - w) / 2
        wy = FLOAT_TOP if lay == "FLOAT" else 560 - h / 2
        if clip:
            win = bvideo("Window", asset, 0, d, wx, wy, w, h, push=1.5, radius=26)
            frame = rect("Window frame", wx - 3, wy - 3, w + 6, h + 6, [1, 1, 1, 1], 0, d, r=29, shadow=SOFT_SH)
            hls = []
            for k, ((hx, hy, hw, hh), at) in enumerate(opt.get("hl", [])):
                a_ = ms(at) - g0
                hl = rect("Highlight", wx + hx, wy + hy, hw, hh, [1, 1, 1, 0], a_, d - a_, r=12, stroke=CORAL, sw=5)
                kf(hl["id"], "opacity", [(0, 0, LIN), (150, 100, LIN)])
                hls.append(hl)
                SFX.append((ms(at), "dry-click", 0.2))
            for X in (win, frame):
                rise(X)
            L += hls + [win, frame]
            SFX.append((g0 + 40, "soft-pop", 0.18))
        if lay == "FLOAT":
            L += farhan(fa, fb, g0, "full")
        else:
            card = (90, 1090, 990, 1990)
            fl = farhan(fa, fb, g0, "card", card=card, eye_y=1330)
            sh = rect("Card shadow", card[0], card[1], card[2] - card[0], card[3] - card[1], [0.95, 0.93, 0.89, 1], 0,
                      min(d, SPEECH_MS - g0), r=46, shadow=SOFT_SH)
            if opt.get("cta"):   # hold Farhan (last frame) in the card through the tail instead of an empty desk
                tail = json.loads(json.dumps(fl[-1]))
                tail["id"] = nid(); tail["name"] = "Farhan (card, tail hold)"
                for e_ in tail["effects"]:
                    e_["id"] = nid()
                for m_ in tail["masks"]:
                    m_["id"] = nid()
                t0_ = fl[-1]["activeRange"]["start"] + fl[-1]["activeRange"]["duration"]
                tail["activeRange"] = rng(t0_, d - t0_)
                tail["sourceRange"] = rng(0, d - t0_)
                tail["sourceIntrinsicDuration"] = 1500
                tail["source"] = {"assetId": "aroll-tail2", "fit": "contain"}
                fl.append(tail)
                sh["activeRange"] = rng(0, d)
            L += fl + [sh, image("Desk", "desk", 0, 0, 0, d)]
    else:  # FULL / NUM
        L += farhan(fa, fb, g0, "full", hook=opt.get("hook", False))
    # ---------------- text overlays (above everything in the beat)
    top = []
    if opt.get("list"):
        items = [("01", "Coordinator + threads"), ("02", "Shared memory"), ("03", "Different brains")]
        card = rect("List card", 90, 300, 900, 520, WHITE, 0, d, r=34, shadow=SOFT_SH, stroke=[0.89, 0.86, 0.81, 1], sw=3)
        rise(card)
        rows = []
        for k, (n_, lab) in enumerate(items):
            a_ = max(0, ms(4.45) - g0 + k * 300)
            yy = 340 + k * 156
            num_t = text(f"List {n_}", n_, 140, yy, 140, 140, 64, CORAL, a_, d - a_, PLEK, 0, just="left")
            lab_t = text(f"List {n_} label", lab, 290, yy, 660, 140, 52, INK, a_, d - a_, HB, -10, just="left")
            for X in (num_t, lab_t):
                rise(X, 300, 24)
            if k < 2:
                rows.append(rect(f"List rule {k}", 140, yy + 148, 800, 2, [0.92, 0.89, 0.85, 1], a_, d - a_))
            rows += [num_t, lab_t]
            SFX.append((g0 + a_, "soft-tap", 0.2))
        top += rows + [card]
    if "title" in opt:
        l1, l2, t1, t2 = opt["title"]
        a1, a2 = ms(t1) - g0, ms(t2) - g0
        T2 = text("Title line 2", l2, 20, 480, 1040, 190, 150 if len(l2) <= 14 else 132, CORAL_LT, a2, d - a2, BI, -10, TXT_SH)
        T1 = text("Title line 1", l1, 40, 390, 1000, 100, 74, WHITE, a1, d - a1, HB, -10, TXT_SH)
        rise(T1); rise(T2)
        shade = rect("Top shade", 0, 0, W, 900, [0, 0, 0, 1], 0, d)
        shade["rect"]["fillPaint"] = {"type": "gradient", "gradientType": "linear", "start": [0, 0], "end": [0, 900],
                                      "stops": [{"offset": 0, "color": [0, 0, 0, 0.5]}, {"offset": 1, "color": [0, 0, 0, 0]}]}
        top += [T1, T2, shade]
        SFX.append((ms(t2), "soft-impact", 0.34))
    if "num" in opt:
        num, ttl, tt = opt["num"]
        a = ms(tt) - g0 if ms(tt) > g0 else 0
        N = text("Number", num, 0, 260, W, 300, 280, CORAL_LT, 0, d, PLEK, 0, TXT_SH)
        T = text("Section", ttl, 20, 560, 1040, 170, 128, WHITE, a, d - a, BI, -10, TXT_SH)
        for X in (N, T):
            kf(X["id"], "scaleX", [(0, 120, LIN), (260, 100, OUT)])
            kf(X["id"], "scaleY", [(0, 120, LIN), (260, 100, OUT)])
            X["transform"]["anchorPoint"] = [X["sourceText"]["boxSize"][0] / 2, X["sourceText"]["boxSize"][1] / 2]
            X["transform"]["position"] = [X["transform"]["position"][0] + X["sourceText"]["boxSize"][0] / 2,
                                          X["transform"]["position"][1] + X["sourceText"]["boxSize"][1] / 2]
            kf(X["id"], "opacity", [(0, 0, LIN), (120, 100, LIN)])
        dim = rect("Dim", 0, 0, W, H, [0.05, 0.03, 0.02, 0.62], 0, d)
        top += [N, T, dim]
        SFX.append((g0 + 20, "soft-impact", 0.30))
    if opt.get("cta"):
        t0 = ms(66.40) - g0
        click = ms(67.85) - g0
        top.append(text("CTA line 1", "Comment", 40, 230, 1000, 100, 72, INK, 0, d, HB, -10))
        top.append(text("CTA line 2", "“CLAUDE”", 20, 315, 1040, 180, 140, CORAL, 120, d - 120, BI, -10))
        rise(top[-2]); rise(top[-1])
        box = rect("Comment box", 110, 600, 860, 116, WHITE, 300, d - 300, r=58, shadow=SOFT_SH, stroke=[0.89, 0.86, 0.81, 1], sw=3)
        ph = text("Placeholder", "Add a comment...", 155, 600, 600, 116, 38, [0.64, 0.61, 0.56, 1], 300, t0 - 300,
                  ("Helvetica", "Regular"), 0, just="left")
        word = "CLAUDE"
        typed = [text(f"Typed {k}", word[:k], 155, 602, 600, 116, 50, INK, t0 + (k - 1) * 90,
                      (t0 + k * 90 if k < len(word) else d) - (t0 + (k - 1) * 90), PLEK, 0, just="left")
                 for k in range(1, len(word) + 1)]
        send = rect("Send", 870, 617, 82, 82, CORAL, 300, click + 160 - 300, r=41)
        arrow = stroke_shape("Send arrow", [(41, 60), (41, 22), (25, 38), (41, 22), (57, 38)], 870, 617, 300, click + 160 - 300)
        done = rect("Sent", 870, 617, 82, 82, [0.24, 0.75, 0.42, 1], click + 160, d - click - 160, r=41)
        tick = stroke_shape("Sent tick", [(24, 42), (36, 54), (58, 29)], 870, 617, click + 160, d - click - 160)
        for X in (box,):
            rise(X)
        for X in (done, tick):
            kf(X["id"], "opacity", [(0, 0, LIN), (120, 100, LIN)])
        cur = stroke_shape("Cursor", [(0, 0), (0, 44), (11, 34), (19, 52), (27, 48), (19, 31), (33, 31), (0, 0)], 0, 0,
                           click - 700, 900, color=INK, sw=4)
        curf = {"type": "Shape", "id": nid(), "name": "Cursor fill", "blendMode": "normal", "activeRange": rng(click - 700, 900),
                "transform": tf(0, 0), "shape": {"path": json.loads(json.dumps(cur["shape"]["path"])),
                "fills": [{"paint": {"type": "solid", "color": WHITE}, "fillRule": "nonZeroWinding", "blendMode": "normal",
                           "opacity": 100}], "strokes": []}}
        for X in (cur, curf):
            kf(X["id"], "positionX", [(0, 1010, LIN), (600, 918, OUT)])
            kf(X["id"], "positionY", [(0, 900, LIN), (600, 662, OUT)])
            kf(X["id"], "opacity", [(0, 0, LIN), (120, 100, LIN), (780, 100, LIN), (900, 0, LIN)])
            kf(X["id"], "scaleX", [(690, 100, LIN), (740, 82, LIN), (800, 100, LIN)])
            kf(X["id"], "scaleY", [(690, 100, LIN), (740, 82, LIN), (800, 100, LIN)])
        top = [cur, curf, tick, done, arrow, send] + typed + [ph, box] + top
        for k in range(len(word)):
            SFX.append((g0 + t0 + k * 90, "dry-click", 0.16))
        SFX += [(g0 + 300, "soft-pop", 0.22), (g0 + click, "dry-click", 0.3), (g0 + click + 150, "clear-ping", 0.26)]
    beat_groups.append(group(f"Beat {bi + 1:02d} {lay}", g0, d, top + L))


# ------------------------------------------------------------------ captions (centre, dot-matrix white on black 55 %, coral keys)
def plek_advances():
    d = open(os.path.join(HERE, "..", "Assets", "Foundry Plek W01 Regular.ttf"), "rb").read()
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
    return lambda ch: struct.unpack(">H", d[ho + 4 * gid(ch):ho + 4 * gid(ch) + 2])[0] / 1000


ADV = plek_advances()
from build_chunks import CHUNKS, KEY  # noqa: E402

words = []
for a, b, tx in cues():
    ws = tx.split()
    for k, w_ in enumerate(ws):
        words.append((a + (b - a) * k / len(ws), a + (b - a) * (k + 1) / len(ws), w_))
chunks, wi_ = [], 0
for c in CHUNKS:
    n = len(c.split())
    assert " ".join(w_[2] for w_ in words[wi_:wi_ + n]) == c, c
    chunks.append((words[wi_][0], words[wi_ + n - 1][1], c))
    wi_ += n
CS, CH = 50, 82
caps = []
OFF = [(ms(fa), ms(fb)) for fa, fb, lay, c_, o_ in BEATS if lay in CAPTION_OFF]
for i, (a, b, tx) in enumerate(chunks):
    st, en0 = ms(a), ms(b)
    if any(f0 - 30 <= (st + en0) / 2 < f1 for f0, f1 in OFF):
        continue
    for f0, f1 in OFF:
        if f0 <= st < f1:
            st = f1
    nx = ms(chunks[i + 1][0]) if i + 1 < len(chunks) else SPEECH_MS
    en = min(max(nx if nx - en0 < 450 else en0 + 200, st + 250), SPEECH_MS)
    for f0, f1 in OFF:
        if st < f0 < en:
            en = f0
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
    bx, by = (W - bw) / 2, SPLIT_Y - CH / 2
    x = bx + pad
    for sg, hot in segs:
        sw = sum(ADV(ch) for ch in sg) * CS
        if sg.strip():
            caps.append(text(f"Cap {i + 1}" + (" key" if hot else ""), sg, x, by + 3, sw + 24, CH, CS,
                             CORAL_LT if hot else WHITE, st, en - st, PLEK, just="left"))
        x += sw
    caps.append(rect(f"Cap {i + 1} box", bx, by, bw, CH, [0, 0, 0, 0.55], st, en - st, r=12))
captions = group("Captions (centre)", 0, DUR_MS, caps)

# ------------------------------------------------------------------ audio
SFXD = {"soft-pop": 200, "soft-tap": 120, "dry-click": 110, "clear-ping": 450, "air-whoosh": 450, "short-riser": 900,
        "downlifter": 700, "soft-impact": 800}
SFX.append((0, "short-riser", 0.16))
audio = [{"type": "Audio", "id": nid(), "name": "Dialogue (edited, 10 ms fades at cuts)", "activeRange": rng(0, DUR_MS),
          "sourceRange": rng(0, DUR_MS), "sourceIntrinsicDuration": DUR_MS, "source": {"assetId": "dialogue-edit-v4"},
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
json.dump(doc, open(os.path.join(HERE, "editable_v4.json"), "w"), indent=1, ensure_ascii=False)
json.dump(anims, open(os.path.join(HERE, "anim_v4.json"), "w"), indent=1)
print(f"v4: {len(BEATS)} beats, {len(chunks)} captions, {len(SFX)} sfx, {DUR:.2f}s")
