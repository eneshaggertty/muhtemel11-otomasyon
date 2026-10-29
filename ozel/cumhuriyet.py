"""29 Ekim Cumhuriyet Bayramı kutlama görseli (1080x1350)."""
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import render  # noqa: E402

S = 2  # süper örnekleme
W, H = 1080 * S, 1350 * S
RED = (227, 10, 23)
WHITE = (255, 255, 255)

img = Image.new("RGB", (W, H), (150, 4, 14))
glow = Image.new("RGB", (W, H), (150, 4, 14))
ImageDraw.Draw(glow).ellipse([-W * 0.3, -H * 0.25, W * 1.3, H * 0.75], fill=RED)
img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(220 * S)), 1.0)

# Ay-yıldız (TS 2342 oranları, G = bayrak yüksekliği)
G = 560 * S
ox, oy = W / 2 - 0.798 * G, 380 * S   # sembolü yatayda ortala; orta hat y=380
d = ImageDraw.Draw(img)
def circle(cx, r, fill):
    d.ellipse([ox + cx - r, oy - r, ox + cx + r, oy + r], fill=fill)
circle(0.5 * G, 0.25 * G, WHITE)                 # dış daire
# iç daireyi zemin rengiyle değil, alttaki gradyanla kesmek için maske kullan
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).ellipse([ox + 0.5625 * G - 0.2 * G, oy - 0.2 * G, ox + 0.5625 * G + 0.2 * G, oy + 0.2 * G], fill=255)
bg = Image.blend(Image.new("RGB", (W, H), (150, 4, 14)), glow.filter(ImageFilter.GaussianBlur(220 * S)), 1.0)
img.paste(bg, (0, 0), mask)
d = ImageDraw.Draw(img)
# yıldız: çevrel çember çapı 0.25G, iç çember kenarından uzaklık 1/3 G, bir ucu sola bakar
scx = ox + 0.5625 * G + 0.2 * G + G / 3 + 0.125 * G
R, r = 0.125 * G, 0.125 * G * 0.382
pts = []
for i in range(10):
    a = math.pi + i * math.pi / 5  # ilk uç sola
    rr = R if i % 2 == 0 else r
    pts.append((scx + rr * math.cos(a), oy + rr * math.sin(a)))
d.polygon(pts, fill=WHITE)

img = img.resize((1080, 1350), Image.LANCZOS)
d = ImageDraw.Draw(img)
f = render.font
def center(y, t, fnt, fill=WHITE):
    d.text((540 - d.textlength(t, font=fnt) / 2, y), t, font=fnt, fill=fill)

center(70, "29 EKİM 1923", f("Inter-SemiBold.otf", 34), (255, 220, 220))
center(600, "CUMHURİYET", f("InterDisplay-Black.otf", 118))
center(725, "BAYRAMIMIZ", f("InterDisplay-Black.otf", 118))
center(855, "KUTLU OLSUN", f("InterDisplay-ExtraBold.otf", 64), (255, 225, 225))
d.rounded_rectangle([390, 955, 690, 1015], radius=30, outline=WHITE, width=3)
center(963, "103. YIL", f("InterDisplay-Black.otf", 38))
center(1075, "“Cumhuriyet fazilettir.” — Mustafa Kemal Atatürk", f("Inter-Medium.otf", 28), (255, 215, 215))
# alt imza
d.line([64, 1230, 1016, 1230], fill=(255, 140, 140), width=2)
lg = Image.open(render.LOGO).convert("RGBA").resize((70, 70), Image.LANCZOS)
img.paste(lg, (64, 1250), lg)
d.text((150, 1258), "@muhtemel11onbir", font=f("InterDisplay-Bold.otf", 32), fill=WHITE)
d.text((150, 1296), "Futbolda son dakika burada", font=f("Inter-Medium.otf", 20), fill=(255, 210, 210))

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "posts", "ozel", "2026-10-29-cumhuriyet.jpg")
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out, "JPEG", quality=93)
print(out)
