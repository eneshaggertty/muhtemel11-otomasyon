"""API-Football hesap durumu (geçici)."""
import json, os, requests
key = os.environ["FOOTBALL_API_KEY"].strip()
r = requests.get("https://v3.football.api-sports.io/status", headers={"x-apisports-key": key}, timeout=30)
j = r.json()
resp = j.get("response") or {}
ozet = {"http": r.status_code, "hatalar": j.get("errors"),
        "abonelik": resp.get("subscription") if isinstance(resp, dict) else None,
        "istek": resp.get("requests") if isinstance(resp, dict) else None,
        "hesap_aktif_mi": (resp.get("subscription") or {}).get("active") if isinstance(resp, dict) else None}
f = requests.get("https://v3.football.api-sports.io/fixtures", params={"date": "2026-11-02", "timezone": "Europe/Istanbul"},
                 headers={"x-apisports-key": key}, timeout=30).json()
ozet["fixtures_hata"] = f.get("errors")
ozet["fixtures_sayi"] = f.get("results")
os.makedirs("veri", exist_ok=True)
json.dump(ozet, open("veri/api_durum.json", "w"), ensure_ascii=False, indent=1)
print(f"::notice::{json.dumps(ozet, ensure_ascii=False)}"[:900])
