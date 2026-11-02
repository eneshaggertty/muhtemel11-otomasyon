"""Ücretsiz veri kaynağı (API-Football yerine).

- Süper Lig / 1. Lig: TFF resmi sitesi (fikstür, skor, ilk 11, goller, kartlar, hakem, stadyum)
- Premier Lig / La Liga / Serie A: football-data.org (fikstür, skor)

main.py'nin beklediği API-Football biçiminde veri döner, böylece ana kod değişmeden çalışır.
"""
import os
import re
import zlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from lxml import html as lh

import config
import tablo

TZ = ZoneInfo(config.TZ)
H = {"User-Agent": "Mozilla/5.0 (muhtemel11-bot; kisisel futbol sayfasi)"}
TFF_LIG_SAYFA = {config.SUPER_LIG: 198, config.BIRINCI_LIG: 142}
FD_LIG = {39: "PL", 140: "PD", 135: "SA"}
FD_DURUM = {"FINISHED": "FT", "IN_PLAY": "LIVE", "PAUSED": "HT", "SCHEDULED": "NS", "TIMED": "NS",
            "POSTPONED": "PST", "SUSPENDED": "SUSP", "CANCELLED": "CANC", "AWARDED": "AWD"}
FD_KAYDIR = 10_000_000_000   # football-data maç ID'lerini TFF'ninkilerle karışmasın diye kaydır
MAC_SURESI_DK = 120          # skor varsa ve başlangıçtan bu kadar dakika geçtiyse maç bitti sayılır


class PlanHatasi(RuntimeError):
    pass


def _takim_id(ad):
    return zlib.crc32(ad.encode("utf-8")) % 1_000_000


def _decode(b):
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("windows-1254")


def _ad_temizle(ham):
    ad = tablo._tff_ad(ham)
    return {"İstanbul Başakşehir FK": "Başakşehir", "Gaziantep": "Gaziantep FK", "Amed": "Amed SFK",
            "Rizespor": "Çaykur Rizespor"}.get(ad, ad)


def _kisi(ham):
    """'DEIAN CRISTIAN SORESCU' -> 'Deian Cristian Sorescu', 'ALİ OSMAN KALIN' -> 'Ali Osman Kalın'.
    TFF büyük harf kullanıyor; 'I' Türkçe isimde 'ı', yabancı isimde 'i' demek. İsimde Türkçe harf varsa Türkçe sayılır."""
    s = " ".join((ham or "").split())
    turkce = any(c in s for c in "ÇĞİÖŞÜçğıöşü")
    kucuk = s.replace("I", "ı").replace("İ", "i").lower() if turkce else s.lower()

    def bas(w):
        if not w:
            return w
        ilk = w[0]
        ilk = "İ" if ilk == "i" and turkce else ("I" if ilk == "ı" else ilk.upper())
        return ilk + w[1:]
    return " ".join("-".join(bas(p) for p in w.split("-")) for w in kucuk.split())


