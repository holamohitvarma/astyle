#!/usr/bin/env python3
"""HyperFrames graphics layer for the Farhan 'Claude Code Projects' reel (1080x1920, edit time).
Cream grid page + section headers + animated diagrams. Farhan's card, captions and audio are added in Tesseract.
All cue times below are SOURCE seconds (from the SRT) and are mapped to edit time with m()."""
import math, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".tesseract-work"))
from timing import m, DUR, SPEECH, BROLL, BOX_CY, broll_geom  # noqa: E402

W, H = 1080, 1920
INK, CORAL, CREAM = "#1B1A18", "#D0694F", "#F2EDE4"
js, html = [], []


def t(src):
    return f"{m(src):.3f}"


def J(s):
    js.append(s)


def spark(size, color=CORAL, rays=12):
    """Claude-style radial spark (tapered rays of alternating length)."""
    c = size / 2
    parts = []
    for i in range(rays):
        a = i * 360 / rays + (7 if i % 2 else 0)
        L = c * (0.96 if i % 3 == 0 else 0.80 if i % 3 == 1 else 0.70)
        w = size * 0.085
        parts.append(f'<rect x="{c - w/2:.1f}" y="{c - L:.1f}" width="{w:.1f}" height="{L:.1f}" rx="{w/2:.1f}" '
                     f'transform="rotate({a:.1f} {c} {c})"/>')
    return f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" fill="{color}">{"".join(parts)}</svg>'


CURSOR = ('<svg width="54" height="64" viewBox="0 0 27 32"><path d="M2 2 L2 26 L8.5 20 L13 30 L17 28 L12.6 18.5 L21 18.5 Z" '
          'fill="#111" stroke="#fff" stroke-width="2" stroke-linejoin="round"/></svg>')


def el(id_, style, inner="", cls=""):
    html.append(f'<div id="{id_}" class="clip {cls}" data-start="0" data-duration="{DUR}" style="{style}">{inner}</div>')


def pop_in(sel, at, dur=0.45, frm=0.6, y=0, ease="back.out(1.8)"):
    J(f'tl.set("{sel}", {{opacity:0, scale:{frm}, y:{y}}}, 0);')
    J(f'tl.to("{sel}", {{opacity:1, scale:1, y:0, duration:{dur}, ease:"{ease}"}}, {at});')


def fade_out(sel, at, dur=0.25, y=0, scale=1):
    J(f'tl.to("{sel}", {{opacity:0, y:{y}, scale:{scale}, duration:{dur}, ease:"power2.in"}}, {at});')


# ------------------------------------------------------------------ page + headers
HEADERS = [  # (start, end, line1, line2)
    (2.10, 6.62, "Claude Code", "Projects"),
    (7.55, 21.78, "Number one", "the coordinator"),
    (22.86, 28.88, "Every thread's", "stage, live"),
    (29.95, 38.50, "Number two", "shared memory"),
    (39.55, 55.40, "Number three", "different brains"),
    (57.62, 64.20, "Watch your", "usage"),
    (64.25, 99.0, "Comment", "“CLAUDE”"),
]
for i, (a, b, l1, l2) in enumerate(HEADERS):
    el(f"h{i}", "position:absolute; left:0; right:0; top:205px; text-align:center;",
       f'<div class="h1" id="h{i}a">{l1}</div><div class="h2wrap"><span class="h2" id="h{i}b">{l2}</span>'
       f'<div class="ul" id="h{i}u"></div></div>')
    J(f'tl.set("#h{i}", {{opacity:1}}, 0); tl.set(["#h{i}a","#h{i}b"], {{opacity:0, y:34}}, 0); '
      f'tl.set("#h{i}u", {{scaleX:0}}, 0);')
    J(f'tl.to("#h{i}a", {{opacity:1, y:0, duration:0.42, ease:"power3.out"}}, {t(a)});')
    J(f'tl.to("#h{i}b", {{opacity:1, y:0, duration:0.5, ease:"power3.out"}}, {m(a) + 0.12:.3f});')
    J(f'tl.to("#h{i}u", {{scaleX:1, duration:0.55, ease:"power2.inOut"}}, {m(a) + 0.32:.3f});')
    if b < 90:
        J(f'tl.to("#h{i}", {{opacity:0, y:-24, duration:0.22, ease:"power2.in"}}, {m(b) - 0.22:.3f});')
        J(f'tl.set("#h{i}", {{y:0}}, {m(b) + 0.01:.3f});')

# ------------------------------------------------------------------ V0  three things
el("v0logo", "position:absolute; left:420px; top:690px; width:240px; height:240px; border-radius:56px; background:#fff;"
   "box-shadow:0 18px 50px rgba(60,40,20,.16); display:flex; align-items:center; justify-content:center;", spark(150))
