"""Özel (elle hazırlanmış) bir postu paylaşır.

Kullanım: python ozel_paylas.py <görsel.jpg> [görsel2.jpg ...] --aciklama <aciklama.txt>
Görseller repo'ya önceden commit edilmiş olmalı (Instagram onları raw.githubusercontent'ten çeker).
"""
import os
import sys

from instagram import Instagram

args = sys.argv[1:]
i = args.index("--aciklama")
gorseller, aciklama = args[:i], open(args[i + 1], encoding="utf-8").read().strip()
repo = os.environ["GITHUB_REPOSITORY"]
dal = os.environ.get("GITHUB_REF_NAME", "main")
urls = [f"https://raw.githubusercontent.com/{repo}/{dal}/{g}" for g in gorseller]
print("Paylaşılıyor:", urls)
print(f"::notice::Paylaşıldı, medya ID: {Instagram().publish(urls, aciklama)}")
