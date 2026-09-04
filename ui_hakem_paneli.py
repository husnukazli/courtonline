import streamlit as st
import pandas as pd
import re
from supabase import create_client, Client

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

TENNIS_SOZLugu = {
    "top": ["ball", "balls"],
    "top değişimi": ["ball change", "change of balls"],
    "mola": ["break", "rest", "toilet break", "medical time-out", "mto", "rest period"],
    "servis": ["serve", "service", "let", "fault"],
    "itiraz": ["appeal", "challenge", "review", "hawk-eye"],
    "uzatma": ["tie-break", "tiebreak"],
    "hakem": ["umpire", "referee", "supervisor", "chair umpire"],
    "diskalifiye": ["default", "disqualification", "code violation"],
    "kod ihlali": ["code violation", "penalty", "warnings"],
    "hava": ["weather", "suspension", "interruption", "heat rule", "bad weather"],
    "tuvalet": ["toilet break", "restroom"],
    "sağlık": ["medical", "injury", "treatment"]
}

def hakem_panelini_ciz():
    st.title("🎾 Başhakem Dijital Asistanı")
    st.markdown("Talimatlarda arama yapın veya kütüphane indeksini inceleyin.")
    st.markdown("---")

    # Üst Sekmeler (Arama Ekranı ile Belge İndeksi Arasında Geçiş)
    sekme_arama, sekme_indeks = st.tabs(["🔍 Kural Arama", "📚 Belge İndeksi & Kütüphane"])

    with sekme_arama:
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

            aranan_kelime = st.chat_input("Örn: mola, top değişimi, toilet break...")
            
            if aranan_kelime:
                with st.chat_message("user"):
                    st.write(aranan_kelime)
                    
                with st.chat_message("assistant"):
                    with st.spinner("Veritabanı ve yerleşik sözlük taranıyor..."):
                        try:
                            aranan_lower = aranan_kelime.lower().strip()
                            aranacak_terimler = [aranan_lower]
                            
                            for tr_key, en_list in TENNIS_SOZLugu.items():
                                if tr_key in aranan_lower:
                                    aranacak_terimler.extend(en_list)
                            
                            sorgu = supabase.table("kural_icerikleri").select("dosya_adi, kategori, sayfa_no, dosya_url, icerik")
                            
                            if st.session_state.aktif_kategori != "Tüm Talimatlar":
                                sorgu = sorgu.eq("kategori", st.session_state.aktif_kategori)
                            
                            filtre_parcalari = [f"icerik.ilike.%{terim}%" for terim in aranacak_terimler]
                            sorgu = sorgu.or_(",".join(filtre_parcalari))
                            sonuclar = sorgu.execute().data
                            
                            if sonuclar:
                                st.success(f"Bulunan ilgili sayfa sayısı: {len(sonuclar)}")
                                
                                for kayit in sonuclar:
                                    sayfa_bilgi = f" | 📌 Sayfa: {kayit.get('sayfa_no', 'Bilinmiyor')}" if kayit.get('sayfa_no') else ""
                                    st.markdown(f"📄 **Belge:** {kayit['dosya_adi']} *({kayit['kategori']}){sayfa_bilgi}*")
                                    st.markdown(f"🔗 [Orijinal PDF'i Aç / İndir]({kayit['dosya_url']})")
                                    
                                    # Bağlam ve Aranan Kelimeyi Vurgulama (Highlight)
                                    metin = kayit['icerik']
                                    bul_terim = aranan_lower if aranan_lower in metin.lower() else aranacak_terimler[0]
                                    idx = metin.lower().find(bul_terim)
                                    
                                    if idx != -1:
                                        baslangic = max(0, idx - 120)
                                        bitis = min(len(metin), idx + 350)
                                        kesit = metin[baslangic:bitis].replace("\n", " ")
                                        
                                        # Metin içinde aranan kelimeyi otomatik **kalın** yapıyoruz ki gözden kaçmasın
                                        pattern = re.compile(re.escape(bul_terim), re.IGNORECASE)
                                        vurgulu_kesit = pattern.sub(lambda m: f"**🔍 {m.group(0)} 🔍**", kesit)
                                        
                                        st.info(f"💡 **İlgili Bağlam:**\n\n...{vurgulu_kesit}...")
                                    else:
                                        st.info(f"💡 **İlgili Bağlam:**\n\n...{metin[:300]}...")
                                        
                                    st.markdown("---")
                            else:
                                st.warning(f"'{aranan_kelime}' (veya sözlük karşılıkları) seçilen kategoride bulunamadı.")
                        except Exception as e:
                            st.error(f"Arama sırasında hata oluştu: {e}")

    with sekme_indeks:
        st.subheader("📚 Kayıtlı Belgeler Kütüphanesi")
        st.markdown("Sistemdeki tüm kural kitapçıklarını filtreleyebilir, inceleyebilir veya indirebilirsiniz.")
        
        # Filtreleme ve Sıralama Seçenekleri (Hakem Paneli için salt okunur)
        siralama_turu = st.radio(
            "Sıralama ve Filtreleme Modu:", 
            ["🔤 Alfabetik Sıralama (Tümü)", "📂 Kategoriye Göre Sıralama"],
            horizontal=True
        )
        
        try:
            response = supabase.table("kural_icerikleri").select("dosya_adi, kategori, dosya_url").execute()
            if response.data:
                df = pd.DataFrame(response.data)
                df_unique = df.drop_duplicates(subset=["dosya_adi"]).reset_index(drop=True)
                
                if siralama_turu == "🔤 Alfabetik Sıralama (Tümü)":
                    df_unique = df_unique.sort_values(by="dosya_adi", ascending=True)
                    st.markdown("---")
                    for idx, row in df_unique.iterrows():
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            st.markdown(f"**{row['dosya_adi']}**")
                        with col2:
                            st.caption(f"📂 {row['kategori']}")
                        with col3:
                            st.markdown(f"[🔗 Aç / İndir]({row['dosya_url']})")
                        st.markdown("---")
                        
                else: # Kategoriye Göre Sıralama
                    secilen_grup_kategori = st.selectbox(
                        "Görüntülenecek Kategoriyi Seçin:", 
                        df_unique["kategori"].unique().tolist()
                    )
                    
                    df_filtered = df_unique[df_unique["kategori"] == secilen_grup_kategori].sort_values(by="dosya_adi")
                    st.markdown("---")
                    if not df_filtered.empty:
                        for idx, row in df_filtered.iterrows():
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.markdown(f"**{row['dosya_adi']}**")
                            with col2:
                                st.markdown(f"[🔗 Aç / İndir]({row['dosya_url']})")
                            st.markdown("---")
                    else:
                        st.info("Bu kategoride kayıtlı belge bulunmuyor.")
            else:
                st.warning("Veritabanında henüz kayıtlı belge bulunmuyor.")
        except Exception as e:
            st.error(f"Arşiv yüklenirken hata oluştu: {e}")
