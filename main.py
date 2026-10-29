"""@muhtemel11onbir otomasyonu - her 15 dakikada bir GitHub Actions tarafından çalıştırılır.

Ne yapar:
  - Maç günü öğlen: günün maç programı (Süper Lig + 1. Lig)
  - Kadrolar açıklanınca: Süper Lig ve milli maç ilk 11'leri
  - Maç bitince: Süper Lig / milli maç sonucu, 1. Lig toplu sonuçları
  - Hafta tamamlanınca: puan durumu
  - Milli maçtan bir gün önce: muhtemel 11 (son maçtaki 11'e göre)

Ortam değişkenleri:
  FOOTBALL_API_KEY, IG_TOKEN, IG_USER_ID  (GitHub Secrets)
  DRY_RUN=1  -> paylaşmaz, sadece görselleri üretir
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

import config
import render
from api_football import PlanHatasi

ROOT = os.path.dirname(os.path.abspath(__file__))
DRY_RUN = os.environ.get("DRY_RUN") == "1"
# Test modunda gerçek durum dosyasına ve posts/ klasörüne dokunulmaz
STATE_PATH = os.path.join(ROOT, ".state_test.json" if DRY_RUN else "state.json")
POSTS = "posts_test" if DRY_RUN else "posts"
TZ = ZoneInfo(config.TZ)
BITTI = {"FT", "AET", "PEN"}
IPTAL = {"PST", "CANC", "ABD", "AWD", "WO"}
CANLI = {"1H", "HT", "2H", "ET", "BT", "P", "SUSP", "INT", "LIVE"}
AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos",
         "Eylül", "Ekim", "Kasım", "Aralık"]
GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]


def log(*a):
    print(datetime.now(TZ).strftime("%H:%M:%S"), *a, flush=True)


# ------------------------------------------------------------------ yardımcılar
def ad(name):
    return config.AD_DUZELT.get(name, name)


def kisa_ad(name):
    name = re.sub(r"^(?:[A-ZÇĞİÖŞÜ]\.\s*)+", "", name or "").strip()
    return name.split()[-1] if len(name) > 15 else name


def tarih_str(dt):
    return f"{dt.day} {AYLAR[dt.month - 1]} {dt.year}, {GUNLER[dt.weekday()]}"


def hafta(round_name):
    m = re.search(r"(\d+)\s*$", round_name or "")
    return f"{m.group(1)}. Hafta" if m else (round_name or "")


def oyun_gunu(now):
    """Gece 03:00'e kadar önceki gün sayılır; böylece gece yarısını geçen maçlar da yakalanır."""
    return now - timedelta(hours=3)


UYARILAR = []


def lig_ust(lig):
    ayar = config.LIGLER.get(lig, {})
    return ayar.get("ust") or render.tr_upper(ayar.get("ad", ""))


def birlesik_tag(ligler, en_fazla=12):
    out = []
    for lig in ligler:
        for t in config.LIGLER[lig]["tag"].split():
            if t not in out:
                out.append(t)
    return " ".join(out[:en_fazla])


def lig_tag(f):
    return config.MILLI_TAG if is_milli(f) else config.LIGLER.get(f["league"]["id"], {}).get("tag", "")


def kickoff(fx):
    return datetime.fromisoformat(fx["fixture"]["date"]).astimezone(TZ)


def status(fx):
    return fx["fixture"]["status"]["short"]


def renk(team_name, lineup_team=None):
    try:
        c = lineup_team["colors"]["player"]
        return render.hex_rgb(c["primary"], None), render.hex_rgb(c["border"], (255, 255, 255))
    except (TypeError, KeyError):
        pass
    c = config.TAKIM_RENKLERI.get(team_name)
    return (render.hex_rgb(c[0], None), render.hex_rgb(c[1], None)) if c else None


def lig_adi(fx):
    return config.LIG_ADLARI.get(fx["league"]["id"], fx["league"]["name"])


def is_milli(fx):
    return config.TURKIYE_ID in (fx["teams"]["home"]["id"], fx["teams"]["away"]["id"])


# ------------------------------------------------------------------ durum
def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"posted": {}, "cache": {}}


def save_state(state):
    # 30 günden eski kayıtları temizle
    sinir = (datetime.now(TZ) - timedelta(days=30)).isoformat()
    state["posted"] = {k: v for k, v in state["posted"].items() if v >= sinir}
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)


