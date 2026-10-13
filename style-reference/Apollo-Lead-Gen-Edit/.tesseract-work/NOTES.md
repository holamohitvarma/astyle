# Apollo x Claude lead-gen, 9:16 edit
- Source: ~/Downloads/claude + apollo_1080p.mp4 (1920x1080, 74.88s, single take) + claude + apollo 1080p.srt (TurboScribe watermark stripped).
- Style (from 8 reference videos): split screen, top 45% native motion-graphic visuals (white/blue node diagrams, highlights, dark serif hook, profile-card end), bottom 55% talking head, grey pill captions (2-4 words) on the seam.
- No cuts: continuous take, speaker scaled 102% and cropped to 1080-wide window (also crops out the BechoMaxx logo).
- Audio: original muted in the video layer; replaced by normalized derivative (highpass 80Hz, compress, loudnorm) -> -16.3 LUFS / -2.3 dBTP final. Procedural whoosh/pop/ping accents, no music.
- Rebuild: python3 .tesseract-work/build.py <srt> 102 -478 836, then project commit + apply anim.json.
- Limits: no real Apollo/Claude UI footage supplied, so visuals are illustrative native graphics (no invented screens/metrics). Export fps 30 (25 not offered). Not auditioned by ear.

## v2 (2026-10-05): reference-matched rebuild
- Script: .tesseract-work/build_v2.py (source-time authored, mapped through pause trim). Commit editable_v2.json then apply anim_v2.json.
- 21 pauses >=0.33s trimmed to 0.24s (74.9s -> 69.4s). Jump cuts alternate wide (102%) / punch-in (110%) with eyes and centre held.
- Top pane: tutorial freeze-frames (left-cropped to hide the creator's face-cam and "Bilal" greeting) with push-ins, yellow highlight sweeps and rings; 5 Veo clips (muted); Apollo/Claude splashes; title stack + series pills; SKIP stamps; comment-bar typing CTA; profile card with Follow click.
- Seam: user's torn-paper PNG. Captions: Helvetica Neue Bold 46, grey pills, <=3 words.
- Audio: normalized dialogue, procedural placeholder music bed (layer "Music bed", vol 0.30), procedural whoosh/pop/tap/click/ping. Final -16.1 LUFS / -1.8 dBTP.
- Avatar is a frame grab from the footage. Profile stats copied from reference videos.

## v3 (2026-10-05): reference-measured rebuild
- Script: .tesseract-work/build_v3.py -> editable_v3.json + anim_v3.json (commit, then apply).
- Live tutorial clips (asset "tut") instead of stills; face-cam kept out by centring x<=930 at 116.7%.
- Fonts (measured): captions Helvetica Neue Bold 47 px (ref "Founders." 226 px vs ours 223 px); small title HN Regular 47, tracking -10; big title HN Bold 96, tracking -30. SF Pro is not importable (variable font >256 instances).
- Caption pill: black @45 % (ref measured 49 % Lead Gen / 26 % P2), h 80, radius 14, centred on the hard seam at 840.
- Speaker: fixed framing 102 %, Levels (0-255 scale!) inputWhite 224, gamma 1.14, outputBlack 15 -> Y avg 149 / low 73 / high 198 (refs 133-165 / 64-109 / 174-200).
- Flash + light-leak transitions at 6.84, 21.0, 45.17, 51.65, 71.95 src; impacts on 3, whoosh on 2, riser at open. No music (user: skip for now).
- Full-screen moments: spreadsheet (src 45.17-51.65) and final 1.5 s end card.

## v3.1 (2026-10-05)
- Removed 4 lines for pace (LINE_CUTS in build_v3.py): decision makers, in-house, rarely outsource, match to service. CEO Veo clip + its flash dropped. 62.4 s, -16.2 LUFS / -2.0 dBTP. All cut points sit inside measured silences.

## v3.2 (2026-10-06)
- Script build_v32.py -> editable_v32.json/anim_v32.json. Apollo splash is a still (live clip ran into face-cam). Thinking beats moved to T=473.6/473.9 (creator appears at ~475.3).
- Filter shots at 160% centred (593,262); employee/location panel at 200% from 3:37. Stock clips 1.4-1.5 s with UI between + gradient labels. Prompt zoomed out to 93-97%; emails 114% full width.
- Drift +4% on single-view shots, sharpen 35 on tutorial, levels + temperature on Veo. Speaker at (-470, 808) behind top pane, grade gamma 1.18 / outputBlack 8.
- Flash 65% / 360 ms (+ Apollo flash). Stickers outward. CTA bar lower, typing immediately; no white gap before profile; bigger travelling cursor; final card 165%.
- Captions: weak-word carry rule, 2px 35% dark outline, full-screen captions at y 1480. 62.4 s, -16.2 LUFS / -2.0 dBTP.
