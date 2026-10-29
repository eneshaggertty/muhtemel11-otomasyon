"""football-data.org anahtar testi (geçici)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tablo  # noqa: E402
for lig in (39, 140, 135):
    try:
        rows = tablo.football_data(lig)
        line = f"{lig}: {len(rows)} takım; ilk 3: {[(r[0], r[1], r[6]) for r in rows[:3]]}"
    except Exception as e:  # noqa: BLE001
        line = f"{lig}: HATA {e}"
    print(f"::notice::{line}"[:900])
