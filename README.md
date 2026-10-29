# @muhtemel11onbir otomasyonu

Süper Lig, 1. Lig ve milli takım içeriklerini Instagram'a **kendiliğinden** paylaşan sistem.
GitHub Actions üzerinde her 15 dakikada bir çalışır, bilgisayarın açık olması gerekmez.

## Neyi, ne zaman paylaşır?

| İçerik | Ligler | Zaman |
|---|---|---|
| Günün maçları (her lig bir görsel, carousel) | Hepsi | Maç günü 12:00'den sonra |
| İlk 11 (iki takım, carousel) | Süper Lig + milli maç | Kadrolar açıklanınca |
| Maç sonucu (her maç ayrı) | Süper Lig + milli maç | Maç bitince |
| Günün sonuçları (tek kart) | 1. Lig, Premier Lig, La Liga, Serie A | O ligin günlük maçları bitince |
| Puan durumu | Hepsi | Haftanın tüm maçları bitince |
| Türkiye muhtemel 11 | Milli takım | Maçtan bir gün önce 20:00'den sonra |

Ligleri ve her lig için ne paylaşılacağını `config.py` içindeki `LIGLER` tablosundan değiştirebilirsin.
Sistem İstanbul saatiyle 10:00 - 02:00 arası 15 dakikada bir çalışır.

## Kurulum

1. **Secrets ekle:** Repo → Settings → Secrets and variables → Actions → *New repository secret*
   - `IG_TOKEN` – Meta panelinden aldığın Instagram token'ı
   - `IG_USER_ID` – Instagram kullanıcı ID'si (Meta panelinde hesabının altındaki numara)
   - `FOOTBALL_API_KEY` – API-Football anahtarı
   - `GH_PAT` – (token'ın otomatik yenilenmesi için) aşağıya bak
2. **Test et:** Actions → *Muhtemel11 Otomasyon* → *Run workflow* → "Test modu" işaretli çalıştır.
   Paylaşım yapmaz; üretilen görseller çalışmanın sonunda *gorseller* adıyla indirilebilir.
3. **Canlıya al:** Hiçbir şey yapmana gerek yok, zamanlanmış çalışmalar gerçek paylaşım yapar.
   Durdurmak için: Actions → *Muhtemel11 Otomasyon* → ••• → *Disable workflow*.

## Token yenileme

Instagram token'ı 60 gün geçerli. *Instagram token yenile* iş akışı her pazartesi yeniler ve
yeni token'ı `IG_TOKEN`'a yazar. Bunun için bir kez **GH_PAT** oluştur:
GitHub → Settings → Developer settings → Fine-grained tokens → *Generate new token* →
sadece bu repo, **Secrets: Read and write** izni → oluşan anahtarı `GH_PAT` adıyla secret olarak ekle.

GH_PAT eklemezsen 50 günde bir Meta panelinden yeni token alıp `IG_TOKEN`'ı elle güncelle.

## Notlar

- **API kotası:** Sistem API'ye sadece maç saatlerine yakın istek atar (maç günü yaklaşık 40-80 istek).
  API-Football ücretsiz planı güncel sezonu kapsamıyorsa ücretli plana geçmek gerekir.
- **İlk 11'de kanatlar ters görünürse** `config.py` içinde `GRID_TERS` değerini değiştir.
- **Kulüp armaları ve oyuncu fotoğrafları kullanılmaz** (tescilli marka / telif). Takım renkleri kullanılır.
- Yerel test: `pip install -r requirements.txt && python test_mock.py` (sahte veriyle bir maç gününü simüle eder).
