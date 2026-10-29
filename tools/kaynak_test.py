"""TFF okuyucu testi (geçici)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tablo  # noqa: E402
for lig in (203, 204):
    try:
        rows = tablo.tff(lig)
        print(f"::notice::{lig}: {len(rows)} takım: " + "; ".join(f"{r[0]} {r[1]}O {r[5]:+d} {r[6]}P" for r in rows)[:850])
    except Exception as e:  # noqa: BLE001
        print(f"::notice::{lig}: HATA {e}"[:900])
