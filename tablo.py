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
        if f["fixture"]["date"][:10] <= t.get("baslangic", ""):
            continue  # başlangıç tablosuna zaten dahil
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
    if sorted(biz) != sorted(onlar):  # eşit puanlı takımların sırası farklı olabilir
        return False, f"ilk 5 tutmuyor: biz {biz} / TheSportsDB {onlar}"
    return True, "ilk 5 tutuyor"


# ------------------------------------------------------------ TFF resmi sitesi
TFF_SAYFA = {203: 198, 204: 142}
_TFF_TEMIZLE = re.compile(r"\b(A\.?Ş\.?|FUTBOL KULÜBÜ|SPORTİF FAALİYETLER|METRO HOLDİNG|ALAGÖZ HOLDİNG|"
                          r"BATMAN PETROL SPOR A\.Ş\.|EKENLER BETON|ORFA YAPI|TURKA|EMİNEVİM|ARTI DEĞER|SMS GRUP|"
                          r"MISIRLICOMTR|ÇAYKUR|TÜMOSAN|CORENDON|NET GLOBAL|İKAS|ZECORNER|BELLONA|HESAP\.COM|"
                          r"NATURA DÜNYASI|ATAKAŞ|RAMS|ARCA|KEÇTAŞ ANKARA|KULÜBÜ|FUTBOL)\b", re.IGNORECASE)


def _tff_ad(ham):
    s = re.sub(r"^\d+\.", "", ham).strip()
    s = _TFF_TEMIZLE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip(" .-")
    kucuk = s.replace("I", "ı").replace("İ", "i").lower()
    ad = " ".join(w[:1].replace("i", "İ").replace("ı", "I").upper() + w[1:] for w in kucuk.split())
    return re.sub(r"\bFk\b", "FK", re.sub(r"\bSk\b", "SK", ad))


def tff(lig):
    """TFF puan cetveli: [(ad, O, G, B, M, AV, P), ...] ya da hata."""
    from lxml import html as lh
    r = requests.get(f"https://www.tff.org/Default.aspx?pageID={TFF_SAYFA[lig]}", timeout=40,
                     headers={"User-Agent": "Mozilla/5.0 (muhtemel11-bot; haftalik puan cetveli)"})
    r.raise_for_status()
    metin = r.content.decode("utf-8", errors="strict") if b"charset=utf-8" in r.content[:3000].lower() else None
    if metin is None:
        try:
            metin = r.content.decode("utf-8")
        except UnicodeDecodeError:
            metin = r.content.decode("windows-1254")
    doc = lh.fromstring(metin)
    for tbl in doc.iter("table"):
        satirlar = []
        for tr in tbl.iter("tr"):
            hucre = [" ".join(td.text_content().split()) for td in tr.findall("td")]
            if len(hucre) == 9 and re.match(r"^\d+\.", hucre[0]) and all(re.match(r"^-?\d+$", h) for h in hucre[1:]):
                o, g, b, m, a, y, av, p = (int(h) for h in hucre[1:])
                satirlar.append((_tff_ad(hucre[0]), o, g, b, m, av, p))
        if len(satirlar) >= 16:
            return satirlar
    raise RuntimeError("TFF sayfasında puan cetveli bulunamadı")


def tff_ile_esitle(lig, satirlar, bugun):
    """TFF tablosunu kendi tablomuza yazar (isimler bizdekiyle eşleştirilir). Görüntülenecek satırları döner."""
    eski = yukle(lig)
    adlar = {}
    if eski:
        for r in satirlar:
            adlar[r[0]] = eslestir(r[0], eski["takimlar"], eski.get("alias")) or r[0]
    yeni = {"lig": (eski or {}).get("lig", str(lig)), "kaynak": f"TFF resmi puan cetveli ({bugun})",
            "baslangic": bugun, "alias": (eski or {}).get("alias", {}), "islenen": [],
            "takimlar": {adlar.get(r[0], r[0]): dict(zip(["O", "G", "B", "M", "AV", "P"], r[1:])) for r in satirlar}}
    kaydet(lig, yeni)
    return [(adlar.get(r[0], r[0]),) + tuple(r[1:]) for r in satirlar]


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
