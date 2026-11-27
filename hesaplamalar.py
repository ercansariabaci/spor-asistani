"""Kalori ve makro (protein, karbonhidrat, yağ) hesapları.

Neden yapay zekâya bırakmıyoruz? Dil modelleri matematikte hata yapabilir.
Kesin sonuç gereken hesapları kodla yapıp, sonucu yapay zekâya hazır veriyoruz.
"""

YAS_ORTALAMASI = {"18-25": 22, "26-35": 30, "36-45": 40, "46+": 50}

# Haftalık antrenman gününe göre aktivite çarpanı
def aktivite_carpani(gun):
    if gun <= 2:
        return 1.375
    if gun <= 4:
        return 1.55
    return 1.725

# Hedefe göre: (faz adı, kalori çarpanı, kg başına protein)
HEDEF_AYARLARI = {
    "Kilo verme": ("Cut (yağ yakımı, %20 kalori açığı)", 0.80, 2.0),
    "Kas kazanma": ("Lean bulk (temiz kas kazanımı, %10 kalori fazlası)", 1.10, 1.8),
    "Genel sağlık": ("Koruma (kilonu korumak)", 1.00, 1.6),
}


def makro_hesapla(profil):
    """Profilden günlük kalori ve makro hedeflerini hesaplar.
    18 yaş altı ya da sağlık durumu varsa None döner (uzmana yönlendireceğiz)."""
    if profil["yaş"] not in YAS_ORTALAMASI or profil["sağlık"] != "Yok":
        return None

    kilo, boy = profil["kilo"], profil["boy"]
    yas = YAS_ORTALAMASI[profil["yaş"]]

    # Mifflin-St Jeor formülü: vücudun dinlenirken harcadığı kalori (BMR)
    bmr = 10 * kilo + 6.25 * boy - 5 * yas
    bmr += 5 if profil["cinsiyet"] == "Erkek" else -161

    koruma = bmr * aktivite_carpani(profil["gün"])  # günlük toplam harcama (TDEE)

    # Hedef metni emoji içerebilir ("🔥 Kilo verme"), anahtar kelimeyi arıyoruz
    anahtar = next(h for h in HEDEF_AYARLARI if h in profil["hedef"])
    faz, carpan, protein_kg = HEDEF_AYARLARI[anahtar]

    kalori = koruma * carpan
    protein = protein_kg * kilo          # 1 g protein = 4 kcal
    yag = 0.8 * kilo                     # 1 g yağ = 9 kcal
    karb = (kalori - protein * 4 - yag * 9) / 4  # kalan kalori karbonhidrattan

    return {
        "faz": faz,
        "koruma_kalorisi": round(koruma, -1),
        "hedef_kalori": round(kalori, -1),
        "protein_g": round(protein),
        "karbonhidrat_g": max(round(karb), 0),
        "yag_g": round(yag),
    }
