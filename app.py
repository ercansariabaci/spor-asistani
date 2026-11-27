import streamlit as st

st.set_page_config(page_title="Spor Başlangıç Asistanı", page_icon="💪", layout="wide")

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

st.write("")

with st.form("profil_formu"):
    sol, sag = st.columns(2)  # sayfayı iki sütuna böl
    with sol:
        st.subheader("🎯 Hedef ve seviye")
        hedef = st.radio("Hedefin", ["🔥 Kilo verme", "💪 Kas kazanma", "❤️ Genel sağlık"], horizontal=True)
        seviye = st.radio("Seviyen", ["Yeni başlıyorum", "Biraz deneyimliyim", "Düzenliyim"], horizontal=True)
        yas = st.selectbox("Yaş aralığın", ["18 yaş altı", "18-25", "26-35", "36-45", "46+"])
    with sag:
        st.subheader("📅 Program ve bütçe")
        gun = st.slider("Haftada kaç gün?", 1, 7, 3)
        yer = st.radio("Nerede?", ["🏋️ Spor salonu", "🏠 Ev"], horizontal=True)
        butce = st.number_input("Aylık supplement bütçen (TL)", 0, 10000, 500, step=100)
    saglik = st.text_area("🩺 Bilinen sağlık durumun var mı? (yoksa boş bırak)")
    gonder = st.form_submit_button("🚀 Planımı oluştur", use_container_width=True)

if gonder:
    st.success("Form alındı!")
    st.write({"hedef": hedef, "seviye": seviye, "yaş": yas, "gün": gun,
              "yer": yer, "bütçe": butce, "sağlık": saglik or "Yok"})
