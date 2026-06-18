import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from PIL import Image
import os

# --- WEB SAYFASI AYARLARI ---
st.set_page_config(page_title="Akıllı Yaşlı Asistanı", page_icon="Asistan")
st.title("Akıllı Yaşlı Asistanı")

# --- 1. İVMEÖLÇER VE DÜŞME ALGILAMA SİMÜLASYONU ---
st.markdown("### Düşme Algılayıcı (İvmeölçer)")
st.info("Web tarayıcıları fiziksel sensörlere doğrudan erişemediği için burada ivme değerini manuel olarak simüle ediyoruz. (Normal yerçekimi ivmesi yaklaşık 9.8 m/s²'dir.)")

# Kullanıcıdan ivme değeri al (simülasyon)
# 25 m/s² ve üzerini ani hareket / düşme olarak kabul edeceğiz.
ivme_degeri = st.slider("Anlık İvme Değeri (m/s²)", min_value=0.0, max_value=40.0, value=9.8, step=0.1)
DUSME_ESIGI = 25.0

if ivme_degeri > DUSME_ESIGI:
st.error("DIKKAT: ANI HAREKET VEYA DUSME ALGILANDI!")

# Acil durum sesli uyarısı
try:
st.write("[BILGI] Acil durum uyarısı seslendiriliyor...")
acil_metin = "Dikkat! Düşme algılandı. İyi misiniz? Acil durum kişilerine haber veriliyor."
acil_tts = gTTS(text=acil_metin, lang='tr')
acil_ses = "acil_durum.mp3"
acil_tts.save(acil_ses)

# Sesi otomatik çalmaya çalış (autoplay)
st.audio(acil_ses, format="audio/mp3", autoplay=True)
except Exception as e:
st.error(f"Ses oluşturulamadı: {e}")

# Düşme varsa sistem acil durumdadır, kamerayı açmaya gerek yok. Kodu burada durduruyoruz.
st.stop()

st.markdown("---")

# --- 2. KAMERA VE GÖRÜNTÜ İŞLEME ---
st.markdown("### Ortam Analizi")
st.write("Kameranızı açın ve bir fotoğraf çekin. Yapay zeka etrafı analiz edip size sesli olarak bildirecektir.")

# Render'dan (Environment Variables) API anahtarını alıyoruz
API_KEY = os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
st.warning("Google API Anahtarı bulunamadı! Lütfen Render.com üzerinden 'Environment Variables' kısmına GOOGLE_API_KEY ekleyin.")
st.stop()

# Yapay Zeka Kurulumu
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Tarayıcıdan kamera açma aracı
kamera_goruntusu = st.camera_input("Kamerayı Aç ve Etrafı Çek")

if kamera_goruntusu is not None:
st.info("Görüntü işleniyor, lütfen bekleyin...")

try:
# Görüntüyü oku
img = Image.open(kamera_goruntusu)

talimat = (
"Sen yaşlı ve görme zorluğu çeken birine yardım eden akıllı bir asistan gözlüksün. "
"Şu an kullanıcının önündeki manzarayı görüyorsun. Kullanıcıya önünde ne olduğunu, "
"takılıp düşebileceği bir engel veya dikkat etmesi gereken bir tehlike olup olmadığını "
"kısaca, nazik, güven verici ve çok anlaşılır bir Türkçe ile söyle. Destan yazma, en fazla 2-3 cümle kur."
)

# Resmi Gemini'a gönder
cevap = model.generate_content([img, talimat])
metin_cevap = cevap.text

st.success("Analiz Tamamlandı!")
st.write(f"**Asistanın Yorumu:** {metin_cevap}")

# Metni sese çevir
tts = gTTS(text=metin_cevap, lang='tr')
ses_dosyasi = "cevap.mp3"
tts.save(ses_dosyasi)

# Sesi web sayfasında çal
st.audio(ses_dosyasi, format="audio/mp3", autoplay=True)

except Exception as e:
st.error(f"Bir hata oluştu: {e}")
