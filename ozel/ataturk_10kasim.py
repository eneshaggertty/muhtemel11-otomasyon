"""10 Kasım anma Reels'i (1080x1920, sessiz, ~16 sn)."""
import math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402
import render, reels  # noqa: E402

W, H, FPS, SURE = 1080, 1920, 30, 16
kok = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "posts", "ozel")
cikti = os.path.join(kok, "2026-11-10-ataturk.mp4")
f = render.font
BEYAZ, GRI, KIRMIZI = (245, 245, 245), (150, 150, 155), (210, 20, 35)

def ease(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

zemin = Image.new("RGB", (W, H), (0, 0, 0))
g = Image.new("RGB", (W, H), (0, 0, 0))
ImageDraw.Draw(g).ellipse([-200, 200, W + 200, 1500], fill=(28, 28, 32))
zemin = Image.blend(zemin, g.filter(ImageFilter.GaussianBlur(220)), 1.0)

def katman(ciz):
    k = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ciz(ImageDraw.Draw(k)); return k

def ortala(d, y, t, fnt, renk):
    d.text(((W - d.textlength(t, font=fnt)) / 2, y), t, font=fnt, fill=renk)

def saat(d):
    cx, cy, r = W / 2, 560, 210
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BEYAZ, width=6)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        r1 = r - (34 if i % 3 == 0 else 20)
        d.line([cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + (r - 10) * math.cos(a), cy + (r - 10) * math.sin(a)],
               fill=BEYAZ, width=6 if i % 3 == 0 else 3)
    # 09:05 -> akrep 9 + 5/60 saat, yelkovan 5 dk
    ak = math.radians((9 + 5 / 60) * 30 - 90); yk = math.radians(5 * 6 - 90)
    d.line([cx, cy, cx + 115 * math.cos(ak), cy + 115 * math.sin(ak)], fill=BEYAZ, width=12)
    d.line([cx, cy, cx + 175 * math.cos(yk), cy + 175 * math.sin(yk)], fill=BEYAZ, width=7)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=KIRMIZI)

def ust(d):
    d.rectangle([W / 2 - 60, 200, W / 2 + 60, 206], fill=KIRMIZI)
    ortala(d, 228, "10 KASIM 1938", f("Inter-SemiBold.otf", 40), GRI)

def baslik(d):
    ortala(d, 850, "09.05", f("InterDisplay-Black.otf", 120), BEYAZ)
    ortala(d, 1010, "SAYGI VE ÖZLEMLE", f("InterDisplay-Black.otf", 76), BEYAZ)
    ortala(d, 1100, "ANIYORUZ", f("InterDisplay-Black.otf", 76), BEYAZ)

def soz(d):
    sf = f("Inter-Medium.otf", 36)
    satirlar = ["“Benim naçiz vücudum elbet bir gün", "toprak olacaktır, ancak Türkiye", "Cumhuriyeti ilelebet payidar kalacaktır.”"]
    for i, s in enumerate(satirlar):
        ortala(d, 1290 + i * 54, s, sf, (210, 210, 215))
    ortala(d, 1470, "— Mustafa Kemal Atatürk", f("Inter-SemiBold.otf", 32), GRI)

def imza(d):
    ortala(d, 1730, render.config.HANDLE if hasattr(render, "config") else "@muhtemel11onbir", f("InterDisplay-Bold.otf", 30), (120, 120, 125))

parcalar = [(katman(ust), 0.3, 1.5), (katman(saat), 1.0, 2.0), (katman(baslik), 3.0, 1.5),
            (katman(soz), 6.0, 2.0), (katman(imza), 9.0, 1.5)]
cmd = [reels.ffmpeg_yolu(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
       "-i", "-", "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000", "-shortest",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
       "-movflags", "+faststart", cikti]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for i in range(SURE * FPS):
    t = i / FPS
    kare = zemin.copy().convert("RGBA")
    for k, bas, sure in parcalar:
        a = ease((t - bas) / sure)
        if a > 0:
            kk = k.copy(); kk.putalpha(k.getchannel("A").point(lambda v, a=a: int(v * a)))
            kare.alpha_composite(kk)
    if t > SURE - 1.0:  # sonda yavaşça karar
        kare = Image.blend(kare.convert("RGB"), Image.new("RGB", (W, H)), ease((t - (SURE - 1.0)) / 1.0) * 0.6).convert("RGBA")
    p.stdin.write(kare.convert("RGB").tobytes())
    if i == 12 * FPS:
        kare.convert("RGB").save(cikti.replace(".mp4", ".jpg"), quality=92)
p.stdin.close(); p.wait()
print(cikti)
