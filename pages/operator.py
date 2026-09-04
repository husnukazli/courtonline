import streamlit as st
import pdfplumber
import io
from supabase import create_client, Client

# Supabase Bağlantısı
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

st.title("🔐 Yönetim Paneli")
st.markdown("PDF kural kitapçıklarını yükleyin; metinler otomatik olarak taranıp veritabanına işlenecektir.")

# Şifre Kontrolü
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
    
    if st.button("📤 Belgeleri Yükle ve Metinleri İşle", type="primary"):
        if yuklenen_dosyalar:
            basarili = 0
            
            for dosya in yuklenen_dosyalar:
                dosya_adi = dosya.name
                dosya_verisi = dosya.read()
                
                try:
                    # 1. Supabase Storage'a Yükleme
                    supabase.storage.from_("Belgeler").upload(dosya_adi, dosya_verisi, file_options={"upsert": "true"})
                    dosya_url = supabase.storage.from_("Belgeler").get_public_url(dosya_adi)
                    
                    # 2. pdfplumber ile PDF içindeki TÜM metinleri ayıkla
                    tum_metin = ""
                    with pdfplumber.open(io.BytesIO(dosya_verisi)) as pdf:
                        for sayfa in pdf.pages:
                            metin = sayfa.extract_text()
                            if metin:
                                tum_metin += metin + "\n"
                    
                    # 3. Veritabanına (kural_icerikleri) kaydet
                    supabase.table("kural_icerikleri").insert({
                        "dosya_adi": dosya_adi,
                        "kategori": secilen_kategori,
                        "icerik": tum_metin,
                        "dosya_url": dosya_url
                    }).execute()
                    
                    basarili += 1
                except Exception as e:
                    st.warning(f"'{dosya_adi}' işlenirken hata oluştu: {e}")
            
            if basarili > 0:
                st.success(f"✅ Toplam {basarili} belge başarıyla işlendi ve veritabanına kaydedildi!")
        else:
            st.warning("Lütfen en az bir PDF seçin.")
