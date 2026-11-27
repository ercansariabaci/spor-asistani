import os
import re
import time

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from hesaplamalar import makro_hesapla
from supplementler import supplement_sec
from prompts import SISTEM_PROMPTU, kullanici_mesaji_olustur


st.set_page_config(page_title="Spor Başlangıç Asistanı", page_icon="💪", layout="wide")

# .env dosyasındaki anahtarı oku (anahtar kodda yazmıyor!)
load_dotenv()
api_anahtari = os.getenv("GEMINI_API_KEY")
if not api_anahtari:
    st.error("GEMINI_API_KEY bulunamadı. Proje klasöründe .env dosyası var mı?")
    st.stop()

# timeout: Google 3 dk içinde cevap vermezse beklemeyi bırak (milisaniye cinsinden).
# Bu süre Google'a da "en geç bu kadar sürede bitir" diye iletiliyor; uzun planlar için geniş tutuyoruz.
istemci = genai.Client(api_key=api_anahtari, http_options=types.HttpOptions(timeout=180_000))


@st.cache_resource  # sonucu hafızada tut, her tıklamada Google'a tekrar sorma
def model_adaylari(_istemci):
    """Kullanılabilir Flash modellerini en iyiden yedeğe doğru sıralı döndürür."""
    adlar = [m.name.removeprefix("models/") for m in _istemci.models.list()
             if "generateContent" in (m.supported_actions or [])]
    flashlar = [a for a in adlar if "flash" in a and not any(
        k in a for k in ("preview", "exp", "latest", "image", "tts", "audio", "live"))]
    normal = sorted([a for a in flashlar if "lite" not in a], reverse=True)
    lite = sorted([a for a in flashlar if "lite" in a], reverse=True)
    adaylar = (normal + lite) or adlar[:1]
    tercih = os.getenv("GEMINI_MODEL")  # .env'de bir model yazıldıysa listenin başına koy
    if tercih:
        adaylar = [tercih] + [a for a in adaylar if a != tercih]
    return adaylar


def akis_baslat(mesaj, durum, deneme_sayisi=2):
    """Cevabı parça parça (stream) almaya başlar. Modelleri sırayla dener; meşgulse bekleyip tekrar dener.
    İlk parça gelene kadar bekler (hatalar genelde burada çıkar), sonra (ilk_parça, akış, model) döndürür.
    durum: ekranda ne olduğunu yazdığımız kutu."""
    son_hata = None
    dusuk_dusunme = True  # modelin "düşünme" süresini kısaltıp daha hızlı cevap almak için
    for model in MODELLER[:3]:              # en fazla 3 farklı model
        for deneme in range(deneme_sayisi):  # her modelde 2 deneme
            durum.write(f"⏳ {model} deneniyor (deneme {deneme + 1})...")
            baslangic = time.time()
            ayarlar = types.GenerateContentConfig(
                system_instruction=SISTEM_PROMPTU,
                temperature=0.7,
                thinking_config=types.ThinkingConfig(thinking_level="LOW") if dusuk_dusunme else None,
            )
            try:
                akis = iter(istemci.models.generate_content_stream(model=model, contents=mesaj, config=ayarlar))
                ilk_parca = next(akis)  # ilk parçayı bekle
                durum.write(f"✅ {model} {time.time() - baslangic:.0f} saniyede yazmaya başladı.")
                return ilk_parca, akis, model
            except Exception as hata:
                son_hata = hata
                metin = str(hata)
                durum.write(f"⚠️ {model}: {metin[:120]}")
                if "400" in metin and "think" in metin.lower():  # model bu ayarı desteklemiyorsa ayarsız dene
                    dusuk_dusunme = False
                    continue
                if any(k in metin for k in ("503", "504", "429", "UNAVAILABLE", "DEADLINE", "timed out", "Timeout")):
                    time.sleep(2 ** deneme * 2)  # 2 sn, sonra 4 sn
                    continue
                raise  # başka bir hataysa (ör. anahtar yanlış) hemen bildir
    raise son_hata


try:
    MODELLER = model_adaylari(istemci)
except Exception as hata:
    st.error(f"Model listesi alınamadı. API anahtarını kontrol et. Hata: {hata}")
    st.stop()

# Üstteki renkli karşılama kutusu: HTML (iskelet) + CSS (görünüm)
st.markdown("""
<style>
.hero {padding: 2rem; border-radius: 16px; color: white;
       background: linear-gradient(135deg, #FF4B6E, #FF9F43);}
.hero h1 {margin: 0;}
.hero p {margin: .5rem 0 0; font-size: 1.1rem;}
</style>
<div class="hero">
  <h1>💪 Spor Başlangıç Asistanı</h1>
  <p>Birkaç soruda sana özel antrenman, beslenme ve supplement planı.</p>
</div>
""", unsafe_allow_html=True)

# Sol kenar paneli
with st.sidebar:
    st.header("Nasıl çalışır?")
    st.markdown("1️⃣ Formu doldur\n\n2️⃣ Yapay zekâ planını hazırlasın\n\n3️⃣ Bugün başla!")
    st.caption("⚠️ Bu bir sağlık tavsiyesi değildir.")
    st.caption("🔒 Formdaki bilgiler plan hazırlamak için Google Gemini'ye gönderilir ve kaydedilmez. "
               "Kimliğini belli edecek bilgi yazma.")
    st.caption(f"🤖 Model: {MODELLER[0]}")