# ------------------------------------------------------------------ yayın
class Yayinci:
    def __init__(self, state):
        self.state = state
        self.ig = None
        if not DRY_RUN:
            from instagram import Instagram
            self.ig = Instagram()
        self.repo = os.environ.get("GITHUB_REPOSITORY")
        self.branch = os.environ.get("GITHUB_REF_NAME", "main")

    def posted(self, key):
        return key in self.state["posted"]

    def mark(self, key):
        self.state["posted"][key] = datetime.now(TZ).isoformat()

    def _git(self, *args):
        subprocess.run(["git", *args], cwd=ROOT, check=True)

    def _push(self, paths, msg):
        save_state(self.state)
        self._git("add", *paths, "state.json")
        if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
            return  # görsel zaten yüklü, yapılacak bir şey yok
        self._git("commit", "-m", msg)
        for _ in range(3):
            try:
                self._git("pull", "--rebase", "-q")
                self._git("push", "-q")
                return
            except subprocess.CalledProcessError:
                time.sleep(5)
        raise RuntimeError("git push başarısız")

    def _url(self, path):
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        return f"https://raw.githubusercontent.com/{self.repo}/{self.branch}/{rel}"

    def paylas(self, key, images, caption):
        if self.posted(key):
            return
        log(f"PAYLAŞ [{key}] {len(images)} görsel")
        log("  " + caption.replace("\n", "\n  "))
        if DRY_RUN:
            self.mark(key)
            return
        self._push(images, f"görsel: {key}")
        urls = [self._url(p) for p in images]
        for u in urls:  # raw.githubusercontent hazır olana kadar bekle
            for _ in range(12):
                if requests.head(u, timeout=15).status_code == 200:
                    break
                time.sleep(5)
        media_id = self.ig.publish(urls, caption)
        self.mark(key)
        save_state(self.state)
        log(f"  paylaşıldı: {media_id}")


# ------------------------------------------------------------------ içerikler
def post_dir(now):
    return os.path.join(ROOT, POSTS, oyun_gunu(now).strftime("%Y-%m-%d"))


def gorev_program(fxs, now, y):
    if not config.PAYLAS["program"] or now.hour < config.PROGRAM_SAATI:
        return
    gun = oyun_gunu(now)
    key = f"program:{gun.date()}"
    if y.posted(key):
        return
    images, ozet, ligler = [], [], []
    for lig in config.LIGLER:
        maclar = sorted([f for f in fxs if f["league"]["id"] == lig and status(f) not in IPTAL],
                        key=kickoff)
        if not maclar:
            continue
        satir = [(kickoff(f).strftime("%H:%M"), ad(f["teams"]["home"]["name"]),
                  ad(f["teams"]["away"]["name"])) for f in maclar]
        alt = f"{tarih_str(gun)} · {hafta(maclar[0]['league']['round'])}"
        images.append(render.program(lig_ust(lig), alt, satir,
                                     os.path.join(post_dir(now), f"program_{lig}.jpg")))
        ligler.append(lig)
        ozet.append(f"🏟️ {config.LIG_ADLARI[lig]}\n" + "\n".join(f"{s} | {e} - {d}" for s, e, d in satir))
    if not images:
        return
    cap = (f"📅 GÜNÜN MAÇLARI | {tarih_str(gun)}\n\n" + "\n\n".join(ozet) +
           "\n\nSizce bugün kim kazanır? 👇\n\n" + birlesik_tag(ligler))
    y.paylas(key, images[:10], cap)


def satirlar_from_lineup(team):
    rows = {}
    xi = team.get("startXI") or []
    for p in xi:
        pl = p["player"]
        g = pl.get("grid")
        if g:
            r, c = (int(v) for v in g.split(":"))
        else:
            r, c = {"G": 1, "D": 2, "M": 3, "F": 4}.get(pl.get("pos"), 3), len(rows.get(3, [])) + 1
        rows.setdefault(r, []).append((c, pl.get("number"), kisa_ad(pl.get("name"))))
    out = []
    for r in sorted(rows, reverse=True):  # forvetler üstte
        # config.GRID_TERS: oyuncular kanatlarda ters görünürse True/False değiştir
        sira = sorted(rows[r], key=lambda t: t[0], reverse=config.GRID_TERS)
        out.append([(no, n) for _, no, n in sira])
    return out


