"""v2 beat sheet: the whole reel is SPLIT (B-roll top, Farhan zoomed bottom). No motion graphics, titles or
full-screen layouts. Times are Farhan SOURCE seconds; clip = (broll file, clip_src_start, crop x,y,w,h, fit)."""

BEATS = [
    (0.28, 2.10, "SPLIT", ("video_57359", 1.5, (0, 40, 720, 640), "cover"), {"maxlen": 1.3}),
    (2.10, 3.87, "SPLIT", ("hermes_sr1", 138.6, (160, 200, 652, 580), "cover"), {}),
    (3.87, 5.00, "SPLIT", ("rec_0720", 6.5, (200, 0, 800, 330), "window"), {}),
    (5.00, 7.00, "SPLIT", ("hermes_setup_720p", 3.9, (90, 400, 540, 480), "cover"), {"maxlen": 1.4}),
    (7.00, 10.48, "SPLIT", ("hermes_setup_720p", 19.0, (90, 60, 540, 480), "cover"), {"maxlen": 2.0}),
    (10.48, 13.00, "SPLIT", ("hermes_sr1", 70.0, (160, 200, 1090, 320), "window"), {}),
    (13.00, 15.62, "SPLIT", ("hermes_sr1", 189.0, (170, 240, 580, 515), "cover"), {}),
    (15.62, 18.88, "SPLIT", ("video_57359", 9.5, (90, 240, 540, 480), "cover"), {"maxlen": 1.6}),
    (18.88, 21.20, "SPLIT", ("video_57359", 13.9, (0, 60, 720, 640), "cover"), {"maxlen": 1.0}),
    (21.20, 21.95, "SPLIT", ("video_57359", 7.6, (0, 80, 720, 640), "cover"), {}),
    (21.95, 23.15, "SPLIT", ("rec_0720", 30.2, (228, 92, 872, 500), "window"), {}),
    (23.15, 25.45, "SPLIT", ("rec_0720", 0.4, (200, 131, 783, 331), "window"), {}),
    (25.45, 26.63, "SPLIT", ("whatsapp_0846", 0.2, (490, 0, 635, 565), "cover"), {}),
    (26.63, 29.87, "SPLIT", ("whatsapp_0846", 4.4, (490, 0, 635, 565), "cover"), {}),
    (29.87, 31.38, "SPLIT", ("video_57359", 24.0, (0, 80, 720, 640), "cover"), {}),
    (31.38, 35.35, "SPLIT", ("hermes_setup_720p", 36.0, (40, 380, 640, 569), "cover"), {"maxlen": 3.5}),
    (35.35, 37.02, "SPLIT", ("hermes_sr1", 223.0, (162, 270, 1080, 500), "window"), {}),
    (37.02, 99.0, "SPLIT", ("hermes_setup_720p", 42.0, (90, 60, 540, 480), "cover"), {"maxlen": 1.0}),
]

SPLIT_Y = 960
WIN_W = 960
CAP_Y = {"SPLIT": 960}


def clip_size(fit, crop):
    w, h = crop[2], crop[3]
    if fit == "cover":
        return 1080, 960
    if fit == "full":
        return 1080, 1920
    return WIN_W, int(round(WIN_W * h / w / 2) * 2)
