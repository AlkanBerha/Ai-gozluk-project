import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from PIL import Image
import os
import uuid

# --- WEB SAYFASI AYARLARI ---
st.set_page_config(page_title="Akıllı Yaşlı Asistanı", page_icon="Asistan")
st.title("Akıllı Yaşlı Asistanı")

# --- 1. İVMEÖLÇER VE DÜŞME ALGILAMA SİMÜLASYONU ---
st.markdown("### Düşme Algılayıcı (İvmeölçer)")
st.info("Web tarayıcıları fiziksel sensörlere doğrudan erişemediği için burada ivme değerini manuel olarak simüle ediyoruz. (Normal yerçekimi ivmesi yaklaşık 9.8 m/s²'dir.)")

ivme_degeri = st.slider(
    "Anlık İvme Değeri (m/s²)",
    min_value=0.0,
    max_value=40.0,
    value=9.8,
    step=0.1
)

DUSME_ESIGI = 25.0

if ivme_degeri > DUSME_ESIGI:
    st.error("DIKKAT: ANI HAREKET VEYA DUSME ALGILANDI!")

    try:
        st.write("Acil durum uyarısı seslendiriliyor...")
        acil_metin = "Dikkat! Düşme algılandı. İyi misiniz? Acil durum kişilerine haber veriliyor."
        acil_tts = gTTS(text=acil_metin, lang='tr')

        acil_ses = f"acil_durum_{uuid.uuid4()}.mp3"
        acil_tts.save(acil_ses)

        st.audio(acil_ses, format="audio/mp3", autoplay=True)

    except Exception as e:
        st.error(f"Ses oluşturulamadı: {e}")

    st.stop()

st.markdown("---")

# --- 2. KAMERA VE GÖRÜNTÜ İŞLEME ---
st.markdown("### Ortam Analizi")
st.write("Kameranızı açın ve bir fotoğraf çekin. Yapay zeka etrafı analiz edip size sesli olarak bildirecektir.")

API_KEY = os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
    st.warning("Google API Anahtarı bulunamadı. Lütfen Environment Variables kısmına GOOGLE_API_KEY ekleyin.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

kamera_goruntusu = st.camera_input("Kamerayı Aç ve Etrafı Çek")

if kamera_goruntusu is not None:
    st.info("Görüntü işleniyor, lütfen bekleyin...")

    try:
        img = Image.open(kamera_goruntusu)

        talimat = (
            "Sen yaşlı ve görme zorluğu çeken birine yardım eden akıllı bir asistan gözlüksün. "
            "Şu an kullanıcının önündeki manzarayı görüyorsun. Kullanıcıya önünde ne olduğunu, "
            "takılıp düşebileceği bir engel veya dikkat etmesi gereken bir tehlike olup olmadığını "
            "kısaca, nazik, güven verici ve çok anlaşılır bir Türkçe ile söyle. "
            "En fazla 2-3 cümle kur."
        )

        cevap = model.generate_content([img, talimat])

        metin_cevap = ""
        if hasattr(cevap, "text") and cevap.text:
            metin_cevap = cevap.text
        else:
            metin_cevap = "Görüntü analiz edilemedi. Lütfen tekrar deneyin."

        st.success("Analiz tamamlandı.")
        st.write(f"Asistanın Yorumu: {metin_cevap}")

        tts = gTTS(text=metin_cevap, lang='tr')
        ses_dosyasi = f"cevap_{uuid.uuid4()}.mp3"
        tts.save(ses_dosyasi)

        st.audio(ses_dosyasi, format="audio/mp3", autoplay=True)

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
