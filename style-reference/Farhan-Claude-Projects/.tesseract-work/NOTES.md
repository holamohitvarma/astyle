# Farhan - Claude Code Projects reel (v1, 2026-10-10)
- Source: ~/Downloads/Claude Projects Update_1080p (1).mp4 (1920x1080 25fps, 68.7s) + SRT (TurboScribe watermark stripped).
- Reference: Austin Marchese "auto-improving system" reel (cream grid page, header, visual, rounded A-roll card, full-frame punches).
- Pipeline: .tesseract-work/timing.py (pause trims, source->edit map) -> hf/gen.py (HyperFrames graphics: headers + diagrams,
  edit time) -> render Assets/graphics.mp4 -> .tesseract-work/build.py (card, punches, captions, audio) -> commit + apply anim.json.
- Render graphics: cd ~/Desktop/content-agent/.tools/hyperframes && PATH=$PWD/bin:$PATH npx hyperframes render <proj>/hf -o <proj>/Assets/graphics.mp4 --fps 30 --quality delivery
- 18 pauses trimmed to 0.24s (68.7 -> 64.3s). Card alternates 88%/96% on each cut, eyes held at (540,1520).
- Captions: Foundry Plek dot-matrix 50px white on black 55%, straddling the card top. Headers Helvetica Neue + Baskerville Italic.
  (STIX Two italic is rejected by tsrct font import.)
- Model labels: coordinator Sonnet / low effort, threads Opus / max effort. No music; ~69 procedural SFX.
- Audio: highpass + light compression + loudnorm -> -16.5 LUFS / -1.9 dBTP final.

## v2 (2026-10-10)
- Real B-roll (timing.BROLL): 8 clips from the official "Getting started with Claude Code Projects" video + the usage tab
  from the "Massive Upgrade" creator video (5:29.8, cropped to exclude his face-cam, frozen before his zoom-out).
  Clips are pre-cut/cropped into hf/assets/br*.mp4 and shown as rounded cards with a coral tag + push-in.
- Coordinator diagram replaced by real UI; settings clip gets coral highlights on model/effort rows.
- Brains cards now show the real defaults: Opus 5.5 for both, coordinator low effort, threads max.
- 6 full-frame punches (hook, Number one/two/three, cool part, really matters) with slow push-in.
- Card tighter (100%/108%), warm grade (levels + temperature 12 + vibrance 8) on all Farhan layers.
- Captions: hand-chunked (build.CHUNKS), coral keywords via per-segment layers using the font's real advances.
- Dialogue: single pre-edited track (dialogue-edit.wav) with 10 ms fades at every pause trim.
- 1.2 s CTA end hold; grid drifts slowly. Graphics asset = graphics3 (Assets/graphics-v2.mp4).
- Rebuild: python3 .tesseract-work/build.py <graphics ms>; commit editable.json; apply anim.json.

## v3 (2026-10-10): rotating layouts
- Project: project_v3.tsrct (v2 stays in project.tsrct). Script: .tesseract-work/build_v3.py, beats in beats_v3.py.
- 24 beats, layout changes on sentence breaks (~3 s): SPLIT (B-roll top / Farhan bottom), FULL (Farhan + title),
  BROLL (full-screen B-roll + Farhan circle top-right), DESK (cream workspace window + Farhan card), FLOAT (Farhan full
  + floating window), NUM (01/02/03 dot-matrix number + Baskerville title over dimmed Farhan).
- Caption fixed at screen centre (y 960) on every layout; dot-matrix white on black 55 %, coral keywords.
- All graphics native in Tesseract (HyperFrames no longer used); CTA comment box typing CLAUDE is native layers.
- B-roll pre-cut (lanczos, no AI upscaling) to Assets/v3/b*.mp4; durations in clip_ms.json; per-beat "aid" overrides.
- Rebuild: python3 .tesseract-work/build_v3.py; commit editable_v3.json to project_v3.tsrct; apply anim_v3.json.

## v4 (2026-10-10): review fixes
- Project project_v4.tsrct; scripts beats_v4.py, cut_v4.py (clip cutter), build_v4.py. Clips Assets/v4/b*.mp4 (ids v4bNN,
  v4b08r / v4b21r are re-cuts), tail freeze aroll-tail2, dialogue-edit-v4.wav (TAIL 0.8 s).
- Every clip has maxlen so it freezes before the source cuts to the presenter / dissolves / camera moves.
- SPLIT clips are letterboxed on the UI's own bg colour; FLOAT window sits at y 90 (above Farhan's hairline).
- Re-picked B-roll: coordinator welcome text, You->Coordinator, typed brief, branching, live thread list, threads panel
  (no "Welcome, Delba" header), PR rows, memory, instructions, settings, open model dropdown, effort highlight,
  thread work log, usage (Tokens 857.2k highlighted, "Threads 0" covered), parallel thread list.
- Captions hidden on FULL/NUM title beats; NUM beats 1.2-1.35 s; native 3-things list card; hook zoom-out reveal;
  whoosh on alternate cuts (soft tap otherwise); CTA cursor tap; Farhan held in card through the tail.
