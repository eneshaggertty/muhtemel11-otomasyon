"""Ayarlar. Değiştirmek istediğin her şey burada."""

HANDLE = "@muhtemel11onbir"
SLOGAN = "Futbolda son dakika burada"
TZ = "Europe/Istanbul"

# API-Football lig ID'leri
SUPER_LIG = 203
BIRINCI_LIG = 204
SEZON = 2026  # 2026/27 sezonu

LIG_ADLARI = {SUPER_LIG: "Trendyol Süper Lig", BIRINCI_LIG: "Trendyol 1. Lig"}

# Türkiye A Milli Takımı (API-Football takım ID'si)
TURKIYE_ID = 777

# Ne paylaşılsın? (True/False)
PAYLAS = {
    "program": True,            # maç günü öğlen: günün maçları (Süper Lig + 1. Lig, carousel)
    "ilk11_superlig": True,     # Süper Lig: kadrolar açıklanınca ilk 11 (2 takım, carousel)
    "ilk11_birincilig": False,  # 1. Lig ilk 11 (günde 9-10 maç = çok post; kapalı)
    "sonuc_superlig": True,     # Süper Lig: her maç bitince ayrı sonuç kartı
    "sonuc_birincilig": True,   # 1. Lig: günün tüm maçları bitince tek toplu kart
    "puan_durumu": True,        # haftanın tüm maçları bitince puan durumu
    "milli_takim": True,        # Türkiye: muhtemel 11 (maçtan 1 gün önce), ilk 11, sonuç
}

PROGRAM_SAATI = 12           # günün maçları bu saatten sonra paylaşılır
MUHTEMEL11_SAATI = 20        # milli maçtan bir gün önce bu saatten sonra
ILK11_PENCERE_DK = 75        # maça bu kadar dakika kala kadroları kontrol etmeye başla
GRID_TERS = True             # ilk 11 kartında sağ/sol kanat ters çıkarsa False yap

HASHTAGS = {
    SUPER_LIG: "#süperlig #trendyolsüperlig #futbol #türkfutbolu #muhtemel11",
    BIRINCI_LIG: "#1lig #trendyol1lig #futbol #türkfutbolu #muhtemel11",
    "milli": "#bizimçocuklar #türkiye #millitakım #futbol #muhtemel11",
}

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
