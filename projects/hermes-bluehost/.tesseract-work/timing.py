"""Shared edit timeline for the Hermes x Bluehost reel (Farhan v4 style).
Source pauses (silencedetect -40 dB, >=0.28 s) are trimmed to GAP seconds; everything is authored in
source seconds and mapped to edit time with m()."""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "raw.mp4")
SRT = os.path.join(ROOT, "raw.srt")
SRC_DUR = 39.488
IN, OUT = 0.28, 39.40          # first word 0.34, last word ends 39.16
TAIL = 0.90                    # CTA end hold (Farhan frozen, aroll-tail)
GAP = 0.24

SIL = [(3.604, 4.143), (4.727, 5.270), (10.232, 10.721), (15.328, 15.915), (18.600, 19.154), (19.887, 20.364),
       (21.791, 22.109), (22.995, 23.306), (25.190, 25.703), (26.456, 26.810), (29.698, 30.045), (31.236, 31.525),
       (35.148, 35.549), (36.807, 37.241)]

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


if __name__ == "__main__":
    print(f"{len(keeps)} segments, speech {SPEECH:.2f}s, edit {DUR:.2f}s")
