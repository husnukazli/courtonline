import streamlit as st
import pandas as pd
import re
import urllib.parse
from supabase import create_client, Client
import google.generativeai as genai

# Sözlüğü yeni oluşturduğumuz dosyadan içe aktarıyoruz
from sozluk import TENNIS_SOZLugu

def supabase_baglantisi_kur():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

# Gemini API Yapılandırması
def yapay_zeka_ayarla():
    try:
        genai.configure(api_key=st.secrets["gemini"]["api_key"])
        # API versiyonuyla tam uyumlu ve uzun metinleri anında okuyan 'flash' modelini kullanıyoruz
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        st.error("Gemini API anahtarı ayarlanırken bir sorun oluştu.")
        return None

def hakem_panelini_ciz():
    st.title("Başhakem Dijital Asistanı")
    st.markdown("Kural arayın, kütüphaneyi inceleyin veya **Yapay Zekaya olayı anlatıp çözdürün.**")
    st.markdown("---")

    try:
        supabase = supabase_baglantisi_kur()
    except Exception as e:
        st.error("Supabase bağlantı ayarları yüklenemedi. Lütfen Secrets bölümünü kontrol edin.")
        return
        
    ai_model = yapay_zeka_ayarla()

    # 3 Sekmeli Yapı: Arama, Yapay Zeka, İndeks
    sekme_arama, sekme_ai, sekme_indeks = st.tabs(["🔍 Kural Arama", "🤖 AI Olay Çözücü", "📚 Belge İndeksi"])

    # ------------------ 1. KLASİK ARAMA SEKMESİ ------------------
    with sekme_arama:
        if 'aktif_kategori' not in st.session_state:
            st.session_state.aktif_kategori = "Kategori Seçilmedi"

        st.subheader("Kategori Seçin")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("ITF Kuralları", key="btn1", use_container_width=True): st.session_state.aktif_kategori = "ITF Kuralları"
            if st.button("Men's WTT", key="btn2", use_container_width=True): st.session_state.aktif_kategori = "Men's WTT"
            if st.button("Women's WTT", key="btn3", use_container_width=True): st.session_state.aktif_kategori = "Women's WTT"
            if st.button("WTT Juniors", key="btn4", use_container_width=True): st.session_state.aktif_kategori = "WTT Juniors"
                
        with col2:
            if st.button("WTT Masters", key="btn5", use_container_width=True): st.session_state.aktif_kategori = "WTT Masters"
            if st.button("Wheelchair Tour", key="btn6", use_container_width=True): st.session_state.aktif_kategori = "Wheelchair Tour"
            if st.button("Beach Tennis", key="btn7", use_container_width=True): st.session_state.aktif_kategori = "Beach Tennis"
            if st.button("Tennis Europe", key="btn8", use_container_width=True): st.session_state.aktif_kategori = "Tennis Europe"
                
        with col3:
            if st.button("ATP", key="btn9", use_container_width=True): st.session_state.aktif_kategori = "ATP"
            if st.button("WTA", key="btn10", use_container_width=True): st.session_state.aktif_kategori = "WTA"
            if st.button("Grand Slam", key="btn11", use_container_width=True): st.session_state.aktif_kategori = "Grand Slam"
                
        with col4:
            if st.button("TTF Ulusal", key="btn12", use_container_width=True): st.session_state.aktif_kategori = "TTF Ulusal"
            if st.button("Ulusal Diğer", key="btn13", use_container_width=True): st.session_state.aktif_kategori = "Ulusal Diğer"
            if st.button("Sık Sorulanlar", key="btn14", use_container_width=True): st.session_state.aktif_kategori = "Sık Sorulanlar"

        st.markdown("---")
        if st.button("Tüm Talimatlarda Aynı Anda Ara (Pro)", type="primary", use_container_width=True):
            st.session_state.aktif_kategori = "Tüm Talimatlar"
        st.markdown("---")
        
        if st.session_state.aktif_kategori == "Kategori Seçilmedi":
            st.warning("Lütfen arama yapmak istediğiniz talimatı seçin.")
        else:
            st.success(f"**Aktif Talimat:** {st.session_state.aktif_kategori}")
            
            aranan_kelime = st.chat_input("Aranacak kelimeyi yazın (veya mikrofona dokunun)...")
            
            if aranan_kelime:
                with st.chat_message("user"):
                    st.write(aranan_kelime)
                    
                with st.chat_message("assistant"):
                    with st.spinner("Veritabanı taranıyor..."):
                        try:
                            aranan_ilk = aranan_kelime.lower().strip()
                            aranan_ilk = re.sub(r'\s+', ' ', aranan_ilk)
                            temel_terimler = {aranan_ilk}
                            
                            # Katı Sözlük Eşleştirmesi
                            for tr_key, en_list in TENNIS_SOZLugu.items():
                                if aranan_ilk == tr_key or aranan_ilk in en_list:
                                    temel_terimler.add(tr_key)
                                    temel_terimler.update(en_list)

                            aranacak_terimler = set()
                            for terim in temel_terimler:
                                aranacak_terimler.add(terim)
                                if ' ' in terim:
                                    aranacak_terimler.add(terim.replace(' ', ''))
                                    aranacak_terimler.add(terim.replace(' ', '-'))
                                if '-' in terim:
                                    aranacak_terimler.add(terim.replace('-', ''))
                                    aranacak_terimler.add(terim.replace('-', ' '))
                                    
                            aranacak_terimler_listesi = list(aranacak_terimler)
                            
                            sorgu = supabase.table("kural_icerikleri").select("dosya_adi, kategori, sayfa_no, dosya_url, icerik")
                            if st.session_state.aktif_kategori != "Tüm Talimatlar":
                                sorgu = sorgu.eq("kategori", st.session_state.aktif_kategori)
                            
                            filtre_parcalari = [f"icerik.ilike.%{terim}%" for terim in aranacak_terimler_listesi]
                            sorgu = sorgu.or_(",".join(filtre_parcalari))
                            
                            sonuclar = sorgu.execute().data
                            
                            if sonuclar:
                                st.success(f"Bulunan ilgili sayfa sayısı: {len(sonuclar)}")
                                for kayit in sonuclar:
                                    sayfa_no = kayit.get('sayfa_no', 1)
                                    st.markdown(f"**Belge:** {kayit['dosya_adi']} *({kayit['kategori']}) | Sayfa: {sayfa_no}*")
                                    
                                    pdf_url = kayit['dosya_url']
                                    if isinstance(pdf_url, dict): pdf_url = pdf_url.get('publicUrl', '')
                                    
                                    metin = kayit['icerik']
                                    metin_lower = metin.lower()
                                    
                                    bulunan_varyasyon = aranacak_terimler_listesi[0]
                                    for varyasyon in aranacak_terimler_listesi:
                                        if varyasyon in metin_lower:
                                            bulunan_varyasyon = varyasyon
                                            break
                                    
                                    if pdf_url:
                                        url_kodlu_terim = urllib.parse.quote(f'"{bulunan_varyasyon}"')
                                        hedefli_url = f"{pdf_url}?render=true#page={sayfa_no}&search={url_kodlu_terim}"
                                        st.markdown(
                                            f'''<a href="{hedefli_url}" target="_blank" 
                                            style="background-color: #2e3034; color: #39ff14; padding: 8px 12px; border-radius: 6px; text-decoration: none; display: inline-block; margin-bottom: 10px; font-weight: bold; border: 1px solid #39ff14;">
                                            ↗️ {sayfa_no}. Sayfayı Aç ve "{bulunan_varyasyon}" Kelimesini Vurgula
                                            </a>''', 
                                            unsafe_allow_html=True
                                        )
                                    
                                    idx = metin_lower.find(bulunan_varyasyon)
                                    if idx != -1:
                                        baslangic = max(0, idx - 120)
                                        bitis = min(len(metin), idx + 350)
                                        kesit = metin[baslangic:bitis].replace("\n", " ")
                                        pattern = re.compile(re.escape(bulunan_varyasyon), re.IGNORECASE)
                                        vurgulu_kesit = pattern.sub(lambda m: f'<span style="background-color: #39ff14; color: #000000; font-weight: bold; padding: 2px 4px; border-radius: 3px;">{m.group(0)}</span>', kesit)
                                        st.markdown(f"**İlgili Bağlam:**<br>...{vurgulu_kesit}...", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"**İlgili Bağlam:**<br>...{metin[:300]}...", unsafe_allow_html=True)
                                        
                                    st.markdown("---")
                            else:
                                st.warning("Bu kategoride sonuç bulunamadı.")
                        except Exception as e:
                            st.error(f"Arama sırasında hata oluştu: {e}")

    # ------------------ 2. YAPAY ZEKA SEKMESİ ------------------
    with sekme_ai:
        st.subheader("🤖 Yapay Zeka Başhakem Yardımcısı")
        st.markdown("Sahada gerçekleşen olayı anlatın, yapay zeka ilgili kural kitapçığını okuyup kararı size söylesin.")
        
        if st.session_state.aktif_kategori == "Kategori Seçilmedi" or st.session_state.aktif_kategori == "Tüm Talimatlar":
            st.warning("Lütfen yukarıdaki Arama sekmesinden okutmak istediğiniz tek bir Kategori seçin.")
        elif not ai_model:
            st.warning("Gemini API hazır değil. Lütfen ayarlarınızı kontrol edin.")
        else:
            st.info(f"Yapay Zeka şu an **{st.session_state.aktif_kategori}** kurallarını baz alarak cevap verecek.")
            
            olay_metni = st.chat_input("Olayı anlatın (Örn: Oyuncu top toplayıcıya bağırdı, ne yapmalıyım?)...", key="ai_input")
            
            if olay_metni:
                with st.chat_message("user"):
                    st.write(olay_metni)
                
                with st.chat_message("assistant"):
                    with st.spinner(f"Gemini {st.session_state.aktif_kategori} kurallarını okuyor ve analiz ediyor..."):
                        try:
                            # Seçili kategorideki metinleri çek (AI'nin okuması için)
                            response = supabase.table("kural_icerikleri").select("sayfa_no, icerik").eq("kategori", st.session_state.aktif_kategori).execute()
                            tum_metin = ""
                            if response.data:
                                for satir in response.data:
                                    tum_metin += f"\n--- Sayfa {satir['sayfa_no']} ---\n{satir['icerik']}\n"
                            
                            if not tum_metin:
                                st.warning("Bu kategoride kural metni bulunamadı.")
                            else:
                                # Gemini'a gönderilecek özel prompt
                                prompt = f"""
                                Sen uluslararası yetkili bir Tenis Başhakemisin (Gold Badge).
                                
                                Sana aşağıdaki resmi tenis kuralları dokümanını veriyorum:
                                KURAL METİNLERİ:
                                {tum_metin}
                                
                                HAKEMİN SORDUĞU OLAY:
                                "{olay_metni}"
                                
                                GÖREVİN:
                                Sadece yukarıda verdiğim kural metinlerine dayanarak bu olayın kural ihlali olup olmadığını, hakemin hangi kararı vermesi gerektiğini (ve varsa cezasını) net ve profesyonel bir dille açıkla.
                                Cevabının sonuna, kararı dayandırdığın 'Sayfa Numarasını' (örneğin: Kaynak: Sayfa 45) mutlaka ekle.
                                Eğer olay kural metinlerinde geçmiyorsa "Bu duruma uygun spesifik bir kural bulunamadı" de.
                                """
                                
                                cevap = ai_model.generate_content(prompt)
                                st.markdown(cevap.text)
                                
                        except Exception as e:
                            st.error(f"Yapay Zeka analizi sırasında hata oluştu: {e}")

    # ------------------ 3. İNDEKS SEKMESİ ------------------
    with sekme_indeks:
        st.subheader("📚 Kayıtlı Belgeler Kütüphanesi")
        try:
            response = supabase.table("kural_icerikleri").select("dosya_adi, kategori, dosya_url").execute()
            if response.data:
                df = pd.DataFrame(response.data)
                df_unique = df.drop_duplicates(subset=["dosya_adi"]).reset_index(drop=True)
                
                siralama_turu = st.radio("Filtreleme Modu:", ["Alfabetik Sıralama", "Kategoriye Göre"], horizontal=True)
                
                if siralama_turu == "Alfabetik Sıralama":
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
                        secilen_grup = st.selectbox("Görüntülenecek Kategoriyi Seçin:", kategoriler_listesi)
                        df_filtered = df_unique[df_unique["kategori"] == secilen_grup].sort_values(by="dosya_adi")
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