def gorev_ilk11(fxs, now, api, y):
    for f in fxs:
        lig = f["league"]["id"]
        milli = is_milli(f)
        if not (milli and config.PAYLAS["milli_takim"] or config.LIGLER.get(lig, {}).get("ilk11")):
            continue
        key = f"ilk11:{f['fixture']['id']}"
        k = kickoff(f)
        if y.posted(key) or status(f) in IPTAL:
            continue
        if now < k - timedelta(minutes=config.ILK11_PENCERE_DK) or now > k + timedelta(minutes=20):
            continue
        lu = api.lineups(f["fixture"]["id"])
        if len(lu) < 2 or not all(t.get("startXI") for t in lu):
            log(f"kadro henüz yok: {f['teams']['home']['name']} - {f['teams']['away']['name']}")
            continue
        if milli:
            tr = [t for t in lu if t["team"]["id"] == config.TURKIYE_ID]
            if tr:
                y.state["cache"]["milli_son"] = {"fixture": f, "lineup": tr[0]}
        ev, dep = ad(f["teams"]["home"]["name"]), ad(f["teams"]["away"]["name"])
        mac = f"{ev} – {dep}"
        alt = f"{lig_adi(f)} · {hafta(f['league']['round'])} · {k.strftime('%H:%M')}"
        images = []
        for i, t in enumerate(lu):
            tn = ad(t["team"]["name"])
            images.append(render.kadro("İLK 11", render.tr_upper(mac), alt, tn, renk(tn, t),
                                       satirlar_from_lineup(t),
                                       os.path.join(post_dir(now), f"ilk11_{f['fixture']['id']}_{i}.jpg"),
                                       dizilis=t.get("formation"),
                                       hoca=(t.get("coach") or {}).get("name")))
        satir = []
        for t in lu:
            isimler = ", ".join(kisa_ad(p["player"]["name"]) for p in t["startXI"])
            satir.append(f"🔹 {ad(t['team']['name'])} ({t.get('formation') or '-'}): {isimler}")
        tag = lig_tag(f)
        cap = f"📋 İLK 11'LER BELLİ OLDU!\n\n⚔️ {mac} | {k.strftime('%H:%M')}\n\n" + "\n\n".join(satir) + f"\n\n{tag}"
        y.paylas(key, images, cap)


def goller(f, events):
    home_id = f["teams"]["home"]["id"]
    out = []
    for e in events:
        if e.get("type") != "Goal" or e.get("detail") == "Missed Penalty":
            continue
        if e.get("comments") == "Penalty Shootout":
            continue
        t = e["time"]
        dk = f"{t['elapsed']}+{t['extra']}" if t.get("extra") else str(t["elapsed"])
        notu = "P" if e["detail"] == "Penalty" else ("k.k." if e["detail"] == "Own Goal" else "")
        taraf = "ev" if e["team"]["id"] == home_id else "dep"
        out.append([dk, kisa_ad(e["player"]["name"]), taraf, notu])
    # skorla tutarlılık kontrolü: kendi kalesine goller yanlış tarafa yazıldıysa çevir
    eh, ea = f["goals"]["home"], f["goals"]["away"]
    if (sum(g[2] == "ev" for g in out), sum(g[2] == "dep" for g in out)) != (eh, ea):
        for g in out:
            if g[3] == "k.k.":
                g[2] = "dep" if g[2] == "ev" else "ev"
    return [tuple(g) for g in out]


