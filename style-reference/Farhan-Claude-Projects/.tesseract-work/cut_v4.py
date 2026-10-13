"""Cut v4 B-roll clips: crop, scale (no AI upscale), letterbox SPLIT clips on the UI's own bg colour, freeze after maxlen."""
import subprocess
from timing import m, O_SRC, C_SRC
from beats_v4 import BEATS, clip_size


def bg_colour(src, t, x, y):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", src, "-frames:v", "1", "-vf", f"crop=4:4:{x}:{y},scale=1:1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return "0x%02X%02X%02X" % tuple(raw[:3])


for i, (fa, fb, lay, clip, opt) in enumerate(BEATS):
    if not clip:
        continue
    v, cs, (x, y, cw, ch) = clip
    src = O_SRC if v == "O" else C_SRC
    d = m(min(fb, 68.62)) - m(fa) + 0.2
    L = min(d, opt.get("maxlen", d))
    W, H = clip_size(lay, (x, y, cw, ch))
    if lay == "SPLIT":
        k = min(1080 / cw, 960 / ch)
        sw, sh = int(round(cw * k / 2) * 2), int(round(ch * k / 2) * 2)
        col = bg_colour(src, cs + 0.3, x + 2, y + 2)
        fit = f"scale={sw}:{sh}:flags=lanczos,pad=1080:960:(ow-iw)/2:(oh-ih)/2:color={col}"
    else:
        fit = f"scale={W}:{H}:flags=lanczos"
    vf = (f"crop={cw}:{ch}:{x}:{y},{fit},unsharp=5:5:0.4,fps=30,"
          f"tpad=stop_mode=clone:stop_duration={d:.2f},trim=duration={d:.3f},setsar=1")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{cs:.3f}", "-t", f"{L:.3f}", "-i", src, "-vf", vf, "-an",
                    "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", f"../Assets/v4/b{i:02d}.mp4"], check=True)
    print(i, lay, v, cs, W, H, f"motion {L:.2f}s of {d:.2f}s")