J(f'tl.set("#v0logo", {{opacity:0, scale:0.2, y:-150}}, 0); tl.to("#v0logo", {{opacity:1, scale:0.5, duration:0.45, '
  f'ease:"back.out(1.8)"}}, {m(3.62):.3f});')
TILES = [("01", "Coordinator + threads"), ("02", "Shared memory"), ("03", "Different brains")]
for k, (n, lab) in enumerate(TILES):
    el(f"v0t{k}", f"position:absolute; left:150px; width:780px; top:{770 + k * 132}px; height:108px; background:#fff;"
       "border:2px solid #E4DCCF; border-radius:22px; display:flex; align-items:center; gap:30px; padding:0 34px;"
       "box-shadow:0 10px 30px rgba(60,40,20,.08);",
       f'<span style="font-family:Plek; font-size:46px; color:{CORAL}">{n}</span>'
       f'<span style="font-size:44px; font-weight:600; color:{INK}; letter-spacing:-0.5px">{lab}</span>')
    J(f'tl.set("#v0t{k}", {{opacity:0, x:-80}}, 0); tl.to("#v0t{k}", {{opacity:1, x:0, duration:0.45, '
      f'ease:"power3.out"}}, {m(4.45) + k * 0.30:.3f});')
    J(f'tl.to("#v0t{k}", {{scale:1.04, duration:0.14, yoyo:true, repeat:1}}, {m(5.35) + k * 0.12:.3f});')
fade_out("#v0logo", m(6.62) - 0.25)
for k in range(3):
    fade_out(f"#v0t{k}", m(6.62) - 0.25 + k * 0.03, y=-20)

# ------------------------------------------------------------------ V1  separate chats (then real UI B-roll)
CHATS = [(130, 560, -6), (600, 520, 5), (360, 720, -2), (120, 900, 4), (640, 880, -5)]
for k, (x, y, r) in enumerate(CHATS):
    lines = "".join(f'<div style="height:14px; border-radius:7px; background:#E8E1D6; width:{w}%; margin-top:14px"></div>'
                    for w in (88, 64, 76))
    el(f"c{k}", f"position:absolute; left:{x}px; top:{y}px; width:320px; height:200px; background:#fff; border-radius:24px;"
       f"border:2px solid #E4DCCF; padding:22px 26px; transform:rotate({r}deg); box-shadow:0 12px 30px rgba(60,40,20,.10);",
       f'<div style="display:flex; align-items:center; gap:12px"><div style="width:22px;height:22px;border-radius:11px;'
       f'background:{CORAL}"></div><span style="font-family:Plek; font-size:26px; color:#8A8378">chat {k + 1}</span></div>'
       + lines)
    J(f'tl.set("#c{k}", {{opacity:0, scale:0.7}}, 0); tl.to("#c{k}", {{opacity:1, scale:1, duration:0.35, '
      f'ease:"back.out(1.7)"}}, {m(7.70) + k * 0.09:.3f});')
el("cur1", "position:absolute; left:0; top:0;", CURSOR)
hops = [(m(8.30), 300, 640), (m(8.75), 760, 600), (m(9.15), 520, 800), (m(9.50), 280, 980), (m(9.85), 800, 960)]
J(f'tl.set("#cur1", {{opacity:0, x:540, y:1180}}, 0); tl.to("#cur1", {{opacity:1, duration:0.2}}, {m(8.0):.3f});')
for tt, x, y in hops:
    J(f'tl.to("#cur1", {{x:{x}, y:{y}, duration:0.3, ease:"power2.inOut"}}, {tt - 0.3:.3f});')
    J(f'tl.to("#cur1", {{scale:0.85, duration:0.06, yoyo:true, repeat:1}}, {tt:.3f});')
J(f'tl.to("#cur1", {{opacity:0, duration:0.15}}, {m(10.1):.3f});')
for k, (x, y, r) in enumerate(CHATS):  # "anymore" -> chats collapse to centre, real coordinator UI takes over
    J(f'tl.to("#c{k}", {{x:{540 - (x + 160)}, y:{850 - (y + 100)}, scale:0.1, opacity:0, rotation:0, duration:0.4, '
      f'ease:"power3.in"}}, {m(10.05) + k * 0.025:.3f});')

# ------------------------------------------------------------------ V1b project panel with live stage pills
STAGES = {"PLAN": "#6B665E", "BUILD": "#E0A23A", "TEST": "#4C8DF6", "DONE": "#3DBE6A"}
ROWS = [("Optimize images", ["BUILD", "TEST", "DONE"], [26.30, 28.05]),
        ("Cache page content", ["PLAN", "BUILD"], [26.95]),
        ("Lazy-load scripts", ["BUILD", "TEST"], [27.55]),
        ("Split the JS bundle", ["TEST", "DONE"], [25.95])]
