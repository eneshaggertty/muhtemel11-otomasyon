"""TFF sayfa örneklerini indirir (yapı incelemesi için, geçici)."""
import os, re, requests
H = {"User-Agent": "Mozilla/5.0 (muhtemel11-bot)"}
os.makedirs("veri/tff", exist_ok=True)
def al(ad, url):
    r = requests.get(url, headers=H, timeout=40)
    open(f"veri/tff/{ad}.html", "wb").write(r.content)
    return r.content.decode("utf-8", "ignore")
s = al("superlig_hafta10", "https://www.tff.org/Default.aspx?pageID=198&hafta=10")
al("superlig_guncel", "https://www.tff.org/Default.aspx?pageID=198")
al("birincilig_hafta12", "https://www.tff.org/Default.aspx?pageID=142&hafta=12")
mac_idler = sorted(set(re.findall(r"macId=(\d+)", s)))
open("veri/tff/mac_idler.txt", "w").write("\n".join(mac_idler))
for m in mac_idler[:2]:
    al(f"mac_{m}", f"https://www.tff.org/Default.aspx?pageId=29&macId={m}")
print(f"::notice::maç id: {mac_idler[:12]}")
