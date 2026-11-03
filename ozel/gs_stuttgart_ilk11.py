"""3 Kasım 2026 GS - Stuttgart ilk 11 (ESPN verisi) -> Reels."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import render, reels  # noqa: E402

veri = json.load(open(sys.argv[1], encoding="utf-8"))["maclar"][0]
KISA = {"Ugurcan Çakir": "Uğurcan", "Abdülkerim Bardakçi": "Abdülkerim", "Davinson Sánchez": "D. Sánchez",
        "Baris Alper Yilmaz": "Barış Alper", "Yunus Akgün": "Yunus Akgün", "Ismail Jakobs": "Jakobs", "Bilal El Khannouss": "El Khannouss"}
X = {3: 0, 11: 0, 6: 1, 8: 1, 10: 1, 5: 2, 4: 2, 9: 1, 7: 3, 2: 4}         # sahada soldan sağa
DERIN = {2: 0, 3: 0, 4: 1, 8: 1, 5: 0, 6: 0, 7: 2, 10: 2, 11: 2, 9: 3}   # orta saha satırlarını ayırmak için

def satirlar(t):
    sayilar = [int(x) for x in t["dizilis"].split("-")]
    ps = [dict(p, yer=int(p["yer"] or 0)) for p in t["ilk11"]]
    kal = [p for p in ps if p["mevki"] == "G"]
    df = [p for p in ps if p["mevki"] == "D"]
    fw = [p for p in ps if p["mevki"] == "F"]
    mf = sorted([p for p in ps if p["mevki"] == "M"], key=lambda p: (DERIN.get(p["yer"], 2), p["yer"]))
    orta, i = [], 0
    for n in sayilar[1:-1]:
        orta.append(mf[i:i + n]); i += n
    rows = [df] + orta + [fw]
    ad = lambda p: KISA.get(p["ad"], p["ad"].split()[-1])  # noqa: E731
    out = [[(int(p["no"]), ad(p)) for p in sorted(r, key=lambda p: X.get(p["yer"], 2))] for r in reversed(rows)]
    return out + [[(int(kal[0]["no"]), ad(kal[0]))]]

kok = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "posts", "ozel")
renk = {"Galatasaray": ((169, 3, 41), (253, 185, 19)), "VfB Stuttgart": ((227, 30, 36), (255, 255, 255))}
gorseller = []
for t in sorted(veri["takimlar"], key=lambda t: t["ev"] != "home"):
    ad_ = "Stuttgart" if "Stuttgart" in t["takim"] else t["takim"]
    p = os.path.join(kok, f"2026-11-03-ilk11-{ad_.lower()}.jpg")
    gorseller.append(render.kadro("İLK 11", "GALATASARAY – STUTTGART", "Şampiyonlar Ligi · 3 Kasım · 20:45",
                                  ad_, renk[t["takim"]], satirlar(t), p, dizilis=t["dizilis"]))
print(reels.reel_yap(gorseller, os.path.join(kok, "2026-11-03-gs-stuttgart-ilk11.mp4"), her_kart=5.0))
