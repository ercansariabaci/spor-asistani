"""Supplement kataloğu ve bütçeye göre seçim.

Neden kodda? Yapay zekâ bütçeyi doldurmayı "unutabiliyor" ya da hep aynı 2-3 ürünü öneriyor.
Hangi ürünlerin seçileceğine KOD karar verir, yapay zekâ sadece açıklar.

Fiyatlar aylık maliyettir (TL). Kaynak: proteinocean.com, 27.11.2026.
Hesap: paket fiyatı / servis sayısı * 30 (pre-workout: ayda ~15 kullanım).
"""

SEVIYE_SIRASI = {"Yeni başlıyorum": 0, "Biraz deneyimliyim": 1, "Düzenliyim": 2}

# Her ürün bir sözlük. Liste sırası = önem sırası (üstteki önce seçilir).
KATALOG = [
    {"ad": "Kreatin monohidrat", "hedefler": ["Kas kazanma", "Kilo verme", "Genel sağlık"],
     "seviye": 0, "aylik_tl": 180, "kanit": "Çok güçlü", "sadece_salon": False},
    {"ad": "Whey protein (konsantre)", "grup": "protein tozu", "yarim_olabilir": True, "hedefler": ["Kas kazanma", "Kilo verme"],
     "seviye": 0, "aylik_tl": 2060, "kanit": "Çok güçlü", "sadece_salon": False},
    {"ad": "D3 vitamini (+K2)", "hedefler": ["Kas kazanma", "Kilo verme", "Genel sağlık"],
     "seviye": 0, "aylik_tl": 150, "kanit": "Güçlü (eksiklikte)", "sadece_salon": False},
    {"ad": "Omega-3 (balık yağı, yüksek EPA/DHA)", "hedefler": ["Kas kazanma", "Kilo verme", "Genel sağlık"],
     "seviye": 0, "aylik_tl": 300, "kanit": "Güçlü", "sadece_salon": False},
    {"ad": "Magnezyum (bisglisinat)", "hedefler": ["Kas kazanma", "Genel sağlık", "Kilo verme"],
     "seviye": 0, "aylik_tl": 200, "kanit": "Orta", "sadece_salon": False},
    {"ad": "Multivitamin", "hedefler": ["Kilo verme", "Genel sağlık"],
     "seviye": 0, "aylik_tl": 330, "kanit": "Orta (diyet yetersizse)", "sadece_salon": False},
    {"ad": "Prebiyotik lif (sindirim ve tokluk)", "hedefler": ["Kilo verme", "Genel sağlık"],
     "seviye": 0, "aylik_tl": 375, "kanit": "Orta", "sadece_salon": False},
    {"ad": "Protein bar (pratik ara öğün, ~15 adet/ay)", "hedefler": ["Kas kazanma", "Kilo verme"],
     "seviye": 0, "aylik_tl": 1250, "kanit": "Besin (protein kaynağı)", "sadece_salon": False},
    {"ad": "Pre-workout (içeriği açık, ölçülü kafeinli)", "grup": "uyarıcı", "hedefler": ["Kas kazanma", "Kilo verme"],
     "seviye": 1, "aylik_tl": 450, "kanit": "Güçlü (kafein)", "sadece_salon": True},
    {"ad": "Kafein tableti (pre-workout'un ucuz alternatifi)", "grup": "uyarıcı", "hedefler": ["Kas kazanma", "Kilo verme"],
     "seviye": 1, "aylik_tl": 120, "kanit": "Güçlü", "sadece_salon": True},
    {"ad": "Beta-alanin", "hedefler": ["Kas kazanma"],
     "seviye": 1, "aylik_tl": 350, "kanit": "Orta-güçlü (yüksek tekrarlı setler)", "sadece_salon": True},
    {"ad": "Sitrülin malat", "hedefler": ["Kas kazanma"],
     "seviye": 2, "aylik_tl": 450, "kanit": "Orta", "sadece_salon": True},
    {"ad": "Elektrolit tozu", "hedefler": ["Kas kazanma", "Kilo verme", "Genel sağlık"],
     "seviye": 1, "aylik_tl": 400, "kanit": "Orta (yoğun terleyenler)", "sadece_salon": False},
    {"ad": "Pirinç kreması (pratik karbonhidrat, bulk için)", "hedefler": ["Kas kazanma"],
     "seviye": 1, "aylik_tl": 600, "kanit": "Besin (karbonhidrat kaynağı)", "sadece_salon": False},
    {"ad": "Pancar kökü (nitrat)", "hedefler": ["Kas kazanma", "Genel sağlık"],
     "seviye": 2, "aylik_tl": 450, "kanit": "Orta (dayanıklılık)", "sadece_salon": True},
    {"ad": "Kolajen + C vitamini (eklem/tendon)", "hedefler": ["Kas kazanma", "Genel sağlık"],
     "seviye": 2, "aylik_tl": 800, "kanit": "Orta-zayıf", "sadece_salon": False},
    {"ad": "Kazein protein (gece proteini)", "hedefler": ["Kas kazanma"],
     "seviye": 2, "aylik_tl": 2060, "kanit": "Orta", "sadece_salon": False}, 
    {"ad": "Çinko", "hedefler": ["Kilo verme", "Genel sağlık"],
     "seviye": 0, "aylik_tl": 120, "kanit": "Orta (diyet yetersizse)", "sadece_salon": False},
    {"ad": "B12 vitamini (az et tüketenler için)", "hedefler": ["Genel sağlık", "Kilo verme"],
     "seviye": 0, "aylik_tl": 150, "kanit": "Güçlü (eksiklikte)", "sadece_salon": False},
    # Alternatif proteinler: sadece özel ihtiyaçta (vegan, laktoz). Formda bu soru olmadığı için
    # otomatik seçilmiyorlar; Sürüm 2'deki supplement planlayıcısında kullanıcı kendisi seçecek.
    {"ad": "Bitkisel protein (bezelye, süt ürünü tüketmeyenler için)", "grup": "protein tozu", "otomatik_secilmez": True, "hedefler": ["Kas kazanma", "Kilo verme"],
     "seviye": 0, "aylik_tl": 1120, "kanit": "Güçlü", "sadece_salon": False},
    {"ad": "Whey izolat (laktoz hassasiyeti olanlar için)", "grup": "protein tozu", "otomatik_secilmez": True, "hedefler": ["Kas kazanma", "Kilo verme"],
     "seviye": 0, "aylik_tl": 3750, "kanit": "Çok güçlü", "sadece_salon": False},
]


