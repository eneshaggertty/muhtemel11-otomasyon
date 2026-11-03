"""3 Kasım 2026 GS 2-0 Stuttgart maç sonucu -> Reels."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import render, reels  # noqa: E402
kok = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "posts", "ozel")
jpg = os.path.join(kok, "2026-11-03-gs-stuttgart-sonuc.jpg")
render.mac_sonucu({
    "lig": "UEFA Şampiyonlar Ligi", "alt": "3 Kasım 2026 · RAMS Park",
    "ev": "Galatasaray", "dep": "Stuttgart", "ev_renk": ((169, 3, 41), (253, 185, 19)),
    "dep_renk": ((227, 30, 36), (255, 255, 255)), "skor": (2, 0),
    "goller": [("12", "Batrakov", "ev", ""), ("15", "Batrakov", "ev", "")],
    "bilgi": ["Sarı kart: Galatasaray 3 · Stuttgart 5"], "ek": "",
}, jpg)
print(reels.reel_yap([jpg], jpg.replace(".jpg", ".mp4"), her_kart=7.0))
