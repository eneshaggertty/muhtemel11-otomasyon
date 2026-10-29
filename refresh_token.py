"""Instagram token'ını yeniler ve yeni token'ı .token_yeni dosyasına yazar (ekrana basmaz).

Facebook/sistem kullanıcısı token'ları (EAA...) süresizdir, yenilenmeleri gerekmez.
"""
import os
import sys
from instagram import refresh_token

token = os.environ["IG_TOKEN"].strip()
if token.startswith("EAA"):
    print("Sistem kullanıcısı token'ı: süresiz, yenileme gerekmiyor.")
    sys.exit(0)
r = refresh_token(token)
with open(".token_yeni", "w") as f:
    f.write(r["access_token"])
print(f"Token yenilendi, {r.get('expires_in', 0) // 86400} gün geçerli.")
