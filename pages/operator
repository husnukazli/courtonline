import streamlit as st
from supabase import create_client

# Supabase Bağlantısı
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

st.title("🔐 Yönetim Paneli")

# Şifre Kontrolü (Oturum Yönetimi)
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
    st.success("Giriş başarılı! Belge yükleyebilirsiniz.")
    st.markdown("---")
    
    # Kategori Seçimi (Kalıcı ve Açık Arayüz)
    kategoriler = ["ITF Kuralları", "Tennis Europe", "TTF Ulusal", "Tekerlekli Sandalye", "Beach Tennis", "Sık Sorulanlar"]
    secilen_kategori = st.radio("Belgenin Kategorisini Seçin:", kategoriler, horizontal=True)
    
    # Dosya Yükleme Alanı
    yuklenen_dosya = st.file_uploader("PDF Belgesi Seçin", type=["pdf"])
    
    if st.button("📤 Belgeyi Supabase'e Yükle", type="primary"):
        if yuklenen_dosya is not None:
            dosya_adi = yuklenen_dosya.name
            
            # 1. Supabase Storage'a Yükleme
            dosya_verisi = yuklenen_dosya.read()
            supabase.storage.from_("belgeler").upload(dosya_adi, dosya_verisi)
            
            # 2. Public URL'i Alma
            dosya_url = supabase.storage.from_("belgeler").get_public_url(dosya_adi)
            
            # 3. Veritabanı Tablosuna (kural_dosyalari) Kaydetme
            supabase.table("kural_dosyalari").insert({
                "dosya_adi": dosya_adi,
                "kategori": secilen_kategori,
                "dosya_url": dosya_url
            }).execute()
            
            st.success(f"✅ {dosya_adi} başarıyla {secilen_kategori} kategorisine yüklendi!")
        else:
            st.warning("Lütfen bir PDF dosyası seçin.")
