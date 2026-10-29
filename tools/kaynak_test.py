"""Ücretsiz puan durumu kaynaklarını dener (geçici test aracı)."""
import json
import requests

def get(url):
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "muhtemel11-bot"})
        return r.status_code, r.text[:200000]
    except Exception as e:  # noqa: BLE001
        return "ERR", str(e)

out = []
# TheSportsDB: Türkiye ligleri
code, t = get("https://www.thesportsdb.com/api/v1/json/123/search_all_leagues.php?c=Turkey&s=Soccer")
try:
    lg = [(x["idLeague"], x["strLeague"], x.get("strCurrentSeason")) for x in json.loads(t)["countries"] or []]
except Exception as e:  # noqa: BLE001
    lg = f"{code} {t[:300]}"
out.append(f"TSDB ligler: {lg}")
for lid in ("4339",):
    for s in ("2026-2027",):
        code, t = get(f"https://www.thesportsdb.com/api/v1/json/123/lookuptable.php?l={lid}&s={s}")
        try:
            rows = json.loads(t).get("table") or []
            out.append(f"TSDB tablo {lid} {s}: {len(rows)} satır; ilk: " +
                       str([(r["intRank"], r["strTeam"], r["intPlayed"], r["intPoints"], r.get("dateUpdated")) for r in rows[:6]]))
        except Exception as e:  # noqa: BLE001
            out.append(f"TSDB tablo {lid} {s}: {code} {t[:300]}")
for line in out:
    print(line)
    print(f"::notice::{line}"[:900])
