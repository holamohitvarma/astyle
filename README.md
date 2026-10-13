# astyle: video editing style reference

The edit "recipe" from earlier Tesseract projects, so future cloud sessions can edit new videos in the same style.

## What's here

- `.claude/skills/`: the `tesseract-video` and `tesseract-motion` skills (CLI pin 0.2.0, Linux supported).
- `style-reference/`: the latest build scripts, edit/animation JSON, SFX, fonts and logos from three past edits:
  - `Farhan-Claude-Projects/`: v4, 9:16 rotating layouts (SPLIT / FULL / BROLL / DESK / FLOAT / NUM), cream grid,
    dot-matrix captions (Foundry Plek) with coral keywords, pause trims to 0.24 s, card 100%/108% on cuts, warm grade,
    procedural SFX, no music, -16.5 LUFS. See `.tesseract-work/NOTES.md`.
  - `Apollo-Lead-Gen-Edit/`: v3.2, split screen (top 45% motion graphics / bottom 55% talking head), torn-paper seam,
    grey pill captions (Helvetica Neue Bold 47, at most 3 words), flash + light-leak transitions, CTA comment typing,
    profile end card.
  - `Farhan-Claude-Skills/`: skill-card reel, Helvetica, no captions.

Not stored in git: the old versions, preview/check renders, B-roll clips and the `.tsrct` project files (150-180 MB each,
above GitHub's 100 MB limit). They stay in Google Drive.

## New edit

Put the new raw video, its `.srt` and the B-roll clips in `projects/<name>/` (raw video and B-roll are git-ignored when
large; share them in the session or via Drive).
