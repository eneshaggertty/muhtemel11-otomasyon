"""ESPN'den bugünkü Avrupa maçında Türk takımlarının ilk 11'leri (geçici)."""
import json, os, requests
H = {"User-Agent": "Mozilla/5.0"}
out = {"maclar": []}
for lig in ("uefa.champions", "uefa.europa", "uefa.europa.conf"):
    sb = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{lig}/scoreboard",
                      params={"dates": os.environ.get("TARIH", "20261103")}, headers=H, timeout=40).json()
    for e in sb.get("events", []):
        if not any(t in e["name"] for t in ("Galatasaray", "Fenerbah", "Besiktas", "Beşiktaş", "Trabzon")):
            continue
        s = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{lig}/summary",
                         params={"event": e["id"]}, headers=H, timeout=40).json()
        mac = {"lig": lig, "ad": e["name"], "tarih": e["date"], "takimlar": []}
        for r in s.get("rosters", []):
            mac["takimlar"].append({
                "takim": r["team"]["displayName"], "ev": r.get("homeAway"), "dizilis": r.get("formation"),
                "ilk11": [{"no": p.get("jersey"), "ad": p["athlete"]["displayName"],
                           "mevki": (p.get("position") or {}).get("abbreviation"), "yer": p.get("formationPlace")}
                          for p in r.get("roster", []) if p.get("starter")]})
        out["maclar"].append(mac)
os.makedirs("veri", exist_ok=True)
json.dump(out, open("veri/avrupa_kadro.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("::notice::" + "; ".join(f"{m['ad']}: " + ", ".join(f"{t['takim']} {len(t['ilk11'])} {t['dizilis']}" for t in m["takimlar"]) for m in out["maclar"])[:900])
