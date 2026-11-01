"""Hazır bir Reels videosunu ve açıklamasını Telegram'a gönderir.

Kullanım: python telegram_gonder.py <video.mp4> <aciklama.txt> "<müzik önerisi>"
"""
import json
import os
import sys

import telegram

video, aciklama, muzik = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "")
durum = json.load(open("state.json", encoding="utf-8"))
chat = durum.get("cache", {}).get("telegram_chat") or telegram.sohbet_bul()[0]
if not chat:
    sys.exit("Telegram sohbeti yok: bota /start yaz")
telegram.video(chat, video, (f"🎵 Müzik önerisi: {muzik}\n\n" if muzik else "") + "Açıklama bir sonraki mesajda 👇")
telegram.mesaj(chat, open(aciklama, encoding="utf-8").read().strip())
print("::notice::Telegram'a gönderildi")
