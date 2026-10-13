"""Cut B-roll clips (crop, lanczos scale, no AI upscale, freeze after maxlen), the A-roll tail freeze and the
edited dialogue (pause trims with 10 ms fades, highpass + light compression + loudnorm). Writes clip_ms.json."""
import json
import os
import subprocess

from timing import m, keeps, SRC, OUT, TAIL, ROOT, HERE
V = os.environ.get("V", "v1")                       # V=v2 -> beats_v2, clips c*.mp4, clip_ms_v2.json
if V == "v2":
    from beats_v2 import BEATS, clip_size
else:
    from beats import BEATS, clip_size
PFX, SUF = ("c", "_v2") if V == "v2" else ("b", "")

A = os.path.join(ROOT, "Assets")
os.makedirs(os.path.join(A, "clips"), exist_ok=True)


def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True, check=True).stdout)


clip_ms = {}
for i, (fa, fb, lay, clip, opt) in enumerate(BEATS):
    if not clip:
        continue
    name, cs, (x, y, cw, ch), fit = clip
    src = os.path.join(ROOT, "broll", name + ".mp4")
    d = m(min(fb, OUT)) - m(fa) + 0.2 + (TAIL if i == len(BEATS) - 1 else 0)
    L = min(d, opt.get("maxlen", d))
    W, H = clip_size(fit, (x, y, cw, ch))
    tail = f"unsharp=5:5:0.4,fps=30,tpad=stop_mode=clone:stop_duration={d:.2f},trim=duration={d:.3f},setsar=1"
    if fit == "full":
        sh = int(round(ch * 1080 / cw / 2) * 2)
        if opt.get("pad") == "blur":
            vf = (f"crop={cw}:{ch}:{x}:{y},split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
                  f"crop=1080:1920,boxblur=40:2,eq=brightness=-0.06[bg];[b]scale=1080:{sh}:flags=lanczos[fg];"
                  f"[bg][fg]overlay=0:(H-h)/2,{tail}")
        else:
            vf = f"crop={cw}:{ch}:{x}:{y},scale=1080:{sh}:flags=lanczos,pad=1080:1920:0:(oh-ih)/2:color={opt['pad']},{tail}"
    else:
        vf = f"crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos,{tail}"
    out = os.path.join(A, "clips", f"{PFX}{i:02d}.mp4")
    ff("-ss", f"{cs:.3f}", "-t", f"{L:.3f}", "-i", src, "-filter_complex" if ";" in vf else "-vf", vf, "-an",
       "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", out)
    clip_ms[f"{PFX}{i:02d}"] = int(dur(out) * 1000)
    print(i, lay, name, cs, W, H, f"motion {L:.2f}s of {d:.2f}s")

# A-roll tail: freeze the last kept frame for the CTA end hold
tail = os.path.join(A, "aroll-tail.mp4")
ff("-ss", f"{OUT - 0.05:.3f}", "-i", SRC, "-vf", f"fps=25,tpad=stop_mode=clone:stop_duration={TAIL + 0.5},setsar=1",
   "-t", f"{TAIL + 0.5:.2f}", "-an", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", tail)
clip_ms["aroll-tail"] = int(dur(tail) * 1000)

# Dialogue: kept segments with 10 ms fades, concatenated, then cleaned and normalised
parts, labels = [], []
for k, (a, b) in enumerate(keeps):
    dd = b - a
    parts.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,"
                 f"afade=t=out:st={dd - 0.01:.3f}:d=0.01[s{k}]")
    labels.append(f"[s{k}]")
fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(keeps)}:v=0:a=1,apad=pad_dur={TAIL}," \
     "highpass=f=80,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2," \
     "loudnorm=I=-16.5:TP=-2:LRA=9,aresample=48000[out]"
ff("-i", SRC, "-filter_complex", fc, "-map", "[out]", "-ac", "2", "-c:a", "pcm_s16le",
   os.path.join(A, "dialogue-edit.wav"))
json.dump(clip_ms, open(os.path.join(HERE, f"clip_ms{SUF}.json"), "w"), indent=1)
print(clip_ms)