rows_html = ""
for r, (name, sts, _) in enumerate(ROWS):
    pills = "".join(f'<span id="p{r}{j}" style="position:absolute; right:0; top:0; padding:10px 18px 6px; border-radius:14px;'
                    f'font-family:Plek; font-size:28px; color:#fff; background:{STAGES[s]}">{s.lower()}</span>'
                    for j, s in enumerate(sts))
    rows_html += (f'<div style="position:relative; height:112px; border-top:1px solid #2C2B29; display:flex; align-items:center;'
                  f'padding:0 34px; gap:20px"><div style="width:14px;height:14px;border-radius:7px;background:{CORAL}"></div>'
                  f'<div style="flex:1"><div style="font-size:36px; font-weight:600; color:#F4F1EA">{name}</div>'
                  f'<div style="margin-top:10px; height:8px; width:300px; border-radius:4px; background:#2E2D2A; overflow:hidden">'
                  f'<div id="pb{r}" style="height:100%; width:100%; background:#BDB5A8; transform-origin:left"></div></div></div>'
                  f'<div style="position:relative; width:170px; height:44px">{pills}</div></div>')
el("panel", "position:absolute; left:100px; top:530px; width:880px; background:#151413; border-radius:30px; overflow:hidden;"
   "box-shadow:0 26px 60px rgba(30,20,10,.28); border:3px solid #151413;",
   f'<div style="display:flex; align-items:center; gap:12px; padding:26px 34px">'
   f'<div style="width:16px;height:16px;border-radius:8px;background:#FF5F57"></div>'
   f'<div style="width:16px;height:16px;border-radius:8px;background:#FEBC2E"></div>'
   f'<div style="width:16px;height:16px;border-radius:8px;background:#28C840"></div>'
   f'<span style="margin-left:18px; font-family:Plek; font-size:30px; color:#B9B2A6">project / site-performance</span>'
   f'<span style="margin-left:auto; font-family:Plek; font-size:26px; color:{CORAL}">4 threads</span></div>{rows_html}')
J(f'tl.set("#panel", {{opacity:0, y:80}}, 0); tl.to("#panel", {{opacity:1, y:0, duration:0.45, ease:"power3.out"}}, {m(25.62):.3f});')
for r, (name, sts, times) in enumerate(ROWS):
    for j in range(1, len(sts)):
        J(f'tl.set("#p{r}{j}", {{opacity:0}}, 0);')
    for j, tt in enumerate(times):
        J(f'tl.set("#p{r}{j}", {{opacity:0}}, {t(tt)}); tl.set("#p{r}{j + 1}", {{opacity:1, scale:1.25}}, {t(tt)});'
          f'tl.to("#p{r}{j + 1}", {{scale:1, duration:0.3, ease:"back.out(2)"}}, {m(tt) + 0.01:.3f});')
    J(f'tl.set("#pb{r}", {{scaleX:{[0.35, 0.1, 0.4, 0.75][r]}}}, 0); tl.to("#pb{r}", {{scaleX:1, duration:{2.8 - r * 0.3:.2f}, '
      f'ease:"none"}}, {m(25.80):.3f});')
J(f'tl.to("#panel", {{borderColor:"{CORAL}", duration:0.3}}, {t(27.10)});')
fade_out("#panel", m(28.88) - 0.22, y=-30)

# ------------------------------------------------------------------ V2 shared memory hub
HUB = (540, 840)
TPOS = [(250, 600), (830, 600), (250, 1080), (830, 1080)]
paths = "".join(f'<line id="ml{k}" x1="{x}" y1="{y}" x2="{HUB[0]}" y2="{HUB[1]}" stroke="#CDBFAE" stroke-width="4" '
                f'stroke-dasharray="10 10"/>' for k, (x, y) in enumerate(TPOS))
el("mlines", "position:absolute; left:0; top:0;", f'<svg width="1080" height="1920">{paths}</svg>')
el("hub", f"position:absolute; left:{HUB[0] - 125}px; top:{HUB[1] - 125}px; width:250px; height:250px; border-radius:60px;"
   f"background:{INK}; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:14px;"
   "box-shadow:0 22px 50px rgba(0,0,0,.25);",
   f'<svg width="110" height="110" viewBox="0 0 110 110" fill="none" stroke="{CORAL}" stroke-width="7">'
   '<ellipse cx="55" cy="22" rx="40" ry="13"/><path d="M15 22 V88 C15 96 33 101 55 101 C77 101 95 96 95 88 V22"/>'
   '<path d="M15 55 C15 63 33 68 55 68 C77 68 95 63 95 55"/></svg>'
   '<span style="font-family:Plek; font-size:26px; color:#EDE7DC">memory</span>')
