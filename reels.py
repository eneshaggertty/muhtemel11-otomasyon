"""Kart görsellerinden Instagram Reels videosu üretir (1080x1920, 30 fps, H.264 + sessiz AAC).

Her kart: alttan kayarak + yukarıdan aşağı açılarak gelir, sonra hafif yakınlaşır.
Birden fazla kart (carousel) art arda gösterilir. Sonda kısa bir "takip et" kapanışı var.
Müzik eklenmez; ses kanalı sessizdir (Instagram'da müzik sonradan seçilebilsin diye).
"""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter

import config
import render

W, H = 1080, 1920
FPS = 30
KART_Y = 300            # kartın üst kenarı (1350 yükseklik -> 300..1650)
GIRIS = 0.9             # kartın gelme süresi (sn)
GECIS = 0.35            # kartlar arası geçiş (sn)


def ffmpeg_yolu():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # noqa: BLE001
        return "ffmpeg"


def _ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def _zemin(golge=True):
    img = Image.new("RGB", (W, H), render.BG)
    glow = Image.new("RGB", (W, H), render.BG)
    g = ImageDraw.Draw(glow)
    g.ellipse([-400, -700, W + 400, 700], fill=(95, 6, 14))
    g.ellipse([-300, H - 500, W + 300, H + 700], fill=(60, 4, 10))
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(180)), 0.9)
    if golge:
        img.paste((0, 0, 0), (0, 0), _golge())
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 10], fill=render.ACCENT)
    # üst: logo + kullanıcı adı
    if os.path.exists(render.LOGO):
        lg = Image.open(render.LOGO).convert("RGBA").resize((96, 96), Image.LANCZOS)
        img.paste(lg, (64, 150), lg)
    d.text((180, 158), config.HANDLE, font=render.font("InterDisplay-Bold.otf", 40), fill=render.TEXT)
    d.text((180, 208), config.SLOGAN, font=render.font("Inter-Medium.otf", 26), fill=render.MUTED)
    return img


def _kapanis():
    img = _zemin(golge=False)
    d = ImageDraw.Draw(img)
    if os.path.exists(render.LOGO):
        lg = Image.open(render.LOGO).convert("RGBA").resize((300, 300), Image.LANCZOS)
        img.paste(lg, ((W - 300) // 2, 640), lg)
    f1 = render.font("InterDisplay-Black.otf", 64)
    t1 = config.HANDLE
    d.text(((W - d.textlength(t1, font=f1)) / 2, 990), t1, font=f1, fill=render.TEXT)
    f2 = render.font("InterDisplay-Black.otf", 44)
    t2 = "TAKİP ET"
    tw = d.textlength(t2, font=f2)
    d.rounded_rectangle([(W - tw) / 2 - 40, 1100, (W + tw) / 2 + 40, 1180], radius=14, fill=render.ACCENT)
    d.text(((W - tw) / 2, 1112), t2, font=f2, fill=render.TEXT)
    return img


_YUVARLAK = {}


def _yuvarlak(size, r=36):
    if size not in _YUVARLAK:
        m = Image.new("L", size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=r, fill=255)
        _YUVARLAK[size] = m
    return _YUVARLAK[size]


def _golge():
    g = Image.new("L", (W, H), 0)
    ImageDraw.Draw(g).rounded_rectangle([30, KART_Y + 30, W - 30, KART_Y + 1350 + 40], radius=48, fill=170)
    return g.filter(ImageFilter.GaussianBlur(30))


def _kart_kare(zemin, kart, t, sure):
    """t: kartın ekrandaki süresi içinde geçen zaman."""
    img = zemin.copy()
    p = _ease(t / GIRIS)
    # yavaş yakınlaşma (Ken Burns)
    z = 1.0 + 0.035 * max(0.0, (t - GIRIS) / max(sure - GIRIS, 0.1))
    k = kart if z == 1.0 else kart.resize((int(1080 * z), int(1350 * z)), Image.BILINEAR)
    kx = (W - k.width) // 2
    ky = KART_Y - (k.height - 1350) // 2 + int((1 - p) * 120)
    # yukarıdan aşağı açılma maskesi
    acilma = Image.new("L", k.size, 0)
    ImageDraw.Draw(acilma).rectangle([0, 0, k.width, int(k.height * min(1.0, p * 1.15))], fill=int(255 * min(1.0, p * 1.6)))
    from PIL import ImageChops
    mask = ImageChops.multiply(acilma, _yuvarlak(k.size))
    img.paste(k, (kx, ky), mask)
    ImageDraw.Draw(img).rounded_rectangle([kx, ky, kx + k.width - 1, ky + k.height - 1], radius=36,
                                          outline=(*render.LINE,) if p >= 1 else None, width=2)
    return img


def reel_yap(gorseller, cikti, her_kart=4.5, kapanis=1.6):
    """gorseller: 1080x1350 JPEG yolları. cikti: .mp4 yolu."""
    os.makedirs(os.path.dirname(cikti), exist_ok=True)
    zemin = _zemin()
    kartlar = [Image.open(g).convert("RGB").resize((1080, 1350)) for g in gorseller]
    son = _kapanis()

    cmd = [ffmpeg_yolu(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
           "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", cikti]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        onceki = None
        for kart in kartlar:
            n = int(her_kart * FPS)
            for i in range(n):
                t = i / FPS
                kare = _kart_kare(zemin, kart, t, her_kart)
                p.stdin.write(kare.tobytes())
            onceki = kare
        n = int(kapanis * FPS)
        for i in range(n):
            t = i / FPS
            kare = Image.blend(onceki, son, _ease(t / 0.4)) if t < 0.4 else son
            p.stdin.write(kare.tobytes())
    finally:
        p.stdin.close()
        p.wait()
    if p.returncode != 0:
        raise RuntimeError("ffmpeg video üretemedi")
    return cikti
