# Yapılacaklar

## 1. Ücretsiz puan durumu ✅ (29 Ekim)
- Süper Lig + 1. Lig: TFF resmi puan cetveli (tff.org pageID 198 / 142). Yedek: tablolar/<lig>.json kendi hesabımız + TheSportsDB ilk 5 kontrolü
- Premier Lig / La Liga / Serie A: football-data.org (secret FOOTBALL_DATA_KEY)
- [ ] İlk gerçek hafta sonunda (Süper Lig 10. hafta) paylaşılan kartları kontrol et

## 2. X (Twitter) hesabı
- [ ] Sayfanın X hesabına da Instagram ile aynı anda paylaşım
- [ ] X API erişimi ve güncel ücret/limitler araştırılacak, kullanıcıdan X geliştirici hesabı/anahtarları
- [ ] Carousel -> X'te en fazla 4 görsel; açıklama 280 karakter sınırına göre kısaltılacak

## 3. Diğer Instagram hesabının video otomasyonunu GitHub'a taşı
- [ ] Şu an kullanıcının bilgisayarında çalışıyor (bilgisayar kapanamıyor)
- [ ] Mevcut kurulumu incele (ne üretiyor, hangi araçlar, nasıl paylaşıyor), GitHub Actions'a taşı
- [ ] Video üretimi Actions'ta çalışmalı (ffmpeg vb.), Reels paylaşımı Instagram API ile

## 4. Ayrı proje: YouTube çizgi filmi
- [ ] Konu, karakterler, hedef kitle ve bölüm uzunluğu konuşulacak (özgün karakterler)

## Notlar
- Instagram token'ı: sistem kullanıcısı (muhtemel11-bot), süresiz. IG_USER_ID = 17841410173892684
- API-Football ücretsiz: sadece dün/bugün/yarın tarihli maç sorguları; sezon/sonraki/son maç sorguları ve puan tablosu yok
- İlk 11 kartları gerçek maçta henüz denenmedi (kanat yönü: `config.GRID_TERS`)