el("hring", f"position:absolute; left:{HUB[0] - 125}px; top:{HUB[1] - 125}px; width:250px; height:250px; border-radius:60px;"
   f"border:4px solid {CORAL};")
for k, (x, y) in enumerate(TPOS):
    el(f"mt{k}", f"position:absolute; left:{x - 120}px; top:{y - 46}px; width:240px; height:92px; background:#fff;"
       "border:2px solid #E4DCCF; border-radius:46px; display:flex; align-items:center; justify-content:center; gap:12px;"
       "box-shadow:0 10px 26px rgba(60,40,20,.10);",
       f'<div style="width:16px;height:16px;border-radius:8px;background:{CORAL}"></div>'
       f'<span style="font-family:Plek; font-size:28px; color:{INK}">thread {k + 1}</span>')
    for wv in range(2):
        el(f"di{k}{wv}", f"position:absolute; left:-11px; top:-11px; width:22px; height:22px; border-radius:11px; background:{INK};")
        el(f"do{k}{wv}", f"position:absolute; left:-11px; top:-11px; width:22px; height:22px; border-radius:11px; background:{CORAL};")
pop_in("#hub", t(29.98), 0.45, 0.3)
J(f'tl.set("#mlines", {{opacity:0}}, 0); tl.to("#mlines", {{opacity:1, duration:0.4}}, {t(30.35)});')
for k, (x, y) in enumerate(TPOS):
    pop_in(f"#mt{k}", f"{m(30.41) + k * 0.1:.3f}", 0.4, 0.5)
    for wv in range(2):
        ti = m(31.07) + wv * 0.45 + k * 0.06
        to = m(32.25) + wv * 0.45 + k * 0.06
        J(f'tl.set("#di{k}{wv}", {{opacity:0, x:{x}, y:{y}}}, 0); tl.set("#di{k}{wv}", {{opacity:1}}, {ti:.3f});'
          f'tl.to("#di{k}{wv}", {{x:{HUB[0]}, y:{HUB[1]}, duration:0.55, ease:"power1.in"}}, {ti:.3f});'
          f'tl.set("#di{k}{wv}", {{opacity:0}}, {ti + 0.55:.3f});')
        J(f'tl.set("#do{k}{wv}", {{opacity:0, x:{HUB[0]}, y:{HUB[1]}}}, 0); tl.set("#do{k}{wv}", {{opacity:1}}, {to:.3f});'
          f'tl.to("#do{k}{wv}", {{x:{x}, y:{y}, duration:0.55, ease:"power1.out"}}, {to:.3f});'
          f'tl.set("#do{k}{wv}", {{opacity:0}}, {to + 0.55:.3f});')
J(f'tl.to("#hub", {{scale:1.07, duration:0.12, yoyo:true, repeat:3}}, {m(31.6):.3f});')
J(f'tl.set("#hring", {{opacity:0}}, 0); tl.set("#hring", {{opacity:0.9, scale:1}}, {t(33.57)});'
  f'tl.to("#hring", {{scale:1.5, opacity:0, duration:0.9, ease:"power2.out"}}, {m(33.57) + 0.01:.3f});')
for s in ["#hub", "#mlines"] + [f"#mt{k}" for k in range(4)]:
    fade_out(s, m(32.90) - 0.15, scale=0.9)
# prompt-engineering card
plines = ["You are a senior full-stack engineer.", "Always remember the brand rules.", "Context: launch site, auth, DB...",
          "Step 1: re-read the last 3 chats.", "Don't forget what we decided.", "Repeat the style guide again..."]
pl = "".join(f'<div class="pl" id="pl{k}" style="font-family:Plek; font-size:27px; color:#CFC8BC; margin-top:16px; white-space:nowrap">'
             f'<span style="color:{CORAL}">&gt;</span> {s}</div>' for k, s in enumerate(plines))
el("pcard", "position:absolute; left:110px; top:640px; width:860px; height:470px; background:#151413; border-radius:28px;"
   "padding:30px 36px; box-shadow:0 26px 60px rgba(30,20,10,.28); overflow:hidden",
   f'<div style="font-family:Plek; font-size:28px; color:#8A8378">prompt.txt</div>{pl}')
el("ptitle", "position:absolute; left:0; right:0; top:520px; text-align:center;",
   f'<span style="position:relative; display:inline-block; font-size:62px; font-weight:700; color:{INK}; letter-spacing:-1px">'
   f'Prompt engineering<span id="pstrike" style="position:absolute; left:-12px; right:-12px; top:52%; height:9px; '
   f'background:{CORAL}; border-radius:5px; transform-origin:left"></span></span>')
el("pless", f"position:absolute; left:720px; top:1060px; padding:14px 28px 10px; background:{CORAL}; color:#fff; border-radius:18px;"
   "font-family:Plek; font-size:44px; transform:rotate(-6deg)", "way less")
