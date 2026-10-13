"""v4 beat sheet. Times are Farhan SOURCE seconds. Clip = (video, clip_src_start, crop x,y,w,h in 1280x720).
opt: maxlen = seconds of real motion before freezing (keeps clips clear of the source's cuts / camera moves),
     hl = coral highlight boxes [(x,y,w,h) in window px, src time], list = native 3-things card, cta = end card.
Layouts: SPLIT (B-roll top, letterboxed on matching bg / Farhan bottom), FULL (Farhan + title, no caption),
BROLL (full-screen B-roll + Farhan circle bottom-right), DESK (cream desk, window above / Farhan card below),
FLOAT (Farhan full + window above his head), NUM (big number, no caption)."""

BEATS = [
    (0.26, 2.10, "FULL", None, {"title": ("Claude just dropped a", "massive update", 0.39, 1.23), "hook": True}),
    (2.10, 3.60, "BROLL", ("O", 18.6, (40, 0, 405, 720)), {"maxlen": 0.6, "circle_top": True}),
    (3.60, 6.62, "DESK", None, {"list": True}),
    (6.62, 7.85, "NUM", None, {"num": ("01", "the coordinator", 6.87)}),
    (7.85, 10.60, "FLOAT", ("O", 90.3, (150, 50, 990, 412)), {}),
    (10.60, 13.40, "SPLIT", ("O", 25.6, (200, 200, 880, 380)), {"maxlen": 1.5}),
    (13.40, 16.40, "DESK", ("O", 96.4, (100, 430, 560, 240)), {}),
    (16.40, 19.00, "SPLIT", ("O", 27.2, (30, 60, 1170, 620)), {"maxlen": 2.6}),
    (19.00, 21.80, "DESK", ("O", 13.0, (30, 150, 1000, 430)), {}),
    (21.80, 22.86, "FULL", None, {"title": ("And the", "cool part?", 21.89, 22.13)}),
    (22.86, 25.60, "SPLIT", ("O", 122.0, (650, 170, 610, 540)), {"maxlen": 2.4}),
    (25.60, 28.88, "FLOAT", ("O", 129.0, (240, 130, 500, 210)), {"maxlen": 2.8}),
    (28.88, 30.20, "NUM", None, {"num": ("02", "shared memory", 29.19)}),
    (30.20, 34.38, "SPLIT", ("O", 249.6, (235, 0, 810, 720)), {"maxlen": 4.2}),
    (34.38, 38.50, "FLOAT", ("O", 239.3, (140, 470, 760, 300)), {}),
    (38.50, 39.85, "NUM", None, {"num": ("03", "different brains", 38.75)}),
    (39.85, 44.00, "FLOAT", ("O", 214.0, (340, 150, 780, 326)), {}),
    (44.00, 48.25, "SPLIT", ("O", 227.6, (360, 150, 760, 520)), {}),
    (48.25, 51.40, "DESK", ("O", 216.0, (340, 170, 780, 320)), {"hl": [((645, 146, 290, 50), 48.62)]}),
    (51.40, 55.42, "FLOAT", ("O", 115.0, (730, 20, 540, 230)), {}),
    (55.42, 57.62, "FULL", None, {"title": ("how you set this up", "really matters", 55.51, 56.65)}),
    (57.62, 60.30, "SPLIT", ("C", 330.1, (170, 150, 585, 520)), {"maxlen": 1.3, "cover": [(0, 14, 190, 66)], "shl": [((528, 16, 300, 62), 58.30)]}),
    (60.30, 64.20, "BROLL", ("O", 116.0, (50, 0, 405, 720)), {}),
    (64.20, 99.0, "DESK", None, {"cta": True}),
]

SPLIT_Y = 960
WIN_W = 960
FLOAT_TOP = 90          # floating window stays above Farhan's hairline (~y 530)
CAPTION_OFF = ("FULL", "NUM")


def clip_size(layout, crop):
    """Size of the pre-cut clip. SPLIT clips are letterboxed to 1080x960 (content fitted, padded with the UI bg)."""
    w, h = crop[2], crop[3]
    if layout == "SPLIT":
        return 1080, 960
    if layout == "BROLL":
        return 1080, 1920
    return WIN_W, int(round(WIN_W * h / w / 2) * 2)