def gorev_sonuc(fxs, now, api, y):
    for f in fxs:
        lig = f["league"]["id"]
        milli = is_milli(f)
        if not (milli and config.PAYLAS["milli_takim"] or config.LIGLER.get(lig, {}).get("sonuc") == "tekil"):
            continue
        key = f"sonuc:{f['fixture']['id']}"
        if y.posted(key) or status(f) not in BITTI:
            continue
        ev, dep = ad(f["teams"]["home"]["name"]), ad(f["teams"]["away"]["name"])
        events = api.events(f["fixture"]["id"])
        gl = goller(f, events)
        eh, ea = f["goals"]["home"], f["goals"]["away"]
        bilgi = []
        venue = (f["fixture"].get("venue") or {}).get("name")
        ref = (f["fixture"].get("referee") or "").split(",")[0].strip()
        if ref:
            bilgi.append(f"Hakem: {ref}")
        kirmizi = [f"{kisa_ad(e['player']['name'])} ({e['time']['elapsed']}')" for e in events
                   if e.get("type") == "Card" and "Red" in (e.get("detail") or "")]
        if kirmizi:
            bilgi.append("Kırmızı kart: " + ", ".join(kirmizi))
        ek = ""
        if status(f) == "AET":
            ek = "Uzatmalar sonucu"
        elif status(f) == "PEN":
            p = f["score"].get("penalty") or {}
            ek = f"Penaltılar: {p.get('home')}-{p.get('away')}"
        k = kickoff(f)
        alt = f"{k.day} {AYLAR[k.month - 1]} {k.year}" + (f" · {venue}" if venue else "")
        img = render.mac_sonucu({
            "lig": f"{lig_adi(f)} · {hafta(f['league']['round'])}", "alt": alt,
            "ev": ev, "dep": dep, "ev_renk": renk(ev), "dep_renk": renk(dep),
            "skor": (eh, ea), "goller": gl, "bilgi": bilgi, "ek": ek,
        }, os.path.join(post_dir(now), f"sonuc_{f['fixture']['id']}.jpg"))
        gol_txt = "\n".join(f"⚽ {dk}' {n}{' (' + nt + ')' if nt else ''} ({ev if t == 'ev' else dep})"
                            for dk, n, t, nt in gl)
        tag = lig_tag(f)
        cap = (f"🏁 MAÇ SONUCU\n\n{ev} {eh}-{ea} {dep}" + (f" ({ek})" if ek else "") +
               (f"\n\n{gol_txt}" if gol_txt else "") +
               f"\n\n📍 {lig_adi(f)} · {hafta(f['league']['round'])}\n\nMaçı nasıl buldunuz? 👇\n\n{tag}")
        y.paylas(key, [img], cap)


def gorev_toplu(fxs, now, y):
    """sonuc='toplu' olan ligler: günün tüm maçları bitince tek kart."""
    gun = oyun_gunu(now)
    for lig, ayar in config.LIGLER.items():
        if ayar.get("sonuc") != "toplu":
            continue
        maclar = [f for f in fxs if f["league"]["id"] == lig and status(f) not in IPTAL]
        key = f"toplu:{lig}:{gun.date()}"
        if not maclar or y.posted(key) or not all(status(f) in BITTI for f in maclar):
            continue
        maclar.sort(key=kickoff)
        son = [(ad(f["teams"]["home"]["name"]), f["goals"]["home"], f["goals"]["away"],
                ad(f["teams"]["away"]["name"])) for f in maclar]
        img = render.gunun_sonuclari(lig_ust(lig), f"{tarih_str(gun)} · {hafta(maclar[0]['league']['round'])}", son,
                                     os.path.join(post_dir(now), f"toplu_{lig}.jpg"))
        cap = (f"🏁 {lig_ust(lig)} | GÜNÜN SONUÇLARI\n\n" +
               "\n".join(f"{e} {a}-{b} {d}" for e, a, b, d in son) + f"\n\n{ayar['tag']}")
        y.paylas(key, [img], cap)


def gorev_puan(fxs, now, api, y):
    for lig, ayar in config.LIGLER.items():
        if not ayar.get("puan"):
            continue
        bugun = [f for f in fxs if f["league"]["id"] == lig]
        if not bugun or not all(status(f) in BITTI | IPTAL for f in bugun):
            continue
        rnd = bugun[0]["league"]["round"]
        key = f"puan:{lig}:{config.SEZON}:{rnd}"
        if y.posted(key):
            continue
        try:
            tum = api.round_fixtures(lig, config.SEZON, rnd, config.TZ)
            if not all(status(f) in BITTI | IPTAL for f in tum):
                continue  # haftanın maçları bitmedi
            st = api.standings(lig, config.SEZON)
        except PlanHatasi as e:
            UYARILAR.append(f"Puan durumu atlandı ({config.LIG_ADLARI[lig]}): ücretli plan gerekiyor. {e}")
            y.mark(key)  # bu hafta için tekrar deneme
            continue
        tablo = [(ad(r["team"]["name"]), r["all"]["played"], r["all"]["win"], r["all"]["draw"],
                  r["all"]["lose"], r["goalsDiff"], r["points"]) for r in st]
        if not tablo:
            continue
        img = render.puan_durumu(lig_ust(lig), f"{hafta(rnd)} sonu", tablo,
                                 os.path.join(post_dir(now), f"puan_{lig}.jpg"))
        ilk = "\n".join(f"{i + 1}. {t[0]} - {t[6]} puan" for i, t in enumerate(tablo[:5]))
        cap = (f"📊 {lig_ust(lig)} | PUAN DURUMU ({hafta(rnd)} sonu)\n\n{ilk}\n...\n\n"
               f"Şampiyon kim olur? 👇\n\n{ayar['tag']}")
        y.paylas(key, [img], cap)