J(f'tl.set("#pcard", {{opacity:0, y:60}}, 0); tl.to("#pcard", {{opacity:1, y:0, duration:0.45, ease:"power3.out"}}, {m(34.55):.3f});')
for k in range(len(plines)):
    J(f'tl.set("#pl{k}", {{opacity:0, x:-16}}, 0); tl.to("#pl{k}", {{opacity:1, x:0, duration:0.2}}, {m(34.75) + k * 0.16:.3f});')
J(f'tl.set("#ptitle", {{opacity:0, y:20}}, 0); tl.to("#ptitle", {{opacity:1, y:0, duration:0.35}}, {t(35.50)});')
J(f'tl.set("#pstrike", {{scaleX:0}}, 0); tl.to("#pstrike", {{scaleX:1, duration:0.35, ease:"power2.out"}}, {t(36.55)});')
for k in (1, 3, 4, 5):
    J(f'tl.to("#pl{k}", {{opacity:0.15, duration:0.3}}, {m(37.0) + k * 0.05:.3f});')
J(f'tl.set("#pless", {{opacity:0, scale:2, rotation:-6}}, 0); tl.to("#pless", {{opacity:1, scale:1, rotation:-6, duration:0.28, '
  f'ease:"power4.in"}}, {m(37.60):.3f});')
for s in ["#pcard", "#ptitle", "#pless"]:
    fade_out(s, m(38.50) - 0.22, y=-20)


# ------------------------------------------------------------------ V3 different brains: model + effort per role
def brain_card(id_, x, title, icon, models, final_model, effort_lab):
    chips = "".join(f'<div id="{id_}m{j}" style="position:absolute; left:0; right:0; top:0; text-align:center; line-height:74px">'
                    f'{mm}</div>' for j, mm in enumerate(models))
    el(id_, f"position:absolute; left:{x}px; top:540px; width:440px; height:660px; background:#fff; border-radius:34px;"
       "border:3px solid #E4DCCF; padding:34px 34px; box-shadow:0 16px 40px rgba(60,40,20,.12);",
       f'<div style="display:flex; align-items:center; gap:16px">{icon}<span style="font-family:Plek; font-size:34px; color:{INK}">'
       f'{title}</span></div>'
       f'<div style="margin-top:44px; font-family:Plek; font-size:26px; color:#8A8378">model</div>'
       f'<div style="position:relative; margin-top:12px; height:74px; border-radius:20px; background:{INK}; color:#fff;'
       f'font-size:38px; font-weight:600; overflow:hidden">{chips}</div>'
       f'<div id="{id_}e" style="margin-top:46px"><div style="font-family:Plek; font-size:26px; color:#8A8378">effort</div>'
       f'<div style="position:relative; margin-top:22px; height:18px; border-radius:9px; background:#EEE7DC">'
       f'<div id="{id_}f" style="position:absolute; left:0; top:0; bottom:0; width:100%; border-radius:9px; background:{CORAL};'
       f'transform-origin:left"></div><div id="{id_}k" style="position:absolute; top:-13px; left:-22px; width:44px; height:44px;'
       f'border-radius:22px; background:#fff; border:4px solid {INK}"></div></div>'
       f'<div id="{id_}v" style="margin-top:30px; font-family:Plek; font-size:34px; color:{CORAL}">{effort_lab}</div></div>'
       f'<div id="{id_}x" style="position:absolute; left:34px; right:34px; bottom:34px"></div>')


ico_c = (f'<div style="width:58px;height:58px;border-radius:29px;background:{INK};display:flex;align-items:center;'
         f'justify-content:center">{spark(36)}</div>')
ico_t = ''.join(f'<div style="width:16px;height:46px;border-radius:5px;background:{CORAL};margin-right:6px;opacity:{o}"></div>'
                for o in (1, .7, .45))
brain_card("bc", 70, "coordinator", ico_c, ["Opus 5.5"], "Opus 5.5", "low \u00b7 light")
brain_card("bt", 570, "threads", f'<div style="display:flex">{ico_t}</div>', ["Opus 5.5"], "Opus 5.5", "max \u00b7 full power")
bars = "".join(f'<div style="margin-top:12px; height:12px; border-radius:6px; background:#EEE7DC; overflow:hidden">'
               f'<div id="bb{k}" style="height:100%; width:100%; background:{INK}; transform-origin:left"></div></div>' for k in range(3))
el("bbuild", "position:absolute; left:604px; top:1048px; width:372px;",
   f'<div style="font-family:Plek; font-size:24px; color:#8A8378">building...</div>{bars}')
