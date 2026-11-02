"""Diğer liglerin hafta sonu sonuçları + bu haftaki Avrupa maçları (ESPN skor tablosu, tek seferlik)."""
import json, os, requests

def skor(lig, tarihler):
    out = []
    r = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{lig}/scoreboard",
                     params={"dates": tarihler, "limit": 300}, timeout=40)
    for e in r.json().get("events", []):
        c = e["competitions"][0]
        tk = {t["homeAway"]: t for t in c["competitors"]}
        out.append({"lig": lig, "tarih": e["date"], "durum": e["status"]["type"]["name"],
                    "ev": tk["home"]["team"]["displayName"], "dep": tk["away"]["team"]["displayName"],
                    "skor": f"{tk['home'].get('score')}-{tk['away'].get('score')}"})
    return out

aranan = ["Celtic", "Hearts", "AEK", "Slavia", "Jablonec", "Shakhtar", "LASK", "Union", "Hapoel Be", "Omonia",
          "Red Star", "Crvena", "KuPS", "CSKA"]
sonuc, hata = {"hafta_sonu": [], "avrupa": []}, []
for lig in ("sco.1", "gre.1", "cze.1", "aut.1", "bel.1", "isr.1", "cyp.1", "srb.1", "fin.1", "bul.1", "ukr.1"):
    try:
        for m in skor(lig, "20261030-20261102"):
            if any(a.lower() in (m["ev"] + " " + m["dep"]).lower() for a in aranan):
                sonuc["hafta_sonu"].append(m)
    except Exception as e:  # noqa: BLE001
        hata.append(f"{lig}: {e}")
for lig in ("uefa.champions", "uefa.europa", "uefa.europa.conf"):
    try:
        for m in skor(lig, "20261103-20261106"):
            if any(t in (m["ev"] + " " + m["dep"]) for t in ("Galatasaray", "Fenerbah", "Besiktas", "Beşiktaş", "Trabzon")):
                sonuc["avrupa"].append(m)
    except Exception as e:  # noqa: BLE001
        hata.append(f"{lig}: {e}")
ham = {}
for lig in ("sco.1", "gre.1", "uefa.champions"):
    try:
        r = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{lig}/scoreboard",
                         params={"dates": "20261030-20261106"}, timeout=40)
        ham[lig] = [r.status_code, len(r.json().get("events", [])), [e.get("name") for e in r.json().get("events", [])][:6]]
    except Exception as e:  # noqa: BLE001
        ham[lig] = str(e)
sonuc["ham"] = ham
sonuc["hatalar"] = hata
os.makedirs("veri", exist_ok=True)
json.dump(sonuc, open("veri/espn.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"::notice::hafta sonu {len(sonuc['hafta_sonu'])}, avrupa {len(sonuc['avrupa'])}, hata {hata}"[:900])
