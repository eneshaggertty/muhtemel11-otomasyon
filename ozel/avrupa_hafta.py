"""2 Kasım 2026: Avrupa rakiplerinin hafta sonu sonuçları + bu haftaki Avrupa maçları (Reels)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import render, reels  # noqa: E402

kok = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "posts", "ozel")
alt = "Hafta sonu iç lig maçları · 30 Ekim - 2 Kasım"
veri = [
    ("Galatasaray", "Şampiyonlar Ligi", ((169, 3, 41), (253, 185, 19)), [
        ("Barcelona", "Barcelona 6-1 Alavés", "G"), ("PSG", "Le Havre 1-5 PSG", "G"),
        ("Stuttgart", "Leverkusen 2-4 Stuttgart", "G"), ("Sporting", "Casa Pia 0-2 Sporting", "G"),
        ("Lille", "Lille 1-0 Lens", "G"), ("Aston Villa", "Aston Villa 1-1 Fulham", "B"),
        ("Feyenoord", "Feyenoord 1-1 Fortuna Sittard", "B"), ("AEK", "Panathinaikos 2-0 AEK", "M")]),
    ("Fenerbahçe", "Şampiyonlar Ligi", ((22, 35, 87), (255, 237, 0)), [
        ("Atlético Madrid", "Levante 0-2 Atlético", "G"), ("Roma", "Udinese 2-5 Roma", "G"),
        ("Slavia Prag", "Jablonec 0-5 Slavia", "G"), ("LASK", "LASK 2-1 Tirol", "G"),
        ("Aston Villa", "Aston Villa 1-1 Fulham", "B"), ("Liverpool", "Liverpool 0-1 Arsenal", "M"),
        ("Villarreal", "Villarreal 0-1 Espanyol", "M")]),
    ("Beşiktaş", "Avrupa Ligi", ((25, 25, 25), (255, 255, 255)), [
        ("Marsilya", "Marsilya 2-0 Toulouse", "G"), ("Union SG", "Beveren 1-2 Union SG", "G"),
        ("Leverkusen", "Leverkusen 2-4 Stuttgart", "M"), ("Celtic", "Falkirk 2-0 Celtic", "M"),
        ("Crystal Palace", "Tottenham 2-0 C. Palace", "M"), ("Hoffenheim", "Werder 2-0 Hoffenheim", "M")]),
    ("Trabzonspor", "Konferans Ligi", ((122, 31, 61), (79, 163, 222)), [
        ("Freiburg", "Augsburg 1-2 Freiburg", "G"), ("Jablonec", "Jablonec 0-5 Slavia", "M")]),
]
kartlar = []
for takim, turnuva, renk, satirlar in veri:
    p = os.path.join(kok, f"2026-11-02-rakip-{takim.lower().replace('ç','c').replace('ş','s').replace('ğ','g')}.jpg")
    kartlar.append(render.rakipler_karti(takim, turnuva, satirlar, alt, p, renk))
print(reels.reel_yap(kartlar, os.path.join(kok, "2026-11-02-rakipler.mp4"), her_kart=5.0))

prog = os.path.join(kok, "2026-11-02-avrupa-program.jpg")
render.avrupa_programi([
    ("Salı 3 Kasım", "20:45", "Galatasaray", "Stuttgart", "Şampiyonlar Ligi"),
    ("Çarşamba 4 Kasım", "20:45", "Fenerbahçe", "Liverpool", "Şampiyonlar Ligi"),
    ("Perşembe 5 Kasım", "20:45", "Trabzonspor", "Freiburg", "Konferans Ligi"),
    ("Perşembe 5 Kasım", "23:00", "Celtic", "Beşiktaş", "Avrupa Ligi"),
], "3-5 Kasım 2026 · Türkiye saati", prog)
print(reels.reel_yap([prog], os.path.join(kok, "2026-11-02-avrupa-program.mp4"), her_kart=7.0))
