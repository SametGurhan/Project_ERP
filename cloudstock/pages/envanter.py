import streamlit as st
import pandas as pd
import database as db
import time

def goster():
    veriler = db.tum_envanteri_getir()

    if veriler:
        df = pd.DataFrame(veriler)
        
        toplam_varyant = len(df)
        toplam_stok = df['miktar'].sum()
        kritik_sayisi = len(df[(df['miktar'] <= df['kritik_seviye']) & (df['miktar'] > 0)])
        tukenen_sayisi = len(df[df['miktar'] == 0])
        
        st.subheader("📊 Güncel Envanter & Yönetim")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Toplam Varyant Çeşidi", toplam_varyant)
        col2.metric("Toplam Stok Adedi", f"{toplam_stok} Adet")
        col3.metric("Kritik Stok Uyarısı", kritik_sayisi, "-Sipariş Geçilmeli", delta_color="inverse")
        col4.metric("Tükenen Ürünler", tukenen_sayisi, "-Acil Tedarik", delta_color="inverse")
        
        st.markdown("---")
        
        def satiri_boya(satir):
            if satir['miktar'] == 0:
                return ['background-color: #EF4444; color: white; font-weight: bold'] * len(satir)
            elif satir['miktar'] <= satir['kritik_seviye']:
                return ['background-color: #F59E0B; color: black; font-weight: bold'] * len(satir)
            return [''] * len(satir)
        
        format_dict = {
            'alis_fiyati': '{:,.1f} TL',
            'satis_fiyati': '{:,.1f} TL',
            'toplam_deger': '{:,.1f} TL'
        }
        
        styled_df = df.style.apply(satiri_boya, axis=1).format(format_dict)
        
        if "secilen_index" not in st.session_state:
            st.session_state.secilen_index = 0
        if "onceki_tablo_secimi" not in st.session_state:
            st.session_state.onceki_tablo_secimi = []
            
        st.markdown("💡 *Tablodan düzenlemek istediğiniz ürüne tıklayarak aşağıdaki paneli otomatik doldurabilirsiniz:*")
        
        secim_sonucu = st.dataframe(
            styled_df, 
            width='stretch', 
            selection_mode="single-row", 
            on_select="rerun",
            key="envanter_tablosu"
        )
        
        st.markdown("---")
        st.markdown("### ✏️ Ürün Düzenle / Sil (Seçili Ürün Yönetimi)")
        
        edit_secenekler = [f"[{u['urun_kodu']}] {u['barkod']} - {u['urun_adi']} ({u['renk']} - {u['beden']})" for u in veriler]
        
        guncel_tablo_secimi = secim_sonucu.get("selection", {}).get("rows", [])
        
        if guncel_tablo_secimi != st.session_state.onceki_tablo_secimi:
            st.session_state.onceki_tablo_secimi = guncel_tablo_secimi
            if guncel_tablo_secimi:
                st.session_state.secilen_index = guncel_tablo_secimi[0]
                # Tablodan tıklandığında selectbox state'ini de güncelliyoruz
                st.session_state.yonetim_selectbox = edit_secenekler[st.session_state.secilen_index]

        if st.session_state.secilen_index >= len(edit_secenekler):
            st.session_state.secilen_index = 0

        def selectbox_guncelle():
            st.session_state.secilen_index = edit_secenekler.index(st.session_state.yonetim_selectbox)

        secilen_edit = st.selectbox(
            "İşlem Yapılacak Ürünü Seçin:", 
            edit_secenekler, 
            index=st.session_state.secilen_index,
            key="yonetim_selectbox",
            on_change=selectbox_guncelle
        )
        
        secilen_idx = st.session_state.secilen_index
        urun_detay = veriler[secilen_idx]
        
        with st.form("tablo_ici_duzenle_form"):
            st.info(f"Barkod: {urun_detay['barkod']} (Sistemsel ID olduğu için değiştirilemez)")
            
            c_ana1, c_ana2 = st.columns(2)
            c_ana1.text_input("Ürün Kodu", value=urun_detay['urun_kodu'], disabled=True)
            c_ana2.text_input("Ürün Adı", value=urun_detay['urun_adi'], disabled=True)
            
            c1, c2 = st.columns(2)
            y_renk = c1.text_input("Renk", value=urun_detay['renk'])
            y_beden = c2.text_input("Beden", value=urun_detay['beden'])
            
            y_miktar = c1.number_input("Stok Miktarı", min_value=0, step=1, value=int(urun_detay['miktar']))
            y_kritik = c2.number_input("Kritik Seviye", min_value=1, step=1, value=int(urun_detay['kritik_seviye']))
            
            y_alis = c1.number_input("Alış Fiyatı (TL)", min_value=0.0, step=10.0, value=float(urun_detay['alis_fiyati']))
            y_satis = c2.number_input("Satış Fiyatı (TL)", min_value=0.0, step=10.0, value=float(urun_detay['satis_fiyati']))
            
            col_btn1, col_btn2 = st.columns(2)
            guncelle_btn = col_btn1.form_submit_button("🔄 Değişiklikleri Kaydet", type="primary", use_container_width=True)
            sil_btn = col_btn2.form_submit_button("🗑️ Ürünü Tamamen Sil", use_container_width=True)
            
            if guncelle_btn:
                basari = db.stok_guncelle(urun_detay['barkod'], y_renk, y_beden, y_miktar, y_alis, y_satis, y_kritik)
                if basari:
                    st.success("Ürün başarıyla güncellendi!")
                    time.sleep(1)
                    st.rerun()
                    
            if sil_btn:
                basari = db.stok_sil(urun_detay['barkod'])
                if basari:
                    st.session_state.secilen_index = 0
                    st.session_state.onceki_tablo_secimi = []
                    st.warning("Ürün sistemden silindi!")
                    time.sleep(1)
                    st.rerun()
    else:
        st.info("Sistemde henüz kayıtlı ürün bulunmuyor. Yeni ürün ekleyebilirsiniz.")