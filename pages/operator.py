import streamlit as st
import pdfplumber
import io
import pandas as pd
from supabase import create_client, Client

# Supabase Bağlantısı
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

st.title("🔐 Yönetim Paneli")
st.markdown("PDF kural kitapçıklarını yükleyin ve mevcut arşivinizi yönetin.")

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
    
    # Sekmeler (1. Belge Yükleme | 2. Belge Arşivi ve İndeks)
    sekme1, sekme2 = st.tabs(["📤 Yeni Belge Yükle", "📚 Alfabetik Belge Arşivi (İndeks)"])
    
    with sekme1:
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
                
    with sekme2:
        st.subheader("📋 Yüklenmiş Belgeler İndeksi")
        st.markdown("Sistemde kayıtlı tüm PDF'ler alfabetik olarak aşağıda listelenmiştir.")
        
        try:
            # Veritabanından tüm benzersiz dosyaları ve kategorilerini çekelim
            response = supabase.table("kural_icerikleri").select("dosya_adi, kategori, dosya_url").execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                # Benzersiz dosya adlarını alıp alfabetik sıralayalım
                df_unique = df.drop_duplicates(subset=["dosya_adi"]).sort_values(by="dosya_adi", ascending=True).reset_index(drop=True)
                
                st.info(f"Toplam Yüklenen Benzersiz Belge Sayısı: **{len(df_unique)}**")
                
                # Tablo Görünümü ve İndirme Linkleri
                for idx, row in df_unique.iterrows():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"**{idx+1}. {row['dosya_adi']}**")
                    with col2:
                        st.caption(f"📂 Kategori: {row['kategori']}")
                    with col3:
                        st.markdown(f"[🔗 İndir / Aç]({row['dosya_url']})")
                    st.markdown("---")
            else:
                st.warning("Henüz veritabanına yüklenmiş bir belge bulunmuyor.")
        except Exception as e:
            st.error(f"Arşiv yüklenirken bir hata oluştu: {e}")
