import streamlit as st
import pandas as pd
import re
import urllib.parse
from supabase import create_client, Client

TENNIS_SOZLugu = {
    "top": ["ball", "balls"],
    "top değişimi": ["ball change", "change of balls"],
    "mola": ["break", "rest", "toilet break", "medical time-out", "mto", "rest period", "changeover", "heat rule"],
    "servis": ["serve", "service", "let", "fault", "service fault", "second serve", "foot fault"],
    "itiraz": ["appeal", "challenge", "review", "hawk-eye", "electronic review"],
    "uzatma": ["tie-break", "tiebreak", "match tie-break", "set tie-break", "super tie-break"],
    "hakem": ["umpire", "referee", "supervisor", "chair umpire", "roving umpire", "chief", "line umpire"],
    "diskalifiye": ["default", "disqualification", "code violation", "expulsion"],
    "kod ihlali": ["code violation", "penalty", "warnings", "point penalty", "game penalty", "unsportsmanlike"],
    "hakaret": ["verbal abuse", "obscenity", "profanity"],
    "suistimal": ["abuse", "ball abuse", "racket abuse", "equipment abuse", "physical abuse"],
    "hava": ["weather", "suspension", "interruption", "heat rule", "bad weather", "inclement weather"],
    "tuvalet": ["toilet break", "restroom", "change of attire"],
    "sağlık": ["medical", "injury", "treatment", "bleed time", "evaluation", "trainer", "doctor"],
    "ceza": ["penalty", "fine", "suspension", "point penalty", "default", "time penalty", "code violation"],
    "çekilme": ["retirement", "withdrawal", "walkover", "w/o", "ret"],
    "hükmen": ["walkover", "default", "w/o", "bye"],
    "kura": ["draw", "seeding", "qualifying", "lucky loser", "alternate", "withdrawal", "wild card"],
    "koçluk": ["coaching", "communication", "instruction"],
    "gecikme": ["time violation", "delay", "continuous play", "warm-up", "starting time", "punctuality"],
    "seyirci": ["spectator", "crowd", "interruption", "noise", "behavior"],
    "forma": ["attire", "clothing", "shoes", "commercial identification", "logos", "white clothing", "dress code"],
    "katılım": ["sign-in", "entry", "withdrawal", "acceptance list", "deadline", "entry fee"],
    "ısınma": ["warm-up", "practice", "hitting session"]
}