for cid, at in (("bc", 40.27), ("bt", 41.71)):
    J(f'tl.set("#{cid}", {{opacity:0, y:70}}, 0); tl.to("#{cid}", {{opacity:1, y:0, duration:0.45, ease:"power3.out"}}, {t(at)});')
    J(f'tl.set("#{cid}e", {{opacity:0}}, 0); tl.set("#{cid}f", {{scaleX:0.5}}, 0); tl.set("#{cid}k", {{x:186}}, 0);'
      f'tl.set("#{cid}v", {{opacity:0}}, 0);')
J(f'tl.to(["#bc","#bt"], {{y:-14, duration:0.18, yoyo:true, repeat:1, ease:"power1.out"}}, {t(42.40)});')
J(f'tl.to(["#bc","#bt"], {{opacity:0, y:-20, duration:0.18, ease:"power2.in"}}, {m(44.0) - 0.18:.3f});'
  f'tl.to(["#bc","#bt"], {{opacity:1, y:0, duration:0.35, ease:"power3.out"}}, {m(48.25):.3f});')
for cid in ("bc", "bt"):
    J(f'tl.to("#{cid}e", {{opacity:1, duration:0.35}}, {m(48.30):.3f});')
J(f'tl.to("#bc", {{borderColor:"{CORAL}", scale:1.03, duration:0.3}}, {t(48.62)}); tl.to("#bt", {{opacity:0.45, duration:0.3}}, {t(48.62)});')
J(f'tl.to("#bcf", {{scaleX:0.22, duration:0.7, ease:"power2.inOut"}}, {t(49.10)}); tl.to("#bck", {{x:60, duration:0.7, '
  f'ease:"power2.inOut"}}, {t(49.10)}); tl.to("#bcv", {{opacity:1, duration:0.3}}, {t(50.10)});')
J(f'tl.to("#bc", {{borderColor:"#E4DCCF", scale:1, opacity:0.55, duration:0.3}}, {t(52.10)});'
  f'tl.to("#bt", {{opacity:1, borderColor:"{CORAL}", scale:1.03, duration:0.3}}, {t(52.10)});')
J(f'tl.to("#btf", {{scaleX:1, duration:0.8, ease:"power2.inOut"}}, {t(52.70)}); tl.to("#btk", {{x:350, duration:0.8, '
  f'ease:"power2.inOut"}}, {t(52.70)}); tl.to("#btv", {{opacity:1, duration:0.3}}, {t(53.35)});')
J(f'tl.to("#bt", {{boxShadow:"0 0 0 10px rgba(208,105,79,.18), 0 16px 40px rgba(60,40,20,.12)", duration:0.4}}, {t(53.0)});')
J(f'tl.set("#bbuild", {{opacity:0}}, 0); tl.to("#bbuild", {{opacity:1, duration:0.3}}, {t(53.97)});')
for k in range(3):
    J(f'tl.set("#bb{k}", {{scaleX:0}}, 0); tl.to("#bb{k}", {{scaleX:{[1, 0.8, 0.9][k]}, duration:{[0.9, 1.2, 1.0][k]}, '
      f'ease:"power1.out"}}, {m(54.05) + k * 0.1:.3f});')
for s in ["#bc", "#bt", "#bbuild"]:
    fade_out(s, m(55.40) - 0.2)

# ------------------------------------------------------------------ V4 usage burn (after real usage + thread clips)
el("usage", "position:absolute; left:100px; top:640px; width:880px; background:#fff; border-radius:30px; border:3px solid #E4DCCF;"
   "padding:34px 40px 40px; box-shadow:0 16px 40px rgba(60,40,20,.12)",
   f'<div style="display:flex; align-items:baseline; justify-content:space-between"><span style="font-family:Plek; font-size:34px;'
   f'color:{INK}">usage \u00b7 4 threads in parallel</span><span id="upct" style="font-family:Plek; font-size:70px; color:{INK}">'
   f'58%</span></div><div style="margin-top:22px; height:38px; border-radius:19px; background:#EEE7DC; overflow:hidden">'
   f'<div id="ufill" style="height:100%; width:100%; background:linear-gradient(90deg,#E9A23B,{CORAL},#C2342B);'
   f'transform-origin:left"></div></div>')
J(f'tl.set("#usage", {{opacity:0, y:60}}, 0); tl.to("#usage", {{opacity:1, y:0, duration:0.35, ease:"power3.out"}}, {m(62.85):.3f});')
J(f'tl.set("#ufill", {{scaleX:0.58}}, 0); var U={{v:58}}; tl.set(U, {{v:58}}, 0);'
  f'tl.to("#ufill", {{scaleX:0.94, duration:0.9, ease:"power1.in"}}, {m(62.95):.3f});'
  f'tl.to(U, {{v:94, duration:0.9, ease:"power1.in", onUpdate:function(){{document.getElementById("upct").textContent='
  f'Math.round(U.v)+"%";}}}}, {m(62.95):.3f});')