HEDEF_KULLANIM = 0.85  # bütçenin en az %85'ini kullanmaya çalış


def _uygun_mu(urun, hedef, seviye, salon, hedefe_bak=True):
    """Ürün bu kullanıcıya önerilebilir mi?"""
    if urun.get("otomatik_secilmez"):           # özel ihtiyaç ürünü, otomatik önerme
        return False
    if hedefe_bak and hedef not in urun["hedefler"]:
        return False
    return seviye >= urun["seviye"] and (salon or not urun["sadece_salon"])


def _doldur(adaylar, secilenler, kalan):
    """Adayları sırayla dener; sığan ve grubu tekrar etmeyen ürünü ekler. Kalan parayı döndürür."""
    for urun in adaylar:
        if urun in secilenler:
            continue
        secilen_gruplar = [u.get("grup") for u in secilenler]
        if urun.get("grup") and urun["grup"] in secilen_gruplar:  # ikinci protein tozu alma
            continue
        if urun["aylik_tl"] <= kalan:
            secilenler.append(urun)
            kalan -= urun["aylik_tl"]
        elif urun.get("yarim_olabilir") and urun["aylik_tl"] // 2 <= kalan:
            # Tam paket sığmıyorsa gün aşırı kullanım (yarı maliyet) dene
            yarim = dict(urun, ad=urun["ad"] + " – gün aşırı (~15 servis/ay)", aylik_tl=urun["aylik_tl"] // 2)
            secilenler.append(yarim)
            kalan -= yarim["aylik_tl"]
    return kalan


def supplement_sec(profil, makrolar):
    """Bütçeyi önem sırasına göre doldurur. Uygun değilse boş liste döner.

    1. tur: Sadece hedefe uygun ürünler (whey tam sığmazsa gün aşırı kullanımla).
    2. tur: Bütçenin %85'i dolmadıysa hedef şartını gevşetip seviyeye uygun diğer ürünlere bakar.
    3. tur: Hâlâ dolmadıysa whey konsantreyi izolata yükseltir.
    4. tur: Hâlâ dolmadıysa bir üst seviyenin (hedefe uygun) ürünlerini açar.
    Kanıtı olan uygun ürünler biterse %85'in altında kalabilir; bunu ekranda açıklıyoruz.
    """
    if makrolar is None:          # 18 yaş altı veya sağlık durumu: supplement yok
        return []
    hedef = next(h for h in ("Kilo verme", "Kas kazanma", "Genel sağlık") if h in profil["hedef"])
    seviye = SEVIYE_SIRASI[profil["seviye"]]
    salon = "salon" in profil["yer"].lower()
    butce = profil["bütçe"]

    secilenler = []
    kalan = _doldur([u for u in KATALOG if _uygun_mu(u, hedef, seviye, salon)], secilenler, butce)

    def yeterli():
        return butce == 0 or (butce - kalan) / butce >= HEDEF_KULLANIM

    # 2. tur: Hedef şartını gevşet (seviye, salon ve güvenlik şartları aynen geçerli)
    if not yeterli():
        kalan = _doldur([u for u in KATALOG if _uygun_mu(u, hedef, seviye, salon, hedefe_bak=False)],
                        secilenler, kalan)

    # 3. tur: Bütçe yüksekse whey konsantreyi izolata yükselt (daha saf, daha kolay sindirilir)
    if not yeterli():
        for i, urun in enumerate(secilenler):
            if urun["ad"] == "Whey protein (konsantre)":
                izolat = next(u for u in KATALOG if u["ad"].startswith("Whey izolat"))
                fark = izolat["aylik_tl"] - urun["aylik_tl"]
                if fark <= kalan:
                    secilenler[i] = dict(izolat, ad="Whey izolat (bütçen yettiği için konsantre yerine)")
                    kalan -= fark

    # 4. tur: Hâlâ dolmadıysa bir üst seviyenin ürünlerini de aç
    if not yeterli() and seviye < 2:
        kalan = _doldur([u for u in KATALOG if _uygun_mu(u, hedef, seviye + 1, salon)],
                        secilenler, kalan)
    return secilenler
