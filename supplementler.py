"""Supplement kataloğu ve bütçeye göre seçim.

Neden kodda? Yapay zekâ bütçeyi doldurmayı "unutabiliyor" ya da hep aynı 2-3 ürünü öneriyor.
Hangi ürünlerin seçileceğine KOD karar verir, yapay zekâ sadece açıklar.

Fiyatlar TAHMİNİ aylık maliyettir (TL, Kasım 2026). Güvenilir sitelerden bakıp kendin güncelle!
"""

SEVIYE_SIRASI = {"Yeni başlıyorum": 0, "Biraz deneyimliyim": 1, "Düzenliyim": 2}

# Her ürün bir sözlük. Liste sırası = önem sırası (üstteki önce seçilir).
KATALOG = [
    {"ad": "Kreatin monohidrat", "hedefler": ["Kas kazanma", "Kilo verme", "Genel sağlık"],
     "seviye": 0, "aylik_tl": 400, "kanit": "Çok güçlü", "sadece_salon": False},
    {"ad": "Whey protein (konsantre)", "hedefler": ["Kas kazanma", "Kilo verme"],
     "seviye": 0, "aylik_tl": 1800, "kanit": "Çok güçlü", "sadece_salon": False},
    {"ad": "D3 vitamini (+K2)", "hedefler": ["Kas kazanma", "Kilo verme", "Genel sağlık"],
     "seviye": 0, "aylik_tl": 150, "kanit": "Güçlü (eksiklikte)", "sadece_salon": False},
    {"ad": "Omega-3 (balık yağı, yüksek EPA/DHA)", "hedefler": ["Kas kazanma", "Kilo verme", "Genel sağlık"],
     "seviye": 0, "aylik_tl": 350, "kanit": "Güçlü", "sadece_salon": False},
    {"ad": "Magnezyum (bisglisinat)", "hedefler": ["Kas kazanma", "Genel sağlık", "Kilo verme"],
     "seviye": 0, "aylik_tl": 250, "kanit": "Orta", "sadece_salon": False},
    {"ad": "Multivitamin", "hedefler": ["Kilo verme", "Genel sağlık"],
     "seviye": 0, "aylik_tl": 250, "kanit": "Orta (diyet yetersizse)", "sadece_salon": False},
    {"ad": "Pre-workout (içeriği açık, ölçülü kafeinli)", "hedefler": ["Kas kazanma", "Kilo verme"],
     "seviye": 1, "aylik_tl": 700, "kanit": "Güçlü (kafein)", "sadece_salon": True},
    {"ad": "Beta-alanin", "hedefler": ["Kas kazanma"],
     "seviye": 1, "aylik_tl": 350, "kanit": "Orta-güçlü (yüksek tekrarlı setler)", "sadece_salon": True},
    {"ad": "Sitrülin malat", "hedefler": ["Kas kazanma"],
     "seviye": 2, "aylik_tl": 450, "kanit": "Orta", "sadece_salon": True},
    {"ad": "Elektrolit tozu", "hedefler": ["Kas kazanma", "Kilo verme", "Genel sağlık"],
     "seviye": 1, "aylik_tl": 300, "kanit": "Orta (yoğun terleyenler)", "sadece_salon": False},
    {"ad": "Pancar kökü (nitrat)", "hedefler": ["Kas kazanma", "Genel sağlık"],
     "seviye": 2, "aylik_tl": 450, "kanit": "Orta (dayanıklılık)", "sadece_salon": True},
    {"ad": "Kolajen + C vitamini (eklem/tendon)", "hedefler": ["Kas kazanma", "Genel sağlık"],
     "seviye": 2, "aylik_tl": 600, "kanit": "Orta-zayıf", "sadece_salon": False},
    {"ad": "Kazein protein (gece proteini)", "hedefler": ["Kas kazanma"],
     "seviye": 2, "aylik_tl": 1800, "kanit": "Orta", "sadece_salon": False},
]


def supplement_sec(profil, makrolar):
    """Bütçeyi önem sırasına göre doldurur. Uygun değilse boş liste döner."""
    if makrolar is None:          # 18 yaş altı veya sağlık durumu: supplement yok
        return []
    hedef = next(h for h in ("Kilo verme", "Kas kazanma", "Genel sağlık") if h in profil["hedef"])
    seviye = SEVIYE_SIRASI[profil["seviye"]]
    salon = "salon" in profil["yer"].lower()

    kalan = profil["bütçe"]
    secilenler = []
    for urun in KATALOG:
        uygun = (hedef in urun["hedefler"]
                 and seviye >= urun["seviye"]
                 and (salon or not urun["sadece_salon"]))
        if uygun and urun["aylik_tl"] <= kalan:   # sığıyorsa ekle, sığmıyorsa sıradakine bak
            secilenler.append(urun)
            kalan -= urun["aylik_tl"]
    return secilenler
