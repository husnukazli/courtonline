import streamlit as st
from supabase import create_client, Client

# Supabase Bağlantısı
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

st.title("🔐 Yönetim Paneli")
st.markdown("Veritabanına yeni kural kitapçıkları ve evraklar yükleyin.")

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
    
    # Kategori Seçimi
    kategoriler = [
        "ITF Kuralları", "ATP", "WTA", "Grand Slam", "Tennis Europe", 
        "TTF Ulusal", "Masters", "Tekerlekli Sandalye", "Beach Tennis", "Sık Sorulanlar"
    ]
    secilen_kategori = st.radio("Belgelerin Kategorisini Seçin:", kategoriler, horizontal=True)
    
    # Çoklu Dosya Yükleme Alanı (accept_multiple_files=True)
    yuklenen_dosyalar = st.file_uploader("PDF Belgeleri Seçin (Çoklu seçebilirsiniz)", type=["pdf"], accept_multiple_files=True)
    
    if st.button("📤 Seçilen Belgeleri Supabase'e Yükle", type="primary"):
        if yuklenen_dosyalar:
            basarili_sayisi = 0
            
            for yuklenen_dosya in yuklenen_dosyalar:
                dosya_adi = yuklenen_dosya.name
                
                try:
                    # 1. Supabase Storage'a Yükleme (Bucket adı: 'Belgeler')
                    dosya_verisi = yuklenen_dosya.read()
                    supabase.storage.from_("Belgeler").upload(dosya_adi, dosya_verisi)
                    
                    # 2. Public URL'i Alma
                    dosya_url = supabase.storage.from_("Belgeler").get_public_url(dosya_adi)
                    
                    # 3. Veritabanı Tablosuna (kural_dosyalari) Kaydetme
                    supabase.table("kural_dosyalari").insert({
                        "dosya_adi": dosya_adi,
                        "kategori": secilen_kategori,
                        "dosya_url": dosya_url
                    }).execute()
                    
                    basarili_sayisi += 1
                except Exception as e:
                    # Aynı dosya önceden varsa veya yükleme hatası olursa kullanıcıya gösterelim
                    st.warning(f"'{dosya_adi}' yüklenirken hata oluştu: {e}")
            
            if basarili_sayisi > 0:
                st.success(f"✅ Toplam {basarili_sayisi} adet belge başarıyla '{secilen_kategori}' kategorisine yüklendi!")
        else:
            st.warning("Lütfen en az bir PDF dosyası seçin.")
