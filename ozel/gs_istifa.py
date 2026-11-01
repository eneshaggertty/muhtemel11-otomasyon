"""1 Kasım 2026: Galatasaray'da iki istifa (haber kartı + Reels)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import render, reels  # noqa: E402

kok = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jpg = os.path.join(kok, "posts", "ozel", "2026-11-01-gs-istifa.jpg")
render.haber("SON DAKİKA · GALATASARAY", "GALATASARAY'DA İKİ İSTİFA", [
    ("Metin Öztürk", "İkinci Başkan", "Yönetim kurulu ve bağlı şirketlerdeki görevlerinden istifa etti."),
    ("Abdullah Kavukçu", "Başkanvekili", "Metin Öztürk'ün ardından yönetim kurulu üyeliğinden istifa etti."),
], "1 Kasım 2026", jpg, renk=((169, 3, 41), (253, 185, 19)))
print(reels.reel_yap([jpg], jpg.replace(".jpg", ".mp4"), her_kart=7.0))
