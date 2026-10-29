"""TFF resmi sitesinden puan cetveli okunabiliyor mu? (geçici)"""
import io
import requests
import pandas as pd

for ad, page in (("Süper Lig", 198), ("1. Lig", 142)):
    try:
        r = requests.get(f"https://www.tff.org/Default.aspx?pageID={page}", timeout=40,
                         headers={"User-Agent": "Mozilla/5.0 (muhtemel11-bot; haftalik puan cetveli)"})
        r.encoding = "utf-8"
        tables = pd.read_html(io.StringIO(r.text))
        aday = [t for t in tables if t.shape[0] >= 16 and t.shape[1] >= 8]
        line = f"{ad}: HTTP {r.status_code}, {len(tables)} tablo, aday {[t.shape for t in aday]}"
        print(f"::notice::{line}"[:900])
        for t in aday[:2]:
            print(f"::notice::{ad} örnek: " + t.head(4).to_csv(index=False).replace(chr(10), ' | ')[:850])
    except Exception as e:  # noqa: BLE001
        print(f"::notice::{ad}: HATA {e}"[:900])
