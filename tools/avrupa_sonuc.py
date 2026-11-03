"""ESPN'den bugünkü Avrupa maçlarında Türk takımlarının sonuçları ve golleri (geçici)."""
import json, os, requests
H = {"User-Agent": "Mozilla/5.0"}
out = {"maclar": []}
for lig in ("uefa.champions", "uefa.europa", "uefa.europa.conf"):
    sb = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{lig}/scoreboard",
                      params={"dates": os.environ.get("TARIH", "20261103")}, headers=H, timeout=40).json()
    for e in sb.get("events", []):
        if not any(t in e["name"] for t in ("Galatasaray", "Fenerbah", "Besiktas", "Beşiktaş", "Trabzon")):
            continue
        c = e["competitions"][0]
        tk = {t["homeAway"]: t for t in c["competitors"]}
        olaylar = []
        for d in c.get("details", []):
            olaylar.append({"dk": (d.get("clock") or {}).get("displayValue"), "tip": (d.get("type") or {}).get("text"),
                            "gol": d.get("scoringPlay"), "penalti": d.get("penaltyKick"), "kk": d.get("ownGoal"),
                            "kirmizi": d.get("redCard"), "takim": (d.get("team") or {}).get("id"),
                            "oyuncu": [a.get("displayName") for a in d.get("athletesInvolved", [])]})
        out["maclar"].append({"lig": lig, "ad": e["name"], "durum": e["status"]["type"]["name"],
                              "ev": tk["home"]["team"]["displayName"], "ev_id": tk["home"]["team"]["id"],
                              "dep": tk["away"]["team"]["displayName"], "dep_id": tk["away"]["team"]["id"],
                              "skor": [tk["home"].get("score"), tk["away"].get("score")],
                              "stad": (c.get("venue") or {}).get("fullName"), "olaylar": olaylar})
os.makedirs("veri", exist_ok=True)
json.dump(out, open("veri/avrupa_sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("::notice::" + "; ".join(f"{m['ev']} {m['skor']} {m['dep']} {m['durum']}" for m in out["maclar"])[:900])