class Kaynak:
    def __init__(self):
        self.calls = 0
        self.now = datetime.now(TZ)
        self._sayfa = {}
        self._hafta_cache = {}
        self._mac = {}

    # ---------------------------------------------------------------- yardımcılar
    def _get(self, url, **kw):
        self.calls += 1
        r = requests.get(url, headers={**H, **kw.pop("headers", {})}, timeout=40, **kw)
        r.raise_for_status()
        return r

    def _tff_sayfa(self, sayfa_id, hafta=None):
        key = (sayfa_id, hafta)
        if key not in self._sayfa:
            url = f"https://www.tff.org/Default.aspx?pageID={sayfa_id}" + (f"&hafta={hafta}" if hafta else "")
            self._sayfa[key] = _decode(self._get(url).content)
        return self._sayfa[key]

    def _tff_hafta(self, lig, hafta=None):
        """Bir haftanın maçları: [(macId, datetime, ev, dep, skor|None)], hafta numarası"""
        key = (lig, hafta)
        if key in self._hafta_cache:
            return self._hafta_cache[key]
        s = self._tff_sayfa(TFF_LIG_SAYFA[lig], hafta)
        doc = lh.fromstring(s)
        maclar = []
        for tr in doc.iter("tr"):
            hucre = [" ".join(td.text_content().split()) for td in tr.findall("td")]
            link = next((a.get("href") for a in tr.iter("a") if "macId=" in (a.get("href") or "")), None)
            if len(hucre) != 5 or not link or not re.match(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}", hucre[0]):
                continue
            mac_id = int(re.search(r"macId=(\d+)", link).group(1))
            tarih = datetime.strptime(hucre[0], "%d.%m.%Y %H:%M").replace(tzinfo=TZ)
            m = re.match(r"^(\d+)\s*-\s*(\d+)$", hucre[2])
            skor = (int(m.group(1)), int(m.group(2))) if m else None
            maclar.append((mac_id, tarih, hucre[1], hucre[3], skor))
        maclar = list({m[0]: m for m in maclar}.values())
        no = hafta
        if no is None:
            m = re.search(r"(\d+)\.Hafta", s)
            no = int(m.group(1)) if m else None
        self._hafta_cache[key] = (maclar, no)
        self._hafta_cache[(lig, no)] = (maclar, no)
        return maclar, no

    def _tff_fixture(self, lig, mac, hafta):
        mac_id, tarih, ev, dep, skor = mac
        if skor is None:
            durum = "NS"
        elif self.now >= tarih + timedelta(minutes=MAC_SURESI_DK):
            durum = "FT"
        else:
            durum = "LIVE"
        ev_ad, dep_ad = _ad_temizle(ev), _ad_temizle(dep)
        return {
            "kaynak": "tff",
            "fixture": {"id": mac_id, "date": tarih.isoformat(), "status": {"short": durum},
                        "venue": {"name": None}, "referee": None},
            "league": {"id": lig, "name": config.LIG_ADLARI.get(lig, ""), "round": f"Regular Season - {hafta}"},
            "teams": {"home": {"id": _takim_id(ev_ad), "name": ev_ad}, "away": {"id": _takim_id(dep_ad), "name": dep_ad}},
            "goals": {"home": skor[0] if skor else None, "away": skor[1] if skor else None},
            "score": {"penalty": {}},
        }

    # ---------------------------------------------------------------- TFF maç sayfası
    def _tff_mac(self, mac_id):
        if mac_id in self._mac:
            return self._mac[mac_id]
        s = _decode(self._get(f"https://www.tff.org/Default.aspx?pageId=29&macId={mac_id}").content)
        doc = lh.fromstring(s)

        def ids(desen):
            return [e for e in doc.iter() if re.search(desen, e.get("id") or "")]

        def tek(desen):
            e = ids(desen)
            return " ".join(e[0].text_content().split()) if e else ""

        sonuc = {"stad": _kisi(tek(r"dtMacBilgisi_lnkStad$").split(" - ")[0]) or None,
                 "hakem": _kisi(re.sub(r"\(.*?\)", "", tek(r"dtMacBilgisi_rpt_ctl00_lnkHakem$"))) or None,
                 "takimlar": []}
        for t in (1, 2):
            no = {e.get("id").rsplit("_", 2)[-2]: e.text_content().strip(" .")
                  for e in ids(rf"grdTakim{t}_rptKadrolar_ctl\d+_formaNo$")}
            ilk11 = [(int(no.get(e.get("id").rsplit("_", 2)[-2], "0") or 0), _kisi(e.text_content()))
                     for e in ids(rf"grdTakim{t}_rptKadrolar_ctl\d+_lnkOyuncu$")]
            hoca = tek(rf"grdTakim{t}_rptTeknikKadro_ctl\d+_lnkTeknikSorumlu$")
            goller = []
            for e in ids(rf"grdTakim{t}_rptGoller_ctl\d+_lblGol$"):
                m = re.match(r"(.+?),\s*(\d+)(?:\+(\d+))?\.dk\s*\((\w)\)", " ".join(e.text_content().split()))
                if m:
                    goller.append((_kisi(m.group(1)), int(m.group(2)), int(m.group(3)) if m.group(3) else None, m.group(4)))
            kartlar = []
            for e in ids(rf"grdTakim{t}_rptKartlar_ctl\d+_lblKart$"):
                kok = e.get("id").rsplit("_", 1)[0]
                img = next((x for x in doc.iter("img") if x.get("id") == kok + "_k"), None)
                dk = next((x for x in doc.iter("span") if x.get("id") == kok + "_d"), None)
                kirmizi = img is not None and "kirmizi" in (img.get("src") or "").lower()
                m = re.match(r"(\d+)(?:\+(\d+))?", (dk.text_content() if dk is not None else "0").strip())
                kartlar.append((_kisi(e.text_content()), int(m.group(1)) if m else 0, kirmizi))
            sonuc["takimlar"].append({"ilk11": ilk11, "hoca": _kisi(hoca) if hoca else None,
                                      "goller": goller, "kartlar": kartlar})
        self._mac[mac_id] = sonuc
        return sonuc

    # ---------------------------------------------------------------- football-data.org
    def _fd(self, tarih_bas, tarih_son):
        key = os.environ.get("FOOTBALL_DATA_KEY", "").strip()
        if not key:
            return []
        r = self._get("https://api.football-data.org/v4/matches",
                      params={"dateFrom": tarih_bas, "dateTo": tarih_son, "competitions": ",".join(FD_LIG.values())},
                      headers={"X-Auth-Token": key})
        ters = {v: k for k, v in FD_LIG.items()}
        out = []
        for m in r.json().get("matches", []):
            lig = ters.get(m["competition"]["code"])
            if lig not in config.LIGLER:
                continue
            ft = m["score"]["fullTime"]
            ev = m["homeTeam"].get("shortName") or m["homeTeam"]["name"]
            dep = m["awayTeam"].get("shortName") or m["awayTeam"]["name"]
            out.append({
                "kaynak": "fd",
                "fixture": {"id": FD_KAYDIR + m["id"], "status": {"short": FD_DURUM.get(m["status"], "NS")},
                            "date": datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00")).astimezone(TZ).isoformat(),
                            "venue": {"name": None}, "referee": None},
                "league": {"id": lig, "name": config.LIG_ADLARI[lig], "round": f"Regular Season - {m.get('matchday')}"},
                "teams": {"home": {"id": m["homeTeam"]["id"], "name": ev}, "away": {"id": m["awayTeam"]["id"], "name": dep}},
                "goals": {"home": ft.get("home"), "away": ft.get("away")}, "score": {"penalty": {}},
            })
        return out

    # ---------------------------------------------------------------- main.py arayüzü
    def fixtures_by_date(self, date, tz=None):
        gun = datetime.fromisoformat(date).date()
        out = []
        for lig in TFF_LIG_SAYFA:
            if lig not in config.LIGLER:
                continue
            maclar, no = self._tff_hafta(lig)
            haftalar = [(maclar, no)]
            if no:  # güncel haftada o gün yoksa komşu haftalara bak
                if not any(m[1].date() == gun for m in maclar):
                    for h in (no + 1, no - 1):
                        if h >= 1:
                            haftalar.append(self._tff_hafta(lig, h))
            for maclar_h, no_h in haftalar:
                out += [self._tff_fixture(lig, m, no_h) for m in maclar_h if m[1].date() == gun]
        try:  # football-data UTC çalışır ve bitiş gününü dahil etmeyebilir: aralığı genişletip yerel tarihe göre süz
            bas, son = str(gun - timedelta(days=1)), str(gun + timedelta(days=1))
            out += [f for f in self._fd(bas, son) if datetime.fromisoformat(f["fixture"]["date"]).date() == gun]
        except Exception as e:  # noqa: BLE001
            print(f"::warning::football-data okunamadı: {e}"[:900])
        return list({f["fixture"]["id"]: f for f in out}.values())

    def fixture(self, fixture_id, tz=None):
        return None

    def lineups(self, fixture_id):
        if fixture_id >= FD_KAYDIR:
            return []
        m = self._tff_mac(fixture_id)
        out = []
        for i, t in enumerate(m["takimlar"]):
            if len(t["ilk11"]) < 11:
                return []  # kadrolar henüz açıklanmadı
            out.append({"team": {"id": i, "name": None}, "formation": None, "coach": {"name": t["hoca"]},
                        "startXI": [{"player": {"name": ad, "number": no, "grid": None, "pos": None}} for no, ad in t["ilk11"]]})
        return out

    def events(self, fixture_id):
        if fixture_id >= FD_KAYDIR:
            return []
        m = self._tff_mac(fixture_id)
        ev = []
        for i, t in enumerate(m["takimlar"]):
            for ad, dk, ek, tip in t["goller"]:
                if tip == "S":
                    continue  # seri penaltılar
                detay = {"P": "Penalty", "K": "Own Goal"}.get(tip, "Normal Goal")
                ev.append({"time": {"elapsed": dk, "extra": ek}, "team": {"id": f"t{i}"}, "player": {"name": ad},
                           "type": "Goal", "detail": detay, "taraf": "ev" if i == 0 else "dep"})
            for ad, dk, kirmizi in t["kartlar"]:
                ev.append({"time": {"elapsed": dk, "extra": None}, "team": {"id": f"t{i}"}, "player": {"name": ad},
                           "type": "Card", "detail": "Red Card" if kirmizi else "Yellow Card", "taraf": "ev" if i == 0 else "dep"})
        return ev

    def mac_detay(self, fixture_id):
        """Hakem ve stadyum (TFF)."""
        if fixture_id >= FD_KAYDIR:
            return {}
        m = self._tff_mac(fixture_id)
        return {"hakem": m["hakem"], "stad": m["stad"]}

    def fixtures_team(self, *a, **k):
        raise PlanHatasi("Bu kaynakta takım fikstürü yok")

    def fixtures_team_season(self, *a, **k):
        raise PlanHatasi("Bu kaynakta takım fikstürü yok")