st.write("")

with st.form("profil_formu"):
    sol, sag = st.columns(2)  # sayfayı iki sütuna böl
    with sol:
        st.subheader("🎯 Hedef ve seviye")
        hedef = st.radio("Hedefin", ["🔥 Kilo verme", "💪 Kas kazanma", "❤️ Genel sağlık"], horizontal=True)
        seviye = st.radio("Seviyen", ["Yeni başlıyorum", "Biraz deneyimliyim", "Düzenliyim"], horizontal=True)
        yas = st.selectbox("Yaş aralığın", ["18 yaş altı", "18-25", "26-35", "36-45", "46+"], index=1)
        cinsiyet = st.radio("Cinsiyet", ["Erkek", "Kadın"], horizontal=True)
        k1, k2 = st.columns(2)
        boy = k1.number_input("Boy (cm)", 140, 220, 175)
        kilo = k2.number_input("Kilo (kg)", 40, 200, 70)
    with sag:
        st.subheader("📅 Program ve bütçe")
        gun = st.slider("Haftada kaç gün?", 1, 7, 3)
        yer = st.radio("Nerede?", ["🏋️ Spor salonu", "🏠 Ev"], horizontal=True)
        butce = st.number_input("Aylık supplement bütçen (TL)", 0, 10000, 500, step=100)
    saglik = st.text_area("🩺 Bilinen sağlık durumun var mı? (yoksa boş bırak)")
    gonder = st.form_submit_button("🚀 Planımı oluştur", use_container_width=True)

if gonder:
    profil = {"hedef": hedef, "seviye": seviye, "yaş": yas, "cinsiyet": cinsiyet,
              "boy": boy, "kilo": kilo, "gün": gun, "yer": yer, "bütçe": butce,
              "sağlık": saglik.strip() or "Yok"}

    makrolar = makro_hesapla(profil)  # kesin hesap kodla, yapay zekâyla değil
    if not makrolar:
        st.info("ℹ️ 18 yaş altı ya da bir sağlık durumu seçtiğin için supplement ve kalori hedefi verilmeyecek; "
                "bunun yerine bir doktora/diyetisyene yönlendireceğiz.")
    if makrolar:
        st.subheader("📊 Günlük hedeflerin")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Kalori", f'{makrolar["hedef_kalori"]:.0f} kcal')
        m2.metric("Protein", f'{makrolar["protein_g"]} g')
        m3.metric("Karbonhidrat", f'{makrolar["karbonhidrat_g"]} g')
        m4.metric("Yağ", f'{makrolar["yag_g"]} g')
        st.caption(f'Faz: {makrolar["faz"]} · Koruma kalorin yaklaşık {makrolar["koruma_kalorisi"]:.0f} kcal')

    supplementler = supplement_sec(profil, makrolar)  # bütçeyi kod doldurur
    if supplementler:
        st.subheader("💊 Bütçene göre supplement seçimi")
        st.dataframe(
            [{"Ürün": u["ad"], "Kanıt": u["kanit"], "Aylık (TL, tahmini)": u["aylik_tl"]} for u in supplementler],
            hide_index=True, use_container_width=True)
        toplam = sum(u["aylik_tl"] for u in supplementler)
        st.caption(f"Toplam ~{toplam} TL / bütçe {butce} TL (%{toplam * 100 // max(butce, 1)} kullanıldı)")

    akis = None
    with st.status("Plan hazırlanıyor... 🏃", expanded=True) as durum:
        try:
            ilk_parca, akis, kullanilan_model = akis_baslat(
                kullanici_mesaji_olustur(profil, makrolar, supplementler), durum)
            durum.update(label="Plan yazılıyor ✍️", state="complete", expanded=False)
        except Exception as hata:
            durum.update(label="Plan oluşturulamadı", state="error")
            st.error(f"Biraz sonra tekrar dene. Hata: {hata}")

    if akis:
        def _hepsi(ilk, kalan):
            """İlk parçayı ve kalan parçaların metinlerini sırayla verir."""
            if ilk.text:
                yield ilk.text
            for parca in kalan:
                if parca.text:
                    yield parca.text

        def parcalar():
            """Gelen parçaların metnini sırayla verir (generator)."""
            for parca in _hepsi(ilk_parca, akis):
                # Gemini bazen büyük parçalar gönderiyor; kelime kelime vererek akışı görünür kılıyoruz.
                # re.split boşlukları da ayrı parça olarak korur, metin bozulmaz.
                for kelime in re.split(r"(\s+)", parca):
                    yield kelime
                    if kelime.strip():
                        time.sleep(0.004)  # kelime başına çok kısa bekleme: daktilo etkisi

        try:
            st.write_stream(parcalar())  # metni geldikçe ekrana yazar
            st.caption(f"Bu planı {kullanilan_model} hazırladı.")
        except Exception as hata:
            st.error(f"Plan yazılırken bağlantı koptu, tekrar dene. Hata: {hata}")

    # Yapay zekâ unutsa bile uyarı her zaman görünsün diye kodla da ekliyoruz
    st.warning("⚠️ Bu bir sağlık tavsiyesi değildir. Yeni bir programa başlamadan önce bir uzmana danışın.")
