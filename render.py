"""@muhtemel11onbir kart üretici.

Tüm kartlar 1080x1350 (Instagram dikey post), JPEG olarak kaydedilir
(Instagram API yalnızca JPEG kabul ediyor).
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import config

W, H = 1080, 1350
ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(ROOT, "fonts")
LOGO = os.path.join(ROOT, "assets", "logo.png")

BG = (8, 8, 10)
PANEL = (22, 16, 18)
LINE = (90, 20, 26)
TEXT = (240, 244, 241)
MUTED = (165, 160, 162)
ACCENT = (230, 28, 40)

_font_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    return _font_cache[key]


def tr_upper(t):
    return (t or "").replace("i", "İ").replace("ı", "I").upper()


def hex_rgb(h, default):
    try:
        h = (h or "").lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) if len(h) == 6 else default
    except ValueError:
        return default


def center(d, cx, y, text, f, fill):
    d.text((cx - d.textlength(text, font=f) / 2, y), text, font=f, fill=fill)


def fit(d, text, name, size, max_w, min_size=18):
    """Metin max_w genişliğe sığana kadar yazı boyutunu küçültür."""
    while size > min_size and d.textlength(text, font=font(name, size)) > max_w:
        size -= 2
    return font(name, size)


def base(kicker, title, subtitle=None):
    img = Image.new("RGB", (W, H), BG)
    glow = Image.new("RGB", (W, H), BG)
    ImageDraw.Draw(glow).ellipse([-300, -700, W + 300, 420], fill=(95, 6, 14))
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(160)), 0.9)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 10], fill=ACCENT)
    d.rectangle([64, 74, 72, 104], fill=ACCENT)
    d.text((86, 70), kicker, font=fit(d, kicker, "Inter-SemiBold.otf", 30, W - 150), fill=TEXT)
    d.text((60, 108), title, font=fit(d, title, "InterDisplay-Black.otf", 92, W - 128), fill=TEXT)
    if subtitle:
        d.text((64, 216), subtitle, font=fit(d, subtitle, "Inter-Medium.otf", 32, W - 128), fill=MUTED)
    d.line([64, H - 120, W - 64, H - 120], fill=LINE, width=2)
    x0 = 64
    if os.path.exists(LOGO):
        lg = Image.open(LOGO).convert("RGBA").resize((84, 84), Image.LANCZOS)
        img.paste(lg, (64, H - 104), lg)
        x0 = 164
    d.text((x0, H - 96), config.HANDLE, font=font("InterDisplay-Bold.otf", 34), fill=TEXT)
    d.text((x0, H - 54), config.SLOGAN, font=font("Inter-Medium.otf", 22), fill=MUTED)
    tag = "TAKİP ET"
    tf = font("InterDisplay-Black.otf", 26)
    tw = d.textlength(tag, font=tf)
    d.rounded_rectangle([W - 64 - tw - 40, H - 92, W - 64, H - 42], radius=10, fill=ACCENT)
    d.text((W - 64 - tw - 20, H - 83), tag, font=tf, fill=TEXT)
    return img, d


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.convert("RGB").save(path, "JPEG", quality=92)
    return path


# ---------------------------------------------------------------- PROGRAM
def program(lig_adi, tarih_str, maclar, path):
    """maclar: [(saat, ev, dep), ...]"""
    img, d = base(tr_upper(lig_adi), "GÜNÜN MAÇLARI", tarih_str)
    top, bottom = 290, H - 150
    n = max(len(maclar), 1)
    rh = min(110, (bottom - top) / n)
    tf_size = 40 if rh >= 90 else 32
    for i, (saat, ev, dep) in enumerate(maclar):
        y = top + i * rh
        d.rounded_rectangle([64, y, W - 64, y + rh - 14], radius=16, fill=PANEL,
                            outline=LINE, width=2)
        cy = y + (rh - 14) / 2
        sf = font("InterDisplay-Black.otf", tf_size)
        d.rounded_rectangle([84, cy - 26, 214, cy + 26], radius=10, fill=ACCENT)
        center(d, 149, cy - tf_size * 0.62, saat, sf, TEXT)
        tf = font("Inter-SemiBold.otf", tf_size - 4)
        mid = 640
        evf = fit(d, ev, "Inter-SemiBold.otf", tf_size - 4, mid - 270)
        d.text((mid - 30 - d.textlength(ev, font=evf), cy - (tf_size - 4) * 0.62), ev, font=evf, fill=TEXT)
        center(d, mid, cy - (tf_size - 4) * 0.62, "–", tf, MUTED)
        depf = fit(d, dep, "Inter-SemiBold.otf", tf_size - 4, W - 84 - mid - 30)
        d.text((mid + 30, cy - (tf_size - 4) * 0.62), dep, font=depf, fill=TEXT)
    return save(img, path)


# ---------------------------------------------------------------- MAÇ SONUCU
def mac_sonucu(m, path):
    """m: lig, alt, ev, dep, ev_renk, dep_renk, skor(tuple), goller[(dk, ad, 'ev'|'dep', not)], bilgi[str]"""
    img, d = base(tr_upper(m["lig"]), "MAÇ SONUCU", m.get("alt"))
    d.rounded_rectangle([64, 290, W - 64, 700], radius=24, fill=PANEL, outline=ACCENT, width=3)
    lx, rx = 290, W - 290
    for cx, renk in ((lx, m.get("ev_renk")), (rx, m.get("dep_renk"))):
        c1, c2 = renk or ((90, 90, 90), (170, 170, 170))
        d.rectangle([cx - 70, 340, cx, 354], fill=c1)
        d.rectangle([cx, 340, cx + 70, 354], fill=c2)
    for cx, ad in ((lx, m["ev"]), (rx, m["dep"])):
        t = tr_upper(ad)
        center(d, cx, 380, t, fit(d, t, "InterDisplay-ExtraBold.otf", 46, 400), TEXT)
    sf = font("InterDisplay-Black.otf", 190)
    e, a = m["skor"]
    center(d, lx, 450, str(e), sf, ACCENT if e > a else TEXT)
    center(d, rx, 450, str(a), sf, ACCENT if a > e else TEXT)
    center(d, W / 2, 520, "–", font("InterDisplay-Bold.otf", 110), MUTED)
    if m.get("ek"):  # uzatma / penaltı bilgisi
        center(d, W / 2, 640, m["ek"], font("Inter-SemiBold.otf", 26), MUTED)

    y = 740
    if m["goller"]:
        d.text((64, y), "GOLLER", font=font("Inter-SemiBold.otf", 28), fill=ACCENT)
        y += 52
    goller = m["goller"]
    gsize = 40 if len(goller) <= 4 else (34 if len(goller) <= 6 else 28)
    step = gsize + 22
    for dk, ad, taraf, notu in goller:
        x = 64 if taraf == "ev" else W / 2 + 20
        mf = font("InterDisplay-Bold.otf", gsize)
        d.text((x, y), f"{dk}'", font=mf, fill=ACCENT)
        label = ad + (f" ({notu})" if notu else "")
        d.text((x + gsize * 2.3, y), label,
               font=fit(d, label, "Inter-SemiBold.otf", gsize, W / 2 - 84 - gsize * 2.3), fill=TEXT)
        y += step
    y = max(y + 24, 1040)
    if m.get("bilgi"):
        d.line([64, y, W - 64, y], fill=LINE, width=2)
        y += 26
        for satir in m["bilgi"][: max(1, int((H - 140 - y) // 44))]:
            d.text((64, y), satir, font=fit(d, satir, "Inter-Medium.otf", 30, W - 128), fill=MUTED)
            y += 44
    return save(img, path)


# ---------------------------------------------------------------- İLK 11 / MUHTEMEL 11
def _pitch(d, box):
    px0, py0, px1, py1 = box
    d.rounded_rectangle(box, radius=36, fill=(20, 52, 34))
    for i in range(0, 8, 2):
        yy = py0 + i * (py1 - py0) / 8
        d.rectangle([px0, yy, px1, yy + (py1 - py0) / 8], fill=(23, 58, 38))
    lc = (70, 110, 85)
    d.rounded_rectangle(box, radius=36, outline=lc, width=3)
    my = (py0 + py1) / 2
    d.line([px0, my, px1, my], fill=lc, width=3)
    cx = (px0 + px1) / 2
    d.ellipse([cx - 90, my - 90, cx + 90, my + 90], outline=lc, width=3)
    d.rectangle([cx - 160, py1 - 140, cx + 160, py1], outline=lc, width=3)
    d.rectangle([cx - 160, py0, cx + 160, py0 + 140], outline=lc, width=3)


def kadro(baslik, kicker, alt, takim_adi, renk, satirlar, path, dipnot=None, dizilis=None, hoca=None):
    """satirlar: forvetten kaleciye, her satır [(numara, ad), ...]"""
    img, d = base(kicker, baslik, alt)
    box = (64, 280, W - 64, 1180 if not dipnot else 1150)
    _pitch(d, box)
    px0, py0, px1, py1 = box
    c1, c2 = renk or ((200, 200, 200), (60, 60, 60))
    nf = font("Inter-SemiBold.otf", 26)
    numf = font("InterDisplay-Black.otf", 26)
    usable = (py1 - 80) - (py0 + 100)
    for r, satir in enumerate(satirlar):
        y = py0 + 100 + (usable * r / (len(satirlar) - 1) if len(satirlar) > 1 else usable / 2)
        n = len(satir)
        for i, (no, ad) in enumerate(satir):
            x = px0 + (px1 - px0) * (i + 1) / (n + 1)
            d.ellipse([x - 34, y - 34, x + 34, y + 34], fill=c1, outline=c2, width=6)
            if no is not None:
                center(d, x, y - 17, str(no), numf, c2 if sum(c2) > 200 else TEXT)
            maxw = (px1 - px0) / (n + 0.4) - 16
            f = fit(d, ad, "Inter-SemiBold.otf", 26, maxw, 16)
            tw = d.textlength(ad, font=f)
            d.rounded_rectangle([x - tw / 2 - 12, y + 42, x + tw / 2 + 12, y + 82], radius=10, fill=(10, 14, 12))
            d.text((x - tw / 2, y + 47), ad, font=f, fill=TEXT)
            d.rectangle([x - tw / 2 - 12, y + 78, x + tw / 2 + 12, y + 82], fill=ACCENT)
    t = tr_upper(takim_adi)
    d.text((px0 + 28, py0 + 22), t, font=fit(d, t, "InterDisplay-ExtraBold.otf", 34, 300), fill=TEXT)
    if dizilis:
        df = font("InterDisplay-Black.otf", 30)
        d.text((px1 - 28 - d.textlength(dizilis, font=df), py0 + 22), dizilis, font=df, fill=ACCENT)
    if hoca:
        hf = font("Inter-Medium.otf", 24)
        d.text((px0 + 28, py1 - 44), f"TD: {hoca}", font=hf, fill=MUTED)
    if dipnot:
        d.text((64, py1 + 14), dipnot, font=fit(d, dipnot, "Inter-Medium.otf", 24, W - 128), fill=MUTED)
    return save(img, path)


# ---------------------------------------------------------------- PUAN DURUMU
def puan_durumu(lig_adi, alt, tablo, path):
    """tablo: [(takim, O, G, B, M, AV, P), ...] sıralı"""
    img, d = base(tr_upper(lig_adi), "PUAN DURUMU", alt)
    top = 270
    rh = (1215 - top - 50) / max(len(tablo), 1)
    fs = 30 if rh >= 46 else 24
    hf = font("Inter-SemiBold.otf", 24)
    cols = {"O": 620, "G": 690, "B": 760, "M": 830, "AV": 905, "P": 980}
    d.text((140, top), "TAKIM", font=hf, fill=MUTED)
    for k, x in cols.items():
        center(d, x, top, k, hf, MUTED)
    rf = font("Inter-SemiBold.otf", fs)
    pf = font("InterDisplay-Black.otf", fs + 2)
    for i, (takim, o, g, b, m, av, pu) in enumerate(tablo):
        y = top + 44 + i * rh
        if i % 2 == 0:
            d.rectangle([64, y - 6, W - 64, y + rh - 6], fill=PANEL)
        if i == 0:
            d.rectangle([64, y - 6, 72, y + rh - 6], fill=ACCENT)
        ty = y + (rh - 12) / 2 - fs * 0.6
        center(d, 106, ty, str(i + 1), rf, MUTED)
        d.text((140, ty), takim, font=fit(d, takim, "Inter-SemiBold.otf", fs, 440), fill=TEXT)
        for (k, x), v in zip(cols.items(), [o, g, b, m, av, pu]):
            txt = f"+{v}" if (k == "AV" and v > 0) else str(v)
            center(d, x, ty, txt, pf if k == "P" else rf, ACCENT if k == "P" else TEXT)
    return save(img, path)


# ---------------------------------------------------------------- GÜNÜN SONUÇLARI (toplu)
def gunun_sonuclari(lig_adi, tarih_str, sonuclar, path):
    """sonuclar: [(ev, ev_gol, dep_gol, dep), ...]"""
    img, d = base(tr_upper(lig_adi), "GÜNÜN SONUÇLARI", tarih_str)
    top, bottom = 290, H - 150
    rh = min(110, (bottom - top) / max(len(sonuclar), 1))
    fs = 38 if rh >= 90 else 30
    for i, (ev, eg, ag, dep) in enumerate(sonuclar):
        y = top + i * rh
        d.rounded_rectangle([64, y, W - 64, y + rh - 14], radius=16, fill=PANEL, outline=LINE, width=2)
        cy = y + (rh - 14) / 2 - fs * 0.62
        mid = W / 2
        evf = fit(d, ev, "Inter-SemiBold.otf", fs, mid - 84 - 110)
        d.text((mid - 100 - d.textlength(ev, font=evf), cy), ev, font=evf, fill=TEXT)
        d.rounded_rectangle([mid - 80, cy - 8, mid + 80, cy + fs * 1.3], radius=10, fill=ACCENT)
        center(d, mid, cy - 2, f"{eg} - {ag}", font("InterDisplay-Black.otf", fs), TEXT)
        depf = fit(d, dep, "Inter-SemiBold.otf", fs, W - 84 - mid - 100)
        d.text((mid + 100, cy), dep, font=depf, fill=TEXT)
    return save(img, path)
