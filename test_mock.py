"""Sahte API verisiyle bir maç gününü baştan sona simüle eder (paylaşım yapmaz).

Çalıştır:  DRY_RUN=1 python test_mock.py
"""
import os
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo

os.environ["DRY_RUN"] = "1"
import main  # noqa: E402

TZ = ZoneInfo("Europe/Istanbul")
SL, L1, TR = 203, 204, 777


def fx(fid, lig, rnd, ev, dep, saat, durum="NS", g=(None, None), ev_id=None, dep_id=None, gun=26):
    return {
        "fixture": {"id": fid, "date": f"2026-10-{gun}T{saat}:00+03:00", "status": {"short": durum},
                    "venue": {"name": "RAMS Park" if ev == "Galatasaray" else "Stadyum"},
                    "referee": "Atilla Karaoğlan, Turkey"},
        "league": {"id": lig, "name": "Super Lig", "round": rnd},
        "teams": {"home": {"id": ev_id or fid * 10, "name": ev}, "away": {"id": dep_id or fid * 10 + 1, "name": dep}},
        "goals": {"home": g[0], "away": g[1]}, "score": {"penalty": {}},
    }


def p(name, no, grid):
    return {"player": {"name": name, "number": no, "grid": grid, "pos": "M"}}


GS_XI = [p("U. Çakır", 1, "1:1"), p("R. Sallai", 7, "2:4"), p("D. Sánchez", 6, "2:3"),
         p("A. Bardakcı", 42, "2:2"), p("I. Jakobs", 4, "2:1"), p("M. Lemina", 99, "3:2"),
         p("L. Torreira", 34, "3:1"), p("Y. Akgün", 11, "4:3"), p("A. Batrakov", 10, "4:2"),
         p("B. A. Yılmaz", 53, "4:1"), p("V. Osimhen", 45, "5:1")]
FB_XI = [p("Ederson", 31, "1:1"), p("N. Semedo", 2, "2:4"), p("M. Škriniar", 37, "2:3"),
         p("J. Brown", 4, "2:2"), p("L. Mercan", 3, "2:1"), p("N. Kanté", 17, "3:2"),
         p("M. Guendouzi", 6, "3:1"), p("O. Aydın", 70, "4:3"), p("İ. C. Kahveci", 10, "4:2"),
         p("M. Greenwood", 18, "4:1"), p("R. Lukaku", 9, "5:1")]


