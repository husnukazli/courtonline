import streamlit as st
from supabase import create_client, Client

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# Yerleşik Tenis Sözlüğü (Türkçe <-> İngilizce Kural Terimleri Eşlemesi)
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
    st.markdown("Talimatlarda Türkçe veya İngilizce terimlerle kelime bazlı arama yapın.")
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

        aranan_kelime = st.chat_input("Örn: mola, top değişimi, toilet break...")
        
        if aranan_kelime:
            with st.chat_message("user"):
                st.write(aranan_kelime)
                
            with st.chat_message("assistant"):
                with st.spinner("Veritabanı ve yerleşik sözlük taranıyor..."):
                    try:
                        # 1. Yerleşik sözlük kontrolü (Türkçe kelimenin İngilizce karşılıklarını bul)
                        aranan_lower = aranan_kelime.lower().strip()
                        aranacak_terimler = [aranan_lower]
                        
                        for tr_key, en_list in TENNIS_SOZLugu.items():
                            if tr_key in aranan_lower:
                                aranacak_terimler.extend(en_list)
                        
                        # 2. Supabase Sorgu Hazırlığı (Çoklu kelime / sözlük desteği)
                        sorgu = supabase.table("kural_icerikleri").select("dosya_adi, kategori, sayfa_no, dosya_url, icerik")
                        
                        if st.session_state.aktif_kategori != "Tüm Talimatlar":
                            sorgu = sorgu.eq("kategori", st.session_state.aktif_kategori)
                        
                        # Sözlükten gelen tüm terimleri (Türkçe ve İngilizce) OR ile bağlıyoruz
                        filtre_parcalari = []
                        for terim in aranacak_terimler:
                            filtre_parcalari.append(f"icerik.ilike.%{terim}%")
                        
                        sorgu = sorgu.or_(",".join(filtre_parcalari))
                        sonuclar = sorgu.execute().data
                        
                        if sonuclar:
                            st.success(f"Bulunan ilgili sayfa sayısı: {len(sonuclar)}")
                            
                            # Her bir sonuç için sayfa ve bağlam detayını basalım
                            for kayit in sonuclar:
                                sayfa_bilgi = f" | 📌 Sayfa: {kayit.get('sayfa_no', 'Bilinmiyor')}" if kayit.get('sayfa_no') else ""
                                st.markdown(f"📄 **Belge:** {kayit['dosya_adi']} *({kayit['kategori']}){sayfa_bilgi}*")
                                st.markdown(f"🔗 [İlgili Sayfayı / PDF'i Aç]({kayit['dosya_url']})")
                                
                                # Bağlam (Metin kesiti)
                                metin = kayit['icerik']
                                bul_terim = aranan_lower if aranan_lower in metin.lower() else aranacak_terimler[0]
                                idx = metin.lower().find(bul_terim)
                                
                                if idx != -1:
                                    baslangic = max(0, idx - 120)
                                    bitis = min(len(metin), idx + 350)
                                    kesit = metin[baslangic:bitis].replace("\n", " ")
                                    st.info(f"💡 **İlgili Bağlam:**\n\n...{kesit}...")
                                else:
                                    # Alternatif olarak ilk 300 karakteri verelim
                                    st.info(f"💡 **İlgili Bağlam:**\n\n...{metin[:300]}...")
                                    
                                st.markdown("---")
                        else:
                            st.warning(f"'{aranan_kelime}' (veya sözlük karşılıkları) seçilen kategoride bulunamadı.")
                    except Exception as e:
                        st.error(f"Arama sırasında hata oluştu: {e}")