J(f'tl.to("#upct", {{color:"#C2342B", duration:0.3}}, {t(63.30)});')
J(f'tl.to("#usage", {{x:-8, duration:0.05, yoyo:true, repeat:5}}, {t(63.70)});')
fade_out("#usage", m(64.20) - 0.2, y=-20)

# ------------------------------------------------------------------ V5 CTA: setup guide + comment box typing CLAUDE
el("guide", "position:absolute; left:290px; top:560px; width:500px; height:380px; background:#fff; border-radius:28px;"
   "border:3px solid #E4DCCF; padding:34px 40px; box-shadow:0 22px 50px rgba(60,40,20,.14); transform:rotate(-4deg)",
   f'<div style="display:flex; align-items:center; gap:16px">{spark(56)}<span style="font-size:36px; font-weight:700; color:{INK}">'
   f'Projects</span></div><div style="margin-top:14px; font-family:Plek; font-size:30px; color:{CORAL}">full setup guide</div>'
   + "".join(f'<div style="margin-top:20px; height:14px; border-radius:7px; background:#EEE7DC; width:{w}%"></div>'
             for w in (92, 80, 86, 60)))
el("cbox", "position:absolute; left:110px; top:1040px; width:860px; height:116px; background:#fff; border-radius:58px;"
   "border:3px solid #E4DCCF; box-shadow:0 14px 34px rgba(60,40,20,.12); display:flex; align-items:center; padding:0 18px 0 44px",
   '<span id="cph" style="position:absolute; left:47px; font-size:38px; color:#A39B8F">Add a comment...</span>'
   f'<span id="ctxt" style="font-family:Plek; font-size:48px; color:{INK}"></span>'
   f'<span id="ccar" style="display:inline-block; width:4px; height:52px; background:{CORAL}; margin-left:6px"></span>'
   f'<div id="csend" style="margin-left:auto; width:82px; height:82px; border-radius:41px; background:{CORAL}; display:flex;'
   'align-items:center; justify-content:center"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#fff" '
   'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg></div>')
el("cdone", "position:absolute; left:870px; top:1057px; width:82px; height:82px; border-radius:41px; background:#3DBE6A; display:flex;"
   "align-items:center; justify-content:center",
   '<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" '
   'stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>')
el("cur2", "position:absolute; left:0; top:0;", CURSOR)
J(f'tl.set("#guide", {{opacity:0, y:60, rotation:-4}}, 0); tl.to("#guide", {{opacity:1, y:0, rotation:-4, duration:0.5, '
  f'ease:"back.out(1.5)"}}, {m(64.55):.3f});')
J(f'tl.to("#guide", {{scale:1.05, duration:0.18, yoyo:true, repeat:1}}, {t(65.35)});')
pop_in("#cbox", t(65.85), 0.45, 0.85, ease="power3.out")
J('tl.set("#ccar", {opacity:0}, 0);')
word = "CLAUDE"
t0 = m(66.40)
J(f'tl.set("#ccar", {{opacity:1}}, {t0 - 0.2:.3f}); tl.set("#cph", {{opacity:0}}, {t0:.3f});')
for k in range(1, len(word) + 1):
    J(f'tl.set("#ctxt", {{textContent:"{word[:k]}"}}, {t0 + (k - 1) * 0.09:.3f});')
J('tl.set("#ctxt", {textContent:""}, 0);')
click = m(67.85)
J(f'tl.set("#cur2", {{opacity:0, x:1000, y:1400}}, 0); tl.to("#cur2", {{opacity:1, duration:0.15}}, {click - 0.6:.3f});'
  f'tl.to("#cur2", {{x:905, y:1100, duration:0.5, ease:"power2.inOut"}}, {click - 0.55:.3f});'
  f'tl.to("#cur2", {{scale:0.82, duration:0.07, yoyo:true, repeat:1}}, {click:.3f});'
  f'tl.to("#csend", {{scale:0.86, duration:0.07, yoyo:true, repeat:1}}, {click:.3f});')
J(f'tl.set("#cdone", {{opacity:0, scale:0.4}}, 0); tl.to("#cdone", {{opacity:1, scale:1, duration:0.35, ease:"back.out(2)"}}, '
  f'{click + 0.16:.3f}); tl.to("#cur2", {{opacity:0, duration:0.3}}, {click + 0.4:.3f});')

J(f'tl.to(["#cbox","#cdone"], {{y:230, duration:0.6, ease:"power3.inOut"}}, {SPEECH + 0.05:.3f});'
  f'tl.to("#guide", {{y:120, scale:1.08, duration:0.6, ease:"power3.inOut"}}, {SPEECH + 0.05:.3f});')