class FakeApi:
    def __init__(self, durum):
        self.durum = durum  # "once" | "bitti"
        self.calls = 0

    def _sl(self):
        if self.durum == "once":
            return fx(1, SL, "Regular Season - 9", "Galatasaray", "Fenerbahce", "21:30")
        return fx(1, SL, "Regular Season - 9", "Galatasaray", "Fenerbahce", "21:30", "FT", (2, 1))

    def _l1(self):
        takimlar = [("Bodrum FK", "Sakaryaspor"), ("Bandırmaspor", "Keçiörengücü"), ("Pendikspor", "Iğdır FK"),
                    ("Ankaragücü", "Esenler Erokspor"), ("Boluspor", "Ümraniyespor"), ("Manisa FK", "Sivasspor"),
                    ("Hatayspor", "Adana Demirspor"), ("Serikspor", "Sarıyer"), ("Erzurumspor", "Vanspor FK")]
        out = []
        for i, (e, d) in enumerate(takimlar):
            if self.durum == "once":
                out.append(fx(100 + i, L1, "Regular Season - 10", e, d, ["13:30", "16:00", "19:00"][i % 3]))
            else:
                out.append(fx(100 + i, L1, "Regular Season - 10", e, d, "16:00", "FT", (i % 3, (i + 1) % 2)))
        return out

    def fixtures_by_date(self, date, tz):
        self.calls += 1
        if date == "2026-10-27":  # yarın: milli maç
            return [fx(900, 1, "Qualification - 5", "Turkey", "Spain", "21:45", ev_id=TR, gun=27)]
        return [self._sl()] + self._l1() + self._pl()

    def _pl(self):
        takimlar = [("Arsenal", "Chelsea"), ("Liverpool", "Manchester City"), ("Tottenham", "Newcastle")]
        if self.durum == "once":
            return [fx(200 + i, 39, "Regular Season - 10", e, d, "18:00") for i, (e, d) in enumerate(takimlar)]
        return [fx(200 + i, 39, "Regular Season - 10", e, d, "18:00", "FT", (i + 1, i % 2)) for i, (e, d) in enumerate(takimlar)]

    def fixtures_team_season(self, team, season, tz):
        self.calls += 1
        return [fx(899, 1, "Qualification - 4", "Georgia", "Turkey", "19:00", "FT", (1, 2), dep_id=TR, gun=14)]

    def lineups(self, fid):
        self.calls += 1
        if fid == 1:
            return [{"team": {"id": 10, "name": "Galatasaray", "colors": {"player": {"primary": "a90329", "border": "fdb913"}}},
                     "formation": "4-2-3-1", "startXI": GS_XI, "coach": {"name": "Okan Buruk"}},
                    {"team": {"id": 11, "name": "Fenerbahce", "colors": {"player": {"primary": "162357", "border": "ffed00"}}},
                     "formation": "4-2-3-1", "startXI": FB_XI, "coach": {"name": "Dirk Kuyt"}}]
        # Türkiye'nin son maçı
        return [{"team": {"id": TR, "name": "Turkey"}, "formation": "4-2-3-1", "coach": {"name": "Vincenzo Montella"},
                 "startXI": [p("U. Çakır", 1, "1:1"), p("Z. Çelik", 2, "2:4"), p("M. Demiral", 3, "2:3"),
                             p("A. Bardakcı", 14, "2:2"), p("F. Kadıoğlu", 20, "2:1"), p("H. Çalhanoğlu", 10, "3:2"),
                             p("İ. Yüksek", 16, "3:1"), p("K. Aktürkoğlu", 7, "4:3"), p("A. Güler", 8, "4:2"),
                             p("K. Yıldız", 19, "4:1"), p("B. A. Yılmaz", 21, "5:1")]}]

    def events(self, fid):
        self.calls += 1
        return [{"time": {"elapsed": 29}, "team": {"id": 10}, "player": {"name": "V. Osimhen"}, "type": "Goal", "detail": "Normal Goal"},
                {"time": {"elapsed": 44}, "team": {"id": 10}, "player": {"name": "V. Osimhen"}, "type": "Goal", "detail": "Normal Goal"},
                {"time": {"elapsed": 62}, "team": {"id": 11}, "player": {"name": "İ. C. Kahveci"}, "type": "Goal", "detail": "Normal Goal"}]

    def round_fixtures(self, league, season, rnd, tz):
        self.calls += 1
        return {SL: [self._sl()], L1: self._l1(), 39: self._pl()}[league]

    def standings(self, league, season):
        self.calls += 1
        rows = [("Galatasaray", 7, 1, 1, 7), ("Amed SFK", 6, 2, 1, 10), ("Trabzonspor", 6, 1, 2, 14),
                ("Besiktas", 6, 0, 3, 8), ("Fenerbahce", 5, 1, 3, 15), ("Kasimpasa", 4, 4, 1, 4),
                ("Kocaelispor", 5, 0, 4, 2), ("Erzurumspor FK", 4, 2, 3, -4), ("Corum FK", 4, 1, 4, 3),
                ("Goztepe", 3, 3, 3, 3), ("Alanyaspor", 3, 3, 3, -2), ("Istanbul Basaksehir", 3, 2, 4, -2),
                ("Rizespor", 3, 1, 5, -4), ("Konyaspor", 2, 2, 5, -3), ("Gaziantep FK", 2, 2, 5, -6),
                ("Genclerbirligi", 2, 2, 5, -11), ("Samsunspor", 1, 1, 7, -13), ("Eyupspor", 1, 0, 8, -21)]
        if league == L1:
            rows = rows + [("Bodrum FK", 1, 0, 8, -15), ("Sakaryaspor", 0, 2, 7, -20)]
        if league == 39:
            rows = [("Arsenal", 8, 1, 1, 15), ("Manchester City", 7, 2, 1, 12), ("Liverpool", 7, 1, 2, 10)] + rows[3:]
        return [{"team": {"name": n}, "all": {"played": w + d + l, "win": w, "draw": d, "lose": l},
                 "goalsDiff": gd, "points": 3 * w + d} for n, w, d, l, gd in rows]

    def fixtures_team(self, team, tz, next_=None, last=None):
        self.calls += 1
        if next_:
            return [fx(900, 1, "Qualification - 5", "Turkey", "Spain", "21:45", ev_id=TR, gun=27)]
        return [fx(899, 1, "Qualification - 4", "Georgia", "Turkey", "19:00", "FT", (1, 2), dep_id=TR, gun=14)]


if __name__ == "__main__":
    for d in (main.POSTS,):
        shutil.rmtree(os.path.join(main.ROOT, d), ignore_errors=True)
    if os.path.exists(main.STATE_PATH):
        os.remove(main.STATE_PATH)
    adimlar = [
        ("12:30 program", "once", datetime(2026, 10, 26, 12, 30, tzinfo=TZ)),
        ("20:45 ilk 11", "once", datetime(2026, 10, 26, 20, 45, tzinfo=TZ)),
        ("23:30 sonuçlar + puan + muhtemel 11", "bitti", datetime(2026, 10, 26, 23, 30, tzinfo=TZ)),
        ("23:45 tekrar (çift paylaşım olmamalı)", "bitti", datetime(2026, 10, 26, 23, 45, tzinfo=TZ)),
    ]
    for ad_, durum, t in adimlar:
        print(f"\n===== {ad_} =====")
        main.state_cache_reset = None
        errs = main.run(FakeApi(durum), now=t)
        assert not errs, errs
    print("\nÜretilen görseller:")
    for root, _, files in os.walk(os.path.join(main.ROOT, main.POSTS)):
        for f in sorted(files):
            print(" ", os.path.join(root, f))
    os.remove(main.STATE_PATH)
