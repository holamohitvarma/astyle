# Hermes x Bluehost reel (v1, 2026-10-13), Farhan v4 style
- Source: raw.mp4 (1920x1080 25fps, 39.5 s, Drive "hermes bluehost_1080p.mp4") + raw.srt (TurboScribe watermark stripped).
- B-roll (Drive folder 1JCm7Zpd5X_necaEu9EB_KxKMq_Klrdhh) in broll/: hermes_sr1 (Bluehost terminal + Claude Code),
  rec_0720 (Bluehost VPS pages / app picker), video_57359 + hermes_setup_720p (other creators' Bluehost ads, screen
  parts only, faces and burned captions cropped out), whatsapp_0846 (Hermes in Telegram).
- Pipeline: timing.py (pause trims, source->edit map) -> cut.py (B-roll clips, A-roll tail, dialogue-edit.wav)
  -> build.py (editable.json + anim.json) -> `tsrct project commit` then `tsrct project apply`.
  Re-cut clips must be imported under a new asset id (build.py ALIAS), e.g. b08r / b09r.
- Layouts: SPLIT (top 1080x960: B-roll cover, window card on cream grid, or native graphic; bottom: Farhan zoomed
  125%/136% alternating on every pause trim, eyes at (540,1290)), BROLL (full-screen B-roll, fitted + padded/blurred),
  FULL (Farhan 185%/197%, eyes (540,774), titles in Helvetica Bold + Baskerville Italic coral), CTA (comment box typing DEPLOY).
- Native graphics: learn/task/skill loop, Claude plan vs other subscription ($0 extra), Docker / SSL strike-through,
  repeat asks x3 -> "fetch_job" skill (name seen in the Telegram B-roll), QUIT stamp, 24/7 badge, LIVE pill.
- Captions: Foundry Plek, ALL CAPS, tracking -1 (all text is tracking -1), white on black 55 %, coral keywords; y 960 on
  SPLIT, 1430 on FULL, 1560 on BROLL; hidden on title / punch / no-docker beats. SRT fixes: "Cloud plan" -> "Claude plan", 24x7 -> 24/7.
- 15 pauses trimmed to 0.24 s (39.5 -> 36.3 s speech + 0.9 s tail = 37.2 s).
- Audio: dialogue highpass 80 Hz + light compression + loudnorm -16.5 LUFS; 57 SFX from the v4 set, no music.
- Fonts (Helvetica.ttc, Baskerville.ttc, Plek) come from the v4 project; licensed, kept out of git (Assets/fonts/).
- Rendering here is CPU (Mesa lavapipe); export uses --encoder-backend external-ffmpeg-command --ffmpeg-path /usr/bin/ffmpeg.
- Not auditioned by ear (cloud session): audio checked by loudness measurement only.

## v2 (2026-10-13): split screen only
- User: no motion graphics; the whole reel is the SPLIT layout (B-roll top, Farhan zoomed bottom).
- Beats in beats_v2.py (every beat SPLIT, new B-roll for the former graphic / full-frame beats); clips c*.mp4,
  clip_ms_v2.json; re-cuts imported as c00r / c03r / c17r (build.py ALIAS).
- Build: `V=v2 python3 cut.py && V=v2 python3 build.py`, then commit editable_v2.json to hermes-bluehost-v2.tsrct
  and apply anim_v2.json. v1 project/scripts untouched (V defaults to v1).
- Captions unchanged (Plek, ALL CAPS, tracking -1) on the seam for the whole video; layout-change whoosh/tap SFX kept.
- Skipped the SSH-login terminal shot (shows the server IP and login).
