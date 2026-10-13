"""Beat sheet. Times are Farhan SOURCE seconds (cuts sit in trimmed pauses where possible).
clip = (broll file, clip_src_start, crop x,y,w,h in that file's pixels, fit)
  fit "cover"  -> SPLIT: fills the 1080x960 top pane (crop is already 9:8)
  fit "window" -> SPLIT: rounded window card on the cream pane
  fit "full"   -> BROLL: fitted to 1080 wide, centred, padded with `pad` colour (or blurred fill)
Layouts: FULL (Farhan full frame, optional title / graphic), SPLIT (B-roll or native graphic top, Farhan zoomed bottom),
BROLL (full-screen B-roll), CTA (Farhan full + comment-box end card).
opt: maxlen = seconds of real motion before freezing, hl = coral highlight [(x,y,w,h) in pane px, src time],
     graphic = native top-pane motion graphic id, title / punch = FULL-frame type."""

BEATS = [
    (0.28, 2.10, "FULL", None, {"title": ("SETTING UP A SERVER", "for an AI agent", 0.34, 1.30), "hook": True}),
    (2.10, 3.87, "SPLIT", ("hermes_sr1", 138.6, (160, 200, 652, 580), "cover"), {"stamp": ("QUIT.", 3.28)}),
    (3.87, 5.00, "FULL", None, {"punch": ("Watch this.", 4.14)}),
    (5.00, 7.00, "BROLL", ("hermes_setup_720p", 3.70, (0, 300, 720, 600), "full"), {"pad": "0xEEECE8"}),
    (7.00, 10.48, "SPLIT", None, {"graphic": "loop"}),
    (10.48, 13.00, "SPLIT", ("hermes_sr1", 70.0, (160, 200, 1090, 320), "window"), {}),
    (13.00, 15.62, "SPLIT", None, {"graphic": "nosub"}),
    (15.62, 18.88, "SPLIT", ("rec_0720", 0.4, (200, 131, 783, 331), "window"), {"badge": ("24/7", 17.62)}),
    (18.88, 21.20, "SPLIT", ("video_57359", 13.9, (0, 60, 720, 640), "cover"),
     {"maxlen": 1.0, "hl": [((352, 652, 270, 66), 19.12), ((750, 466, 330, 70), 20.30)]}),
    (21.20, 21.95, "BROLL", ("video_57359", 7.6, (0, 0, 720, 715), "full"), {"pad": "0x0F2235", "maxlen": 1.2}),
    (21.95, 23.15, "SPLIT", ("rec_0720", 30.2, (228, 92, 872, 500), "window"), {}),
    (23.15, 25.45, "FULL", None, {"graphic": "nodocker"}),
    (25.45, 26.63, "SPLIT", ("whatsapp_0846", 0.2, (490, 0, 635, 565), "cover"), {}),
    (26.63, 29.87, "BROLL", ("whatsapp_0846", 4.4, (490, 0, 635, 636), "full"), {"pad": "blur", "live": 28.46}),
    (29.87, 31.38, "FULL", None, {"title": ("THEN IT", "improves.", 30.06, 30.64)}),
    (31.38, 35.35, "SPLIT", None, {"graphic": "skills"}),
    (35.35, 37.02, "FULL", None, {}),
    (37.02, 99.0, "CTA", None, {}),
]

SPLIT_Y = 960
WIN_W = 960
CAPTION_OFF = ("FULL-TITLE",)        # beats with a title / punch / nodocker graphic hide captions (see build)
CAP_Y = {"SPLIT": 960, "FULL": 1430, "BROLL": 1560, "CTA": 1430}


def clip_size(fit, crop):
    w, h = crop[2], crop[3]
    if fit == "cover":
        return 1080, 960
    if fit == "full":
        return 1080, 1920
    return WIN_W, int(round(WIN_W * h / w / 2) * 2)