def _son_milli_kadro(api, state, now):
    """Türkiye'nin son maçındaki ilk 11. Önce hafızadan, yoksa sezon fikstüründen bulur."""
    son = state["cache"].get("milli_son")
    if son:
        return son["fixture"], son["lineup"]
    try:  # ücretsiz planda izin verilmeyebilir
        maclar = api.fixtures_team_season(config.TURKIYE_ID, now.year, config.TZ)
    except Exception as e:  # noqa: BLE001
        log(f"son milli maç bulunamadı: {e}")
        return None, None
    biten = sorted([f for f in maclar if status(f) in BITTI and kickoff(f) < now], key=kickoff)
    if not biten:
        return None, None
    f = biten[-1]
    lu = [t for t in api.lineups(f["fixture"]["id"]) if t["team"]["id"] == config.TURKIYE_ID]
    if not lu or not lu[0].get("startXI"):
        return None, None
    state["cache"]["milli_son"] = {"fixture": f, "lineup": lu[0]}
    return f, lu[0]


def gorev_muhtemel11(now, api, y, state):
    if not config.PAYLAS["milli_takim"] or now.hour < config.MUHTEMEL11_SAATI:
        return
    c = state["cache"]
    yarin = str(now.date() + timedelta(days=1))
    if c.get("milli_yarin_date") != yarin:  # günde 1 API çağrısı
        c["milli_yarin"] = [f for f in api.fixtures_by_date(yarin, config.TZ) if is_milli(f)]
        c["milli_yarin_date"] = yarin
    for f in c.get("milli_yarin") or []:
        key = f"muhtemel11:{f['fixture']['id']}"
        if y.posted(key) or status(f) in IPTAL:
            continue
        l0, lu = _son_milli_kadro(api, state, now)
        if not lu:
            log("muhtemel 11: son milli maç kadrosu yok, atlanıyor")
            y.mark(key)
            continue
        rakip = ad(f["teams"]["away" if f["teams"]["home"]["id"] == config.TURKIYE_ID else "home"]["name"])
        son_rakip = ad(l0["teams"]["away" if l0["teams"]["home"]["id"] == config.TURKIYE_ID else "home"]["name"])
        k = kickoff(f)
        img = render.kadro("MUHTEMEL 11", f"TÜRKİYE – {render.tr_upper(rakip)}",
                           f"{tarih_str(k)} · {k.strftime('%H:%M')}", "Türkiye", renk("Turkey", lu),
                           satirlar_from_lineup(lu), os.path.join(post_dir(now), f"muhtemel11_{f['fixture']['id']}.jpg"),
                           dipnot=f"Tahmin: {son_rakip} maçındaki ilk 11 baz alınmıştır. Resmi kadro maç günü açıklanır.",
                           dizilis=lu.get("formation"), hoca=(lu.get("coach") or {}).get("name"))
        isimler = ", ".join(kisa_ad(p["player"]["name"]) for p in lu["startXI"])
        cap = (f"🇹🇷 MUHTEMEL 11 | Türkiye - {rakip}\n\n📅 {tarih_str(k)} · {k.strftime('%H:%M')}\n\n"
               f"{isimler}\n\nℹ️ Bu tahmin, {son_rakip} maçındaki ilk 11 baz alınarak hazırlanmıştır. "
               f"Resmi kadro maç günü açıklanır.\n\nSizin 11'iniz nasıl olurdu? 👇\n\n{config.MILLI_TAG}")
        y.paylas(key, [img], cap)


