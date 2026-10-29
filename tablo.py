"""Ücretsiz puan durumu.

- Süper Lig / 1. Lig: tablo repo'daki tablolar/<lig>.json dosyasında tutulur ve her biten maçla
  güncellenir. Paylaşmadan önce TheSportsDB'nin ücretsiz ilk 5'iyle karşılaştırılır.
- Premier Lig / La Liga / Serie A: football-data.org ücretsiz API'sinden alınır.
"""
import difflib
import json
import os
import re
import unicodedata

import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
TABLO_DIR = os.path.join(ROOT, "tablolar")

# Kendi hesapladığımız ligler -> TheSportsDB lig ID'si (doğrulama için)
KENDI_HESAP = {203: "4339", 204: "4676"}
# football-data.org yarışma kodları
FOOTBALL_DATA = {39: "PL", 140: "PD", 135: "SA"}

SPONSOR = re.compile(r"\b(a\.?s\.?|a\.ş\.?|fk|sk|jk|futbol kulubu|kulubu|spor kulubu|metro holding|alagoz holding|"
                     r"batman petrol|ekenler beton|orfa yapi|turka|eminevim|arti deger|sms grup|misirlicomtr|"
                     r"caykur|tumosan|corendon|net global|ikas|zecorner|bellona|hesap\.com|natura dunyasi|"
                     r"atakas|kasimpasa as|rams)\b")


def norm(ad):
    s = unicodedata.normalize("NFKD", (ad or "").replace("ı", "i").replace("İ", "i")).encode("ascii", "ignore").decode()
    s = s.lower().replace("-", " ").replace(".", " ")
    s = SPONSOR.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def eslestir(ad, adaylar, alias=None):
    """API'den gelen takım adını tablodaki adla eşleştirir."""
    if alias and ad in alias:
        return alias[ad]
    if ad in adaylar:
        return ad
    n = norm(ad)
    nmap = {norm(a): a for a in adaylar}
    if n in nmap:
        return nmap[n]
    for k, v in nmap.items():  # biri diğerini içeriyorsa
        if n and k and (n in k or k in n):
            return v
    m = difflib.get_close_matches(n, list(nmap), n=1, cutoff=0.6)
    return nmap[m[0]] if m else None


# ------------------------------------------------------------ kendi tablomuz
def yol(lig):
    return os.path.join(TABLO_DIR, f"{lig}.json")


def yukle(lig):
    p = yol(lig)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def kaydet(lig, t):
    os.makedirs(TABLO_DIR, exist_ok=True)
    with open(yol(lig), "w", encoding="utf-8") as f:
        json.dump(t, f, ensure_ascii=False, indent=1)


def isle(lig, fixtures, bitti):
    """Biten ve daha önce işlenmemiş maçları tabloya ekler. Değişiklik varsa True ve uyarı listesi döner."""
    t = yukle(lig)
    if t is None:
        return False, []
    uyarilar, degisti = [], False
    takimlar = t["takimlar"]
    for f in fixtures:
        if f["league"]["id"] != lig or f["fixture"]["status"]["short"] not in bitti:
            continue
        fid = str(f["fixture"]["id"])
        if fid in t["islenen"]:
            continue
        ev = eslestir(f["teams"]["home"]["name"], takimlar, t.get("alias"))
        dep = eslestir(f["teams"]["away"]["name"], takimlar, t.get("alias"))
        if not ev or not dep or ev == dep:
            uyarilar.append(f"Tablo: takım eşleşmedi ({f['teams']['home']['name']} - {f['teams']['away']['name']})")
            continue
        eg, ag = f["goals"]["home"], f["goals"]["away"]
        for ad, at, ye in ((ev, eg, ag), (dep, ag, eg)):
            s = takimlar[ad]
            s["O"] += 1
            s["AV"] += at - ye
            if at > ye:
                s["G"] += 1
                s["P"] += 3
            elif at == ye:
                s["B"] += 1
                s["P"] += 1
            else:
                s["M"] += 1
        t["islenen"].append(fid)
        degisti = True
    if degisti:
        kaydet(lig, t)
    return degisti, uyarilar


def sirali(lig):
    t = yukle(lig)
    if not t:
        return []
    rows = [(ad, s["O"], s["G"], s["B"], s["M"], s["AV"], s["P"]) for ad, s in t["takimlar"].items()]
    rows.sort(key=lambda r: (-r[6], -r[5], -r[2], r[0]))
    return rows


def tsdb_ilk5(lig, sezon_str):
    """TheSportsDB ücretsiz: ilk 5 sıranın (oynanan, puan) değerleri."""
    r = requests.get(f"https://www.thesportsdb.com/api/v1/json/123/lookuptable.php",
                     params={"l": KENDI_HESAP[lig], "s": sezon_str}, timeout=30)
    rows = (r.json() or {}).get("table") or []
    return [(int(x["intPlayed"]), int(x["intPoints"])) for x in rows[:5]]


def dogrula(lig, sezon_str):
    """Kendi tablomuzun ilk 5'i TheSportsDB ile aynı mı? (ok, açıklama)"""
    biz = [(r[1], r[6]) for r in sirali(lig)[:5]]
    try:
        onlar = tsdb_ilk5(lig, sezon_str)
    except Exception as e:  # noqa: BLE001
        return False, f"TheSportsDB'ye ulaşılamadı: {e}"
    if not onlar:
        return False, "TheSportsDB tablo vermedi"
    if biz != onlar:
        return False, f"ilk 5 tutmuyor: biz {biz} / TheSportsDB {onlar}"
    return True, "ilk 5 tutuyor"


# ------------------------------------------------------------ football-data.org
def football_data(lig):
    key = os.environ.get("FOOTBALL_DATA_KEY", "").strip()
    if not key:
        raise RuntimeError("FOOTBALL_DATA_KEY tanımlı değil")
    r = requests.get(f"https://api.football-data.org/v4/competitions/{FOOTBALL_DATA[lig]}/standings",
                     headers={"X-Auth-Token": key}, timeout=30)
    r.raise_for_status()
    st = next(s for s in r.json()["standings"] if s["type"] == "TOTAL")["table"]
    return [((x["team"].get("shortName") or x["team"]["name"]), x["playedGames"], x["won"], x["draw"],
             x["lost"], x["goalDifference"], x["points"]) for x in st]
