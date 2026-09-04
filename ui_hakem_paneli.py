import streamlit as st
from supabase import create_client, Client

# Supabase Bağlantısı
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

def hakem_panelini_ciz():
    st.title("🎾 Başhakem Dijital Asistanı")
    st.markdown("Sahada hızlı karar için talimatlarda kelime bazlı arama yapın.")
    st.markdown("---")

    if 'aktif_kategori' not in st.session_state:
        st.session_state.aktif_kategori = "Kategori Seçilmedi"

    st.subheader("Kategori Seçin")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏆 ITF Kuralları", use_container_width=True):
            st.session_state.aktif_kategori = "ITF Kuralları"
        if st.button("🌍 ATP", use_container_width=True):
            st.session_state.aktif_kategori = "ATP"
        if st.button("👑 WTA", use_container_width=True):
            st.session_state.aktif_kategori = "WTA"
        if st.button("🏟️ Grand Slam", use_container_width=True):
            st.session_state.aktif_kategori = "Grand Slam"
            
    with col2:
        if st.button("🇪🇺 Tennis Europe", use_container_width=True):
            st.session_state.aktif_kategori = "Tennis Europe"
        if st.button("🇹🇷 TTF Ulusal", use_container_width=True):
            st.session_state.aktif_kategori = "TTF Ulusal"
        if st.button("🏅 Masters", use_container_width=True):
            st.session_state.aktif_kategori = "Masters"
            
    with col3:
        if st.button("♿ Tekerlekli Sandalye", use_container_width=True):
            st.session_state.aktif_kategori = "Tekerlekli Sandalye"
        if st.button("🏖️ Beach Tennis", use_container_width=True):
            st.session_state.aktif_kategori = "Beach Tennis"
        if st.button("📌 Sık Sorulanlar", use_container_width=True):
            st.session_state.aktif_kategori = "Sık Sorulanlar"

    st.markdown("---")
    
    if st.button("🌐 Tüm Talimatlarda Aynı Anda Ara (Pro)", type="primary", use_container_width=True):
        st.session_state.aktif_kategori = "Tüm Talimatlar"

    st.markdown("---")
    
    if st.session_state.aktif_kategori == "Kategori Seçilmedi":
        st.warning("Lütfen yukarıdan arama yapmak istediğiniz talimatı seçin.")
    else:
        st.success(f"📍 **Aktif Kategori / Arama Alanı:** {st.session_state.aktif_kategori}")

        # Sohbet / Arama Kutusu (Sonuçlar doğrudan buraya gelecek)
        aranan_kelime = st.chat_input("Örn: top değişimi, mola, hakem kararı...")
        
        if aranan_kelime:
            with st.chat_message("user"):
                st.write(aranan_kelime)
                
            with st.chat_message("assistant"):
                with st.spinner("Supabase veritabanında taranıyor..."):
                    try:
                        # Supabase Sorgusu (Esnek ve Büyük/Küçük Harf Duyarsız - ILIKE)
                        sorgu = supabase.table("kural_icerikleri").select("dosya_adi, kategori, dosya_url, icerik")
                        
                        # Eğer "Tüm Talimatlar" seçilmediyse kategoriye göre filtrele
                        if st.session_state.aktif_kategori != "Tüm Talimatlar":
                            sorgu = sorgu.eq("kategori", st.session_state.aktif_kategori)
                        
                        # Kelimeyi esnek aratmak için % ekliyoruz
                        sonuclar = sorgu.ilike("icerik", f"%{aranan_kelime}%").execute().data
                        
                        if sonuclar:
                            st.success(f"Bulunan ilgili belge sayısı: {len(sonuclar)}")
                            for kayit in sonuclar:
                                st.markdown(f"📄 **Belge:** {kayit['dosya_adi']} *({kayit['kategori']})*")
                                st.markdown(f"🔗 [Orijinal PDF Dosyasını Aç]({kayit['dosya_url']})")
                                
                                # Metin içinden aranan kelimenin geçtiği kısmı kesip önizleme verelim
                                metin = kayit['icerik']
                                idx = metin.lower().find(aranan_kelime.lower())
                                if idx != -1:
                                    baslangic = max(0, idx - 100)
                                    bitis = min(len(metin), idx + 300)
                                    kesit = metin[baslangic:bitis]
                                    st.info(f"💡 **İlgili Kesit:**\n\n...{kesit}...")
                                st.markdown("---")
                        else:
                            st.warning(f"'{aranan_kelime}' kelimesi seçilen kategorideki belgelerde bulunamadı.")
                    except Exception as e:
                        st.error(f"Arama sırasında hata oluştu: {e}")