# ------------------------------------------------------------------ ana akış
def bugunun_maclari(now, api, state):
    """API çağrısını azaltmak için önbellekli.
    - Gün içinde ilk çalışmada bir kez çeker.
    - Maç saatlerinde en fazla 30 dakikada bir yeniler.
    - Sonucu beklenen (tekil paylaşılan) bir maç varsa her çalışmada yeniler.
    """
    c = state["cache"]
    today = str(oyun_gunu(now).date())
    fxs = c.get("fixtures") if c.get("fixtures_date") == today else None
    son = datetime.fromisoformat(c["fixtures_ts"]) if c.get("fixtures_ts") and fxs is not None else None

    def aktif(f):
        k = kickoff(f)
        return (k - timedelta(minutes=config.ILK11_PENCERE_DK + 15) <= now <= k + timedelta(hours=3)
                and status(f) not in IPTAL | BITTI)

    def sonuc_bekleniyor(f):
        tekil = is_milli(f) or config.LIGLER.get(f["league"]["id"], {}).get("sonuc") == "tekil"
        k = kickoff(f)
        return (tekil and status(f) not in IPTAL | BITTI and k + timedelta(minutes=100) <= now <= k + timedelta(hours=4)
                and f"sonuc:{f['fixture']['id']}" not in state["posted"])

    yenile = (fxs is None
              or any(sonuc_bekleniyor(f) for f in fxs)
              or (any(aktif(f) for f in fxs) and (son is None or now - son >= timedelta(minutes=28))))
    if yenile:
        hepsi = api.fixtures_by_date(today, config.TZ)
        fxs = [f for f in hepsi if f["league"]["id"] in config.LIGLER or is_milli(f)]
        c["fixtures"], c["fixtures_date"], c["fixtures_ts"] = fxs, today, now.isoformat()
        log(f"{today}: {len(fxs)} maç (API'den yenilendi)")
    return fxs


def eski_postlari_sil(now, gun=7):
    """Repo şişmesin diye 7 günden eski görselleri siler (Instagram'daki postlar etkilenmez)."""
    import shutil
    pdir = os.path.join(ROOT, POSTS)
    if not os.path.isdir(pdir):
        return
    sinir = (now - timedelta(days=gun)).strftime("%Y-%m-%d")
    for d in os.listdir(pdir):
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) and d < sinir:
            shutil.rmtree(os.path.join(pdir, d), ignore_errors=True)


def run(api, now=None):
    now = now or datetime.now(TZ)
    eski_postlari_sil(now)
    state = load_state()
    y = Yayinci(state)
    hatalar = []
    fxs = []
    try:
        fxs = bugunun_maclari(now, api, state)
    except Exception as e:  # noqa: BLE001
        hatalar.append(f"maç listesi: {e}")
    sadece = [g.strip() for g in os.environ.get("SADECE", "").split(",") if g.strip()]
    if "tani" in sadece:
        from instagram import Instagram
        t = Instagram().tani()
        log(f"TANI: {t}")
        for k, v in t.items():
            print(f"::notice::TANI {k}: {v}"[:900])
        return []
    for ad_, fn in [("program", lambda: gorev_program(fxs, now, y)),
                    ("ilk11", lambda: gorev_ilk11(fxs, now, api, y)),
                    ("sonuc", lambda: gorev_sonuc(fxs, now, api, y)),
                    ("toplu", lambda: gorev_toplu(fxs, now, y)),
                    ("puan", lambda: gorev_puan(fxs, now, api, y)),
                    ("muhtemel11", lambda: gorev_muhtemel11(now, api, y, state))]:
        if sadece and ad_ not in sadece:
            continue
        try:
            fn()
        except Exception as e:  # noqa: BLE001  bir görev patlarsa diğerleri yine çalışsın
            hatalar.append(f"{ad_}: {e}")
            log(f"HATA {ad_}: {e}")
    save_state(state)
    log(f"bitti. API çağrısı: {api.calls}")
    return hatalar


if __name__ == "__main__":
    from api_football import ApiFootball
    # TEST_TARIH=2026-10-26 -> o günü gün sonu (23:59) itibarıyla canlandırır (sadece test modunda)
    test_tarih = os.environ.get("TEST_TARIH", "").strip()
    now = None
    if test_tarih:
        if not DRY_RUN and not os.environ.get("SADECE", "").strip():
            sys.exit("Gerçek modda TEST_TARIH sadece SADECE ile birlikte kullanılabilir.")
        now = datetime.fromisoformat(test_tarih).replace(hour=23, minute=59, tzinfo=TZ)
        log(f"TEST: {test_tarih} günü canlandırılıyor")
    errs = run(ApiFootball(), now=now)
    for u in UYARILAR:
        print(f"::warning::{u}"[:900])
    if errs:
        for e in errs:  # GitHub'da "Annotations" olarak da görünsün
            print(f"::error::{e}"[:900])
        sys.exit(1)
