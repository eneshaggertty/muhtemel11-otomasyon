"""Ayarlar. Değiştirmek istediğin her şey burada."""

HANDLE = "@muhtemel11onbir"
SLOGAN = "Futbolda son dakika burada"
TZ = "Europe/Istanbul"

# API-Football lig ID'leri
SUPER_LIG = 203
BIRINCI_LIG = 204
SEZON = 2026  # 2026/27 sezonu

# Takip edilen ligler ve her biri için ne paylaşılacağı.
#   ilk11 : kadrolar açıklanınca her maçın ilk 11'i (2 görsel, carousel)
#   sonuc : "tekil" = her maç bitince ayrı kart, "toplu" = günün maçları bitince tek kart, None = paylaşma
#   puan  : haftanın tüm maçları bitince puan durumu
# Bir ligi kapatmak için satırını silmen ya da başına # koyman yeterli.
LIGLER = {
    SUPER_LIG:   {"ad": "Trendyol Süper Lig", "ilk11": True,  "sonuc": "tekil", "puan": True,
                  "tag": "#süperlig #trendyolsüperlig #futbol #türkfutbolu #muhtemel11"},
    BIRINCI_LIG: {"ad": "Trendyol 1. Lig",    "ilk11": False, "sonuc": "toplu", "puan": True,
                  "tag": "#1lig #trendyol1lig #futbol #türkfutbolu #muhtemel11"},
    39:          {"ad": "Premier Lig",        "ilk11": False, "sonuc": "toplu", "puan": True,
                  "tag": "#premierlig #premierleague #ingiltere #futbol #muhtemel11"},
    140:         {"ad": "La Liga",            "ilk11": False, "sonuc": "toplu", "puan": True,
                  "tag": "#laliga #ispanya #futbol #muhtemel11"},
    135:         {"ad": "Serie A",            "ilk11": False, "sonuc": "toplu", "puan": True,
                  "tag": "#seriea #italya #futbol #muhtemel11"},
}
LIG_ADLARI = {k: v["ad"] for k, v in LIGLER.items()}

# Türkiye A Milli Takımı (API-Football takım ID'si)
TURKIYE_ID = 777

# Genel ayarlar
PAYLAS = {
    "program": True,       # maç günü öğlen: günün maçları (her lig bir görsel, carousel)
    "milli_takim": True,   # Türkiye: muhtemel 11 (maçtan 1 gün önce), ilk 11, sonuç
}

PROGRAM_SAATI = 12           # günün maçları bu saatten sonra paylaşılır
MUHTEMEL11_SAATI = 20        # milli maçtan bir gün önce bu saatten sonra
ILK11_PENCERE_DK = 60        # maça bu kadar dakika kala kadroları kontrol etmeye başla
GRID_TERS = True             # ilk 11 kartında sağ/sol kanat ters çıkarsa False yap

MILLI_TAG = "#bizimçocuklar #türkiye #millitakım #futbol #muhtemel11"

# Takım renkleri: API kadro verisinde renk gelmezse kullanılır
TAKIM_RENKLERI = {
    "Galatasaray": ("#A90329", "#FDB913"),
    "Fenerbahce": ("#162357", "#FFED00"),
    "Fenerbahçe": ("#162357", "#FFED00"),
    "Besiktas": ("#111111", "#FFFFFF"),
    "Beşiktaş": ("#111111", "#FFFFFF"),
    "Trabzonspor": ("#7A1F3D", "#4FA3DE"),
    "Basaksehir": ("#F26A21", "#1B2A4A"),
    "Turkey": ("#E30A17", "#FFFFFF"),
}

# Takım adlarını Türkçeleştirme (API bazen İngilizce/aksansız verir)
AD_DUZELT = {
    "Fenerbahce": "Fenerbahçe", "Besiktas": "Beşiktaş", "Basaksehir": "Başakşehir",
    "Istanbul Basaksehir": "Başakşehir", "Goztepe": "Göztepe", "Kasimpasa": "Kasımpaşa",
    "Genclerbirligi": "Gençlerbirliği", "Eyupspor": "Eyüpspor", "Rizespor": "Çaykur Rizespor",
    "Corum FK": "Çorum FK", "Turkey": "Türkiye", "Turkiye": "Türkiye",
    # milli takım rakipleri
    "Spain": "İspanya", "Georgia": "Gürcistan", "Bulgaria": "Bulgaristan", "Germany": "Almanya",
    "Italy": "İtalya", "France": "Fransa", "England": "İngiltere", "Portugal": "Portekiz",
    "Netherlands": "Hollanda", "Belgium": "Belçika", "Croatia": "Hırvatistan", "Greece": "Yunanistan",
    "Hungary": "Macaristan", "Romania": "Romanya", "Wales": "Galler", "Scotland": "İskoçya",
    "Norway": "Norveç", "Sweden": "İsveç", "Denmark": "Danimarka", "Austria": "Avusturya",
    "Switzerland": "İsviçre", "Poland": "Polonya", "Czech Republic": "Çekya", "Iceland": "İzlanda",
    "Montenegro": "Karadağ", "Serbia": "Sırbistan", "Ukraine": "Ukrayna", "Albania": "Arnavutluk",
    "Azerbaijan": "Azerbaycan", "Kosovo": "Kosova", "Brazil": "Brezilya", "Argentina": "Arjantin",
    "USA": "ABD", "Mexico": "Meksika", "Japan": "Japonya", "South Korea": "Güney Kore",
}
