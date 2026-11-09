"""Hazır bir Reels videosunu Instagram'a yükler; istenirse belirli saate kadar bekleyip yayınlar.

Kullanım: python reels_paylas.py <video.mp4> <aciklama.txt> [--saat HH:MM] [--test]
--test: yükler ve işlenmesini bekler ama YAYINLAMAZ (deneme).
"""
import os
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from instagram import Instagram

args = sys.argv[1:]
video, aciklama = args[0], open(args[1], encoding="utf-8").read().strip()
test = "--test" in args
saat = args[args.index("--saat") + 1] if "--saat" in args else None

ig = Instagram()
c = ig._post(f"{ig.hedef}/media", media_type="REELS", upload_type="resumable", caption=aciklama, share_to_feed="true")
cid = c["id"]
uri = c.get("uri") or f"https://rupload.facebook.com/ig-api-upload/v23.0/{cid}"
with open(video, "rb") as f:
    r = requests.post(uri, data=f, timeout=300, headers={"Authorization": f"OAuth {ig.token}", "offset": "0",
                                                         "file_size": str(os.path.getsize(video))})
if not r.ok:
    sys.exit(f"Yükleme hatası {r.status_code}: {r.text[:300]}")
ig._wait(cid, timeout=900)
print(f"::notice::Video yüklendi ve işlendi (konteyner hazır).")
if test:
    print("::notice::TEST: yayınlanmadı.")
    sys.exit(0)
if saat:
    tz = ZoneInfo("Europe/Istanbul")
    hedef = datetime.now(tz).replace(hour=int(saat[:2]), minute=int(saat[3:5]), second=0, microsecond=0)
    bekle = (hedef - datetime.now(tz)).total_seconds()
    if bekle > 0:
        print(f"{saat}'e kadar {int(bekle)} sn bekleniyor")
        time.sleep(bekle)
mid = ig._post(f"{ig.hedef}/media_publish", creation_id=cid)["id"]
print(f"::notice::Yayınlandı ({datetime.now(ZoneInfo('Europe/Istanbul')).strftime('%H:%M:%S')}), medya ID: {mid}")
