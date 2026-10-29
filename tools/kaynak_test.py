"""API-Football standings ücretsiz planda çalışıyor mu? (geçici test)"""
import os
import requests

key = os.environ["FOOTBALL_API_KEY"].strip()
for lig in (203, 204, 39):
    r = requests.get("https://v3.football.api-sports.io/standings", params={"league": lig, "season": 2026},
                     headers={"x-apisports-key": key}, timeout=30).json()
    if r.get("errors"):
        line = f"standings {lig}: HATA {r['errors']}"
    else:
        st = r["response"][0]["league"]["standings"][0] if r["response"] else []
        line = f"standings {lig}: {len(st)} takım; ilk 3: " + str([(x['rank'], x['team']['name'], x['all']['played'], x['points']) for x in st[:3]])
    print(f"::notice::{line}"[:900])
