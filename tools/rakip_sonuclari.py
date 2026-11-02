"""Avrupa rakiplerinin hafta sonu iç lig sonuçlarını toplar -> veri/rakipler.json (geçici araç)."""
import json, os, requests

TAKIMLAR = ["Barcelona", "Stuttgart", "Aston Villa", "Feyenoord", "Sporting", "Lille", "AEK", "Paris",
            "Liverpool", "Atletico", "Atlético", "Roma", "Villarreal", "Shakhtar", "Slavia", "LASK",
            "Marseille", "Union", "Crystal Palace", "Hapoel Beer", "Leverkusen", "Celtic", "Omonia", "Hoffenheim",
            "Freiburg", "Hearts", "Heart of Midlothian", "Jablonec", "Crvena", "Red Star", "KuPS", "CSKA Sofia", "CSKA 1948"]
ARALIK = ("2026-10-30", "2026-11-02")
out = {"football_data": [], "api_football": [], "hatalar": []}

key = os.environ.get("FOOTBALL_DATA_KEY", "").strip()
for kod in ("PL", "PD", "SA", "BL1", "FL1", "DED", "PPL"):
    try:
        r = requests.get(f"https://api.football-data.org/v4/competitions/{kod}/matches",
                         params={"dateFrom": ARALIK[0], "dateTo": ARALIK[1]}, headers={"X-Auth-Token": key}, timeout=30)
        for m in r.json().get("matches", []):
            ev, dep = m["homeTeam"].get("name"), m["awayTeam"].get("name")
            if any(t.lower() in (ev + " " + dep).lower() for t in TAKIMLAR):
                out["football_data"].append({"lig": kod, "tarih": m["utcDate"], "durum": m["status"], "hafta": m.get("matchday"),
                                             "ev": ev, "dep": dep, "skor": m["score"]["fullTime"]})
    except Exception as e:  # noqa: BLE001
        out["hatalar"].append(f"fd {kod}: {e}")

akey = os.environ.get("FOOTBALL_API_KEY", "").strip()
for tarih in ("2026-11-01", "2026-11-02"):
    try:
        r = requests.get("https://v3.football.api-sports.io/fixtures", params={"date": tarih, "timezone": "Europe/Istanbul"},
                         headers={"x-apisports-key": akey}, timeout=60).json()
        if r.get("errors"):
            out["hatalar"].append(f"af {tarih}: {r['errors']}")
        for f in r.get("response", []):
            ev, dep = f["teams"]["home"]["name"], f["teams"]["away"]["name"]
            if f["league"]["type"] == "League" and any(t.lower() in (ev + " " + dep).lower() for t in TAKIMLAR):
                out["api_football"].append({"lig": f"{f['league']['country']} - {f['league']['name']}", "tarih": f["fixture"]["date"],
                                            "durum": f["fixture"]["status"]["short"], "hafta": f["league"]["round"],
                                            "ev": ev, "dep": dep, "skor": f["goals"]})
    except Exception as e:  # noqa: BLE001
        out["hatalar"].append(f"af {tarih}: {e}")

os.makedirs("veri", exist_ok=True)
json.dump(out, open("veri/rakipler.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"::notice::fd {len(out['football_data'])} maç, af {len(out['api_football'])} maç, hata {out['hatalar']}"[:900])
