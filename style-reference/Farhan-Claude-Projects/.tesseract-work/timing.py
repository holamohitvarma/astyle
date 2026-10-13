"""Shared edit timeline for the Farhan 'Claude Code Projects' reel.
Source pauses (silencedetect -40 dB, >=0.28 s) are trimmed to GAP seconds; everything is authored in
source seconds and mapped to edit time with m()."""
import re

SRC = "/Users/mohitvarma/Downloads/Claude Projects Update_1080p (1).mp4"
SRT = "/Users/mohitvarma/Desktop/amrutt-style/Farhan-Claude-Projects/Assets/transcript.srt"
SRC_DUR = 68.694
IN, OUT = 0.26, 68.62          # first word 0.39, last word ends 68.47
TAIL = 0.80                    # hold after the last word (CTA end state, Farhan frozen in card)
GAP = 0.24

SIL = [(6.421, 6.921), (7.500, 7.944), (10.309, 10.783), (13.068, 13.536), (16.441, 16.786), (21.486, 21.905),
       (22.615, 22.991), (28.614, 29.369), (29.891, 30.435), (34.039, 34.481), (38.101, 38.889), (39.448, 40.005),
       (43.639, 44.076), (47.865, 48.390), (55.041, 55.538), (60.262, 60.782), (63.899, 64.365), (66.005, 66.301)]

keeps, a = [], IN
for s, e in SIL:
    keeps.append((a, s + GAP / 2))
    a = e - GAP / 2
keeps.append((a, OUT))

seg_edit, acc = [], 0.0
for a, b in keeps:
    seg_edit.append((a, b, acc))
    acc += b - a
SPEECH = acc
DUR = round(SPEECH + TAIL, 3)


def m(t):
    """source seconds -> edit seconds"""
    for a, b, e in seg_edit:
        if t < a:
            return e
        if t <= b:
            return e + t - a
    return SPEECH


def ms(t):
    return int(round(m(t) * 1000))


def cues():
    s = open(SRT, encoding="utf-8").read().replace("\r", "")
    out = []

    def ts(x):
        h, mm, r = x.split(":"); sec, f = r.split(",")
        return int(h) * 3600 + int(mm) * 60 + int(sec) + int(f) / 1000

    for blk in re.split(r"\n\s*\n", s.strip()):
        L = [l for l in blk.split("\n") if l.strip()]
        mt = re.match(r"(\S+) --> (\S+)", L[1])
        tx = re.sub(r"\(Transcribed by TurboScribe[^)]*\)\s*", "", " ".join(L[2:])).strip()
        if tx:
            out.append((ts(mt.group(1)), ts(mt.group(2)), tx))
    return out


# full-frame punch windows (source seconds): talking head fills the frame, big styled line instead of captions
# (start, end, (line1, line2, t_line1, t_line2))
FULL = [(0.26, 2.10, ("Claude just dropped a", "massive update", 0.39, 1.23)),
        (6.80, 7.55, ("", "Number one", 6.80, 6.87)),
        (21.80, 22.86, ("And the", "cool part?", 21.89, 22.13)),
        (29.10, 29.95, ("", "Number two", 29.10, 29.19)),
        (38.70, 39.55, ("", "Number three", 38.70, 38.75)),
        (55.42, 57.62, ("how you set this up", "really matters", 55.51, 56.65))]

O_SRC = "/Users/mohitvarma/Downloads/vidssave.com Getting started with Claude Code Projects 720P.mp4"
C_SRC = "/Users/mohitvarma/Downloads/vidssave.com Claude Projects Just Got a Massive Upgrade (Here’s What Changed) 720P.mp4"
# real B-roll: (farhan_src_start, farhan_src_end, video, clip_src_start, crop x,y,w,h in 1280x720, tag)
BROLL = [(2.10, 3.60, "O", 18.0, (0, 0, 1280, 720), "claude code projects"),
         (10.60, 13.40, "O", 25.4, (160, 90, 960, 540), "coordinator"),
         (13.40, 16.40, "O", 96.4, (60, 250, 1120, 470), "you brief it"),
         (16.40, 21.80, "O", 27.0, (0, 40, 1200, 675), "threads"),
         (22.86, 25.60, "O", 122.2, (642, 20, 616, 700), "thread status"),
         (32.90, 34.38, "O", 252.6, (60, 20, 1160, 640), "shared memory"),
         (44.00, 48.25, "O", 214.8, (330, 170, 836, 320), "project settings"),
         (57.62, 60.30, "C", 329.8, (140, 40, 940, 520), "usage"),
         (60.30, 62.85, "O", 14.6, (0, 0, 1280, 720), "parallel threads")]
BOX_W, BOX_H, BOX_CY = 960, 700, 850     # B-roll card fits inside this box, centred on BOX_CY


def broll_geom(crop):
    w, h = crop[2], crop[3]
    k = min(BOX_W / w, BOX_H / h)
    return int(round(w * k / 2) * 2), int(round(h * k / 2) * 2)


if __name__ == "__main__":
    print(f"{len(keeps)} segments, speech {SPEECH:.2f}s, edit {DUR:.2f}s")
    for a, b, t in FULL:
        print("full", round(m(a), 2), round(m(b), 2), t[:2])
    for r in BROLL:
        print("broll", r[5], round(m(r[1]) - m(r[0]), 2), broll_geom(r[4]))