def supabase_baglantisi_kur():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def hakem_panelini_ciz():
    st.title("🎾 Başhakem Dijital Asistanı")
    st.markdown("Talimatlarda arama yapın veya kütüphane indeksini inceleyin.")
    st.markdown("---")

    try:
        supabase = supabase_baglantisi_kur()
    except Exception as e:
        st.error("⚠️ Supabase bağlantı ayarları (Secrets) yüklenemedi. Lütfen Streamlit Cloud Secrets bölümünü kontrol edin.")
        return

    sekme_arama, sekme_indeks = st.tabs(["🔍 Kural Arama", "📚 Belge İndeksi & Kütüphane"])

    with sekme_arama:
        if 'aktif_kategori' not in st.session_state:
            st.session_state.aktif_kategori = "Kategori Seçilmedi"

        st.subheader("Kategori Seçin")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🏆 ITF Kuralları", use_container_width=True):
                st.session_state.aktif_kategori = "ITF Kuralları"
            if st.button("🌟 ITF Junior", use_container_width=True):
                st.session_state.aktif_kategori = "ITF Junior"
                
        with col2:
            if st.button("🌍 ATP", use_container_width=True):
                st.session_state.aktif_kategori = "ATP"
            if st.button("👑 WTA", use_container_width=True):
                st.session_state.aktif_kategori = "WTA"
                
        with col3:
            if st.button("🏟️ Grand Slam", use_container_width=True):
                st.session_state.aktif_kategori = "Grand Slam"
            if st.button("🇪🇺 Tennis Europe", use_container_width=True):
                st.session_state.aktif_kategori = "Tennis Europe"
            if st.button("🇹🇷 TTF Ulusal", use_container_width=True):
                st.session_state.aktif_kategori = "TTF Ulusal"
                
        with col4:
            if st.button("🏅 Masters", use_container_width=True):
                st.session_state.aktif_kategori = "Masters"
            if st.button("♿ Tekerlekli S.", use_container_width=True):
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

            aranan_kelime = st.chat_input("Örn: mola, top değişimi, coaching, default...")
            
            if aranan_kelime:
                with st.chat_message("user"):
                    st.write(aranan_kelime)
                    
                with st.chat_message("assistant"):
                    with st.spinner("Genişletilmiş sözlük ve veritabanı taranıyor..."):
                        try:
                            aranan_lower = aranan_kelime.lower().strip()
                            aranacak_terimler = [aranan_lower]
                            
                            for tr_key, en_list in TENNIS_SOZLugu.items():
                                if tr_key in aranan_lower or aranan_lower in tr_key:
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
                                    sayfa_no = kayit.get('sayfa_no', 1)
                                    st.markdown(f"📄 **Belge:** {kayit['dosya_adi']} *({kayit['kategori']}) | 📌 Sayfa: {sayfa_no}*")
                                    
                                    # PDF URL'ini al
                                    pdf_url = kayit['dosya_url']
                                    if isinstance(pdf_url, dict):
                                        pdf_url = pdf_url.get('publicUrl', '')
                                    
                                    metin = kayit['icerik']
                                    bul_terim = aranan_lower if aranan_lower in metin.lower() else aranacak_terimler[0]
                                    
                                    if pdf_url:
                                        # URL'in sonuna #page=X&search=Y ekleme hilesi
                                        url_kodlu_terim = urllib.parse.quote(bul_terim)
                                        hedefli_url = f"{pdf_url}#page={sayfa_no}&search={url_kodlu_terim}"
                                        
                                        st.markdown(f"🔗 **[Orijinal PDF'i Doğrudan {sayfa_no}. Sayfada Aç ve Kelimeyi Bul]({hedefli_url})**")
                                    
                                    idx = metin.lower().find(bul_terim)
                                    
                                    if idx != -1:
                                        baslangic = max(0, idx - 120)
                                        bitis = min(len(metin), idx + 350)
                                        kesit = metin[baslangic:bitis].replace("\n", " ")
                                        
                                        pattern = re.compile(re.escape(bul_terim), re.IGNORECASE)
                                        vurgulu_kesit = pattern.sub(
                                            lambda m: f'<span style="background-color: #39ff14; color: #000000; font-weight: bold; padding: 2px 4px; border-radius: 3px;">{m.group(0)}</span>', 
                                            kesit
                                        )
                                        
                                        st.markdown(f"💡 **İlgili Bağlam:**<br>...{vurgulu_kesit}...", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"💡 **İlgili Bağlam:**<br>...{metin[:300]}...", unsafe_allow_html=True)
                                        
                                    st.markdown("---")
                            else:
                                st.warning(f"'{aranan_kelime}' (veya genişletilmiş sözlük karşılıkları) seçilen kategoride bulunamadı.")
                        except Exception as e:
                            st.error(f"Arama sırasında hata oluştu: {e}")

    with sekme_indeks:
        st.subheader("📚 Kayıtlı Belgeler Kütüphanesi")
        st.markdown("Sistemdeki tüm kural kitapçıklarını filtreleyebilir, inceleyebilir veya indirebilirsiniz.")
        
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
                            doc_url = row['dosya_url']
                            if isinstance(doc_url, dict):
                                doc_url = doc_url.get('publicUrl', '')
                            if doc_url:
                                st.markdown(f"🔗 [Aç / İndir]({doc_url})")
                        st.markdown("---")
                        
                else:
                    kategoriler_listesi = df_unique["kategori"].unique().tolist()
                    if kategoriler_listesi:
                        secilen_grup_kategori = st.selectbox(
                            "Görüntülenecek Kategoriyi Seçin:", 
                            kategoriler_listesi
                        )
                        
                        df_filtered = df_unique[df_unique["kategori"] == secilen_grup_kategori].sort_values(by="dosya_adi")
                        st.markdown("---")
                        if not df_filtered.empty:
                            for idx, row in df_filtered.iterrows():
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    st.markdown(f"**{row['dosya_adi']}**")
                                with col2:
                                    doc_url = row['dosya_url']
                                    if isinstance(doc_url, dict):
                                        doc_url = doc_url.get('publicUrl', '')
                                    if doc_url:
                                        st.markdown(f"🔗 [Aç / İndir]({doc_url})")
                                st.markdown("---")
                        else:
                            st.info("Bu kategoride kayıtlı belge bulunmuyor.")
            else:
                st.warning("Veritabanında henüz kayıtlı belge bulunmuyor.")
        except Exception as e:
            st.error(f"Arşiv yüklenirken hata oluştu: {e}")
