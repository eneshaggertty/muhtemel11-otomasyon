"""Instagram token'ını yeniler ve yeni token'ı .token_yeni dosyasına yazar (ekrana basmaz)."""
import os
from instagram import refresh_token

r = refresh_token(os.environ["IG_TOKEN"])
with open(".token_yeni", "w") as f:
    f.write(r["access_token"])
print(f"Token yenilendi, {r.get('expires_in', 0) // 86400} gün geçerli.")
