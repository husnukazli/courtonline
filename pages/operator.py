import streamlit as st
import pdfplumber
import io
from supabase import create_client, Client

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

st.title("🔐 Yönetim Paneli")
st.markdown("PDF kural kitapçıklarını sayfa sayfa tarayıp veritabanına işleyin.")

if 'admin_giris' not in st.session_state:
    st.session_state.admin_giris = False

if not st.session_state.admin_giris:
    sifre = st.text_input("Admin Şifresi:", type="password")
    if st.button("Giriş Yap", type="primary"):
        if sifre == st.secrets["ADMIN_PASS"]:
            st.session_state.admin_giris = True
            st.rerun()
        else:
            st.error("Hatalı şifre!")
else:
    st.success("Giriş başarılı!")
    st.markdown("---")
    
    kategoriler = [
        "ITF Kuralları", "ATP", "WTA", "Grand Slam", "Tennis Europe", 
        "TTF Ulusal", "Masters", "Tekerlekli Sandalye", "Beach Tennis", "Sık Sorulanlar"
    ]
    secilen_kategori = st.radio("Belgelerin Kategorisini Seçin:", kategoriler, horizontal=True)
    
    yuklenen_dosyalar = st.file_uploader("PDF Belgeleri Seçin", type=["pdf"], accept_multiple_files=True)
    
    if st.button("📤 Belgeleri Yükle ve Sayfa Sayfa İşle", type="primary"):
        if yuklenen_dosyalar:
            toplam_sayfa_kaydi = 0
            
            for dosya in yuklenen_dosyalar:
                dosya_adi = dosya.name
                dosya_verisi = dosya.read()
                
                try:
                    # 1. Supabase Storage'a Yükleme
                    supabase.storage.from_("Belgeler").upload(dosya_adi, dosya_verisi, file_options={"upsert": "true"})
                    dosya_url = supabase.storage.from_("Belgeler").get_public_url(dosya_adi)
                    
                    # 2. pdfplumber ile Sayfa Sayfa Metin Ayıklama
                    with pdfplumber.open(io.BytesIO(dosya_verisi)) as pdf:
                        for sayfa_index, sayfa in enumerate(pdf.pages):
                            metin = sayfa.extract_text()
                            if metin and metin.strip():
                                sayfa_no = sayfa_index + 1
                                
                                # Her sayfayı satır olarak veritabanına kaydediyoruz
                                supabase.table("kural_icerikleri").insert({
                                    "dosya_adi": dosya_adi,
                                    "kategori": secilen_kategori,
                                    "sayfa_no": sayfa_no,
                                    "icerik": metin,
                                    "dosya_url": dosya_url
                                }).execute()
                                
                                toplam_sayfa_kaydi += 1
                                
                    st.success(f"✅ '{dosya_adi}' başarıyla işlendi (Toplam {len(pdf.pages)} sayfa).")
                except Exception as e:
                    st.warning(f"'{dosya_adi}' işlenirken hata oluştu: {e}")
            
            if toplam_sayfa_kaydi > 0:
                st.success(f"🎉 İşlem tamamlandı! Toplam {toplam_sayfa_kaydi} sayfalık veri tabanı kaydı oluşturuldu.")
        else:
            st.warning("Lütfen en az bir PDF seçin.")
