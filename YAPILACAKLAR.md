# Yapılacaklar

## 1. Ücretsiz puan durumu (yarım kaldı)
- [x] `tablo.py` yazıldı (henüz `main.py`'ye bağlı değil)
- [ ] Kullanıcıdan: football-data.org ücretsiz anahtarı -> GitHub secret `FOOTBALL_DATA_KEY`
      (Premier Lig `PL`, La Liga `PD`, Serie A `SA` tabloları)
- [ ] Kullanıcıdan: Maçkolik'ten 1. Lig güncel puan tablosu ekran görüntüsü -> `tablolar/204.json` başlangıcı
- [ ] Süper Lig başlangıç tablosu (9. hafta sonu, goal.com) -> `tablolar/203.json`
      Galatasaray 9-7-1-1 +7 22 · Amed 9-6-2-1 +10 20 · Trabzonspor 9-6-1-2 +14 19 · Beşiktaş 9-6-0-3 +8 18 ·
      Fenerbahçe 9-5-1-3 +15 16 · Kasımpaşa 9-4-4-1 +4 16 · Kocaelispor 9-5-0-4 +2 15 · Erzurumspor 9-4-2-3 -4 14 ·
      Çorum FK 9-4-1-4 +3 13 · Göztepe 9-3-3-3 +3 12 · Alanyaspor 9-3-3-3 -2 12 · Başakşehir 9-3-2-4 -2 11 ·
      Rizespor 9-3-1-5 -4 10 · Konyaspor 9-2-2-5 -3 8 · Gaziantep 9-2-2-5 -6 8 · Gençlerbirliği 9-2-2-5 -11 8 ·
      Samsunspor 9-1-1-7 -13 4 · Eyüpspor 9-1-0-8 -21 3
- [ ] `main.py` `gorev_puan`: kendi tablo (203, 204) + TheSportsDB ilk 5 doğrulaması; football-data (39, 140, 135)
- [ ] Haftanın bittiğini anlamak: bugünün maçları bitti + yarın aynı haftadan maç yok (yarının listesi, günde 1 istek)
- [ ] Dünün maçlarını günde bir kez tekrar işle (kaçan sonuç olmasın)
- [ ] Gerçek veriyle test, sonra `tools/kaynak_test.py` ve `kaynak-test.yml` sil

## 2. X (Twitter) hesabı
- [ ] Sayfanın X hesabına da Instagram ile aynı anda paylaşım
- [ ] X API erişimi ve güncel ücret/limitler araştırılacak, kullanıcıdan X geliştirici hesabı/anahtarları
- [ ] Carousel -> X'te en fazla 4 görsel; açıklama 280 karakter sınırına göre kısaltılacak

## Notlar
- Instagram token'ı: sistem kullanıcısı (muhtemel11-bot), süresiz. IG_USER_ID = 17841410173892684
- API-Football ücretsiz: sadece dün/bugün/yarın tarihli maç sorguları; sezon/sonraki/son maç sorguları ve puan tablosu yok
- İlk 11 kartları gerçek maçta henüz denenmedi (kanat yönü: `config.GRID_TERS`)
