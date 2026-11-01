"""Telegram bildirimleri (yarı otomatik paylaşım için).

Sistem Reels videosunu ve açıklamayı Telegram'dan kullanıcıya gönderir; kullanıcı Instagram'da
kütüphaneden müziği (ör. takım marşı) ekleyip kendisi paylaşır.
"""
import os

import requests

API = "https://api.telegram.org/bot{token}/{metod}"


def _token():
    t = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not t:
        raise RuntimeError("TELEGRAM_BOT_TOKEN tanımlı değil")
    return t


def _cagir(metod, **kw):
    r = requests.post(API.format(token=_token(), metod=metod), timeout=120, **kw)
    j = r.json()
    if not j.get("ok"):
        raise RuntimeError(f"Telegram {metod} hatası: {j.get('description')}")
    return j["result"]


def sohbet_bul():
    """Bota en son mesaj atan kişinin sohbet ID'si (kurulum için)."""
    guncellemeler = _cagir("getUpdates", data={"limit": 50})
    for u in reversed(guncellemeler):
        msg = u.get("message") or u.get("edited_message") or {}
        chat = msg.get("chat") or {}
        if chat.get("type") == "private":
            return chat["id"], chat.get("first_name", "")
    return None, None


def mesaj(chat_id, metin):
    for i in range(0, len(metin), 4000):  # Telegram sınırı 4096 karakter
        _cagir("sendMessage", data={"chat_id": chat_id, "text": metin[i:i + 4000]})


def video(chat_id, yol, baslik=""):
    with open(yol, "rb") as f:
        return _cagir("sendVideo", data={"chat_id": chat_id, "caption": baslik[:1000], "supports_streaming": "true",
                                         "width": 1080, "height": 1920},
                      files={"video": (os.path.basename(yol), f, "video/mp4")})


def foto(chat_id, yollar, baslik=""):
    if len(yollar) == 1:
        with open(yollar[0], "rb") as f:
            return _cagir("sendPhoto", data={"chat_id": chat_id, "caption": baslik[:1000]},
                          files={"photo": (os.path.basename(yollar[0]), f, "image/jpeg")})
    import json
    dosyalar = {f"f{i}": open(y, "rb") for i, y in enumerate(yollar[:10])}
    try:
        medya = [{"type": "photo", "media": f"attach://f{i}", **({"caption": baslik[:1000]} if i == 0 else {})}
                 for i in range(len(dosyalar))]
        return _cagir("sendMediaGroup", data={"chat_id": chat_id, "media": json.dumps(medya)}, files=dosyalar)
    finally:
        for f in dosyalar.values():
            f.close()