# ------------------------------------------------------------------ real UI B-roll (official Claude Code Projects video + usage tab)
HL = {6: [((600, 55, 280, 46), 44.55), ((600, 216, 280, 46), 44.75), ((600, 138, 280, 46), 46.55), ((600, 296, 280, 46), 46.75)]}
for i, (fa, fb, v, cs, crop, tag) in enumerate(BROLL):
    w, h = broll_geom(crop)
    a, b = m(fa), m(fb)
    d = b - a + 0.25
    hls = "".join(f'<div id="hl{i}{k}" style="position:absolute; left:{x}px; top:{y}px; width:{ww}px; height:{hh}px;'
                  f'border:4px solid {CORAL}; border-radius:12px; box-shadow:0 0 0 6px rgba(208,105,79,.18)"></div>'
                  for k, ((x, y, ww, hh), _) in enumerate(HL.get(i, [])))
    el(f"br{i}", f"position:absolute; left:{(1080 - w) // 2}px; top:{BOX_CY - h // 2}px; width:{w}px; height:{h}px; border-radius:26px;"
       "overflow:hidden; background:#fff; box-shadow:0 24px 60px rgba(40,25,10,.22), 0 0 0 3px #E4DCCF;",
       f'<div id="brz{i}" style="position:absolute; inset:0">'
       f'<video id="brv{i}" class="clip" src="assets/br{i}.mp4" muted playsinline data-start="{a:.3f}" data-duration="{d:.3f}" '
       f'data-media-start="0" style="width:{w}px; height:{h}px; display:block"></video>{hls}</div>')
    el(f"brt{i}", f"position:absolute; left:{(1080 - w) // 2 + 22}px; top:{BOX_CY - h // 2 - 30}px; padding:12px 22px 8px;"
       f"background:{CORAL}; color:#fff; border-radius:14px; font-family:Plek; font-size:30px; white-space:nowrap", tag)
    J(f'tl.set("#br{i}", {{opacity:0, scale:0.94, y:30}}, 0); tl.to("#br{i}", {{opacity:1, scale:1, y:0, duration:0.32, '
      f'ease:"power3.out"}}, {a:.3f}); tl.to("#br{i}", {{opacity:0, duration:0.14}}, {b - 0.14:.3f});')
    J(f'tl.set("#brz{i}", {{scale:1, transformOrigin:"50% 45%"}}, 0); tl.to("#brz{i}", {{scale:1.06, duration:{d:.3f}, ease:"none"}}, {a:.3f});')
    J(f'tl.set("#brt{i}", {{opacity:0, y:12}}, 0); tl.to("#brt{i}", {{opacity:1, y:0, duration:0.3, ease:"back.out(2)"}}, {a + 0.15:.3f});'
      f'tl.to("#brt{i}", {{opacity:0, duration:0.14}}, {b - 0.14:.3f});')
    for k, (_, at) in enumerate(HL.get(i, [])):
        J(f'tl.set("#hl{i}{k}", {{opacity:0, scale:1.15}}, 0); tl.to("#hl{i}{k}", {{opacity:1, scale:1, duration:0.25, '
          f'ease:"back.out(2)"}}, {t(at)});')
J('tl.to("#root", {backgroundPosition:"0px 120px", duration:' + f'{DUR}' + ', ease:"none"}, 0);')

# ------------------------------------------------------------------ write
grid = (f"background-color:{CREAM}; background-image:linear-gradient(rgba(60,45,30,.06) 2px, transparent 2px),"
        "linear-gradient(90deg, rgba(60,45,30,.06) 2px, transparent 2px); background-size:60px 60px; background-position:0 0;")
doc = f'''<!doctype html><html lang="en" data-resolution="portrait"><head><meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face {{ font-family:Plek; src:url("assets/plek.ttf"); }}

* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:{CREAM}; }}
#root {{ position:relative; width:{W}px; height:{H}px; overflow:hidden; {grid}
  font-family:"Helvetica Neue", Helvetica, Arial, sans-serif; }}
.h1 {{ font-size:66px; font-weight:500; color:{INK}; letter-spacing:-1.5px; line-height:1.0; }}
.h2wrap {{ position:relative; display:inline-block; margin-top:-2px; }}
.h2 {{ display:inline-block; font-family:Baskerville; font-style:italic; font-size:104px; color:{CORAL}; line-height:1.08;
  letter-spacing:-1px; }}
.ul {{ position:absolute; left:4%; right:4%; bottom:4px; height:5px; border-radius:3px; background:{CORAL}; opacity:.85;
  transform-origin:left center; }}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
{chr(10).join(html)}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
tl.set({{}}, {{}}, {DUR});
window.__timelines["main"] = tl;
tl.seek(0);
</script></body></html>'''
open(os.path.join(os.path.dirname(__file__), "index.html"), "w").write(doc)
print("ok", DUR, "s,", len(html), "elements,", len(js), "js lines")
