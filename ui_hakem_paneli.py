import streamlit as st

def hakem_panelini_ciz():
    st.title("🎾 Başhakem Dijital Asistanı")
    st.markdown("Sahada hızlı, doğru ve net kararlar için güncel talimatlarda arama yapın.")
    st.markdown("---")

    # Hangi kategorinin seçili olduğunu hafızada tutuyoruz
    if 'aktif_kategori' not in st.session_state:
        st.session_state.aktif_kategori = "Kategori Seçilmedi"

    st.subheader("Kategori Seçin")
    
    # Kalıcı Aksiyon Butonları (Açılır menü kullanılmamıştır)
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
    
    # Tüm talimatlarda arama için vurgulu premium/pro buton
    if st.button("🌐 Tüm Talimatlarda Aynı Anda Ara (Pro)", type="primary", use_container_width=True):
        st.session_state.aktif_kategori = "Tüm Talimatlar"

    st.markdown("---")
    
    # Hakeme nerede arama yaptığını gösteren uyarı alanı
    if st.session_state.aktif_kategori == "Kategori Seçilmedi":
        st.warning("Lütfen yukarıdan arama yapmak istediğiniz talimatı seçin.")
    else:
        st.success(f"📍 **Aktif Kategori:** {st.session_state.aktif_kategori}")

        # Sohbet / Arama Kutusu
        mesaj = st.chat_input("Örn: 14 yaşta top değişimi kuralı nedir?")
        
        if mesaj:
            # Kullanıcının sorusunu ekrana basıyoruz
            with st.chat_message("user"):
                st.write(mesaj)
                
            # Yapay Zeka cevap alanı (Şimdilik yer tutucu)
            with st.chat_message("assistant"):
                st.write(f"*{st.session_state.aktif_kategori} veritabanı taranıyor...*")
                st.info("Buraya Supabase'den çekilen belgelere göre Gemini 1.5 Flash'tan dönen cevap gelecek.")
