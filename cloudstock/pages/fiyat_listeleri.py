import streamlit as st
import pandas as pd
import database as db
import time

def goster():
    st.subheader("💰 Dinamik Fiyat Listeleri")
    st.markdown("Farklı müşteri gruplarına özel satış fiyat listeleri (Toptan, Perakende, Kampanya) oluşturun ve inceleyin.")
    
    fiyat_listeleri = db.fiyat_listelerini_getir()
    veriler = db.tum_envanteri_getir()
    
    if fiyat_listeleri:
        liste_isimleri = [f"{l['liste_adi']} (x{l['carpan']})" for l in fiyat_listeleri]
        
        c_fl1, c_fl2 = st.columns([1, 2])
        with c_fl1:
            st.markdown("#### 📌 Fiyat Listesi Seçimi")
            secili_liste_isim = st.radio("Listeler", liste_isimleri)
            secili_liste_idx = liste_isimleri.index(secili_liste_isim)
            secili_carpan = fiyat_listeleri[secili_liste_idx]['carpan']
            
            st.markdown("---")
            with st.form("yeni_liste_formu"):
                st.markdown("#### ➕ Yeni Liste Ekle")
                yeni_liste_adi = st.text_input("Liste Adı", placeholder="Örn: Bayi Fiyatı")
                yeni_liste_carpan = st.number_input("Fiyat Çarpanı", min_value=0.1, step=0.1, value=1.0, help="1.2 girilirse taban fiyat %20 artırılır.")
                if st.form_submit_button("Listeyi Oluştur", use_container_width=True, type="primary"):
                    if yeni_liste_adi:
                        if db.yeni_fiyat_listesi_ekle(yeni_liste_adi, yeni_liste_carpan):
                            st.success("Yeni fiyat listesi eklendi!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Bu isimde bir fiyat listesi zaten var!")
                    else:
                        st.error("Lütfen bir liste adı girin.")

        with c_fl2:
            st.markdown(f"#### 📊 {secili_liste_isim.split(' (')[0]} Hesaplanmış Liste")
            if veriler:
                df_fiyat = pd.DataFrame(veriler)
                df_fiyat['Liste_Fiyati'] = df_fiyat['satis_fiyati'] * secili_carpan
                gosterim_df = df_fiyat[['urun_kodu', 'barkod', 'urun_adi', 'renk', 'beden', 'alis_fiyati', 'satis_fiyati', 'Liste_Fiyati']]
                
                st.dataframe(
                    gosterim_df.style.format({
                        'alis_fiyati': '{:,.1f} TL', 
                        'satis_fiyati': '{:,.1f} TL', 
                        'Liste_Fiyati': '{:,.1f} TL'
                    }), 
                    width='stretch'
                )
            else:
                st.info("Hesaplanacak ürün verisi bulunamadı.")