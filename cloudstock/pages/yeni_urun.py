import streamlit as st
import sqlite3
import database as db
import time

def goster():
    st.subheader("➕ Yeni Ürün & Varyant Ekle")
    with st.form("ana_ekran_urun_ekle_formu"):
        st.markdown("📋 **1. Ana Ürün Bilgileri (Katalog)**")
        c_ekle1, c_ekle2 = st.columns(2)
        urun_kodu = c_ekle1.text_input("Ürün Kodu", placeholder="Örn: TSH-005")
        ad = c_ekle2.text_input("Ürün Adı", placeholder="Örn: Basic Tişört")
        
        c_ekle3, c_ekle4 = st.columns(2)
        kategori = c_ekle3.selectbox("Kategori", ["Üst Giyim", "Alt Giyim", "İç Giyim", "Dış Giyim", "Aksesuar"])
        marka = c_ekle4.text_input("Marka")
        
        st.markdown("---")
        st.markdown("👕 **2. Varyant & Stok Bilgileri (Beden/Renk)**")
        barkod = st.text_input("Barkod (Bu varyanta özel)")
        
        cc1, cc2 = st.columns(2)
        renk = cc1.text_input("Renk")
        beden = cc2.text_input("Beden")
        
        cc3, cc4 = st.columns(2)
        miktar = cc3.number_input("Stok Miktarı", min_value=0, step=1)
        kritik = cc4.number_input("Kritik Seviye Uyarısı", min_value=1, step=1, value=5)
        
        cc5, cc6 = st.columns(2)
        alis_fiyati = cc5.number_input("Alış Fiyatı (TL)", min_value=0.0, step=10.0)
        satis_fiyati = cc6.number_input("Satış Fiyatı (TL)", min_value=0.0, step=10.0)
        
        submit_btn = st.form_submit_button("Ürünü Kaydet", type="primary", use_container_width=True)
        
        if submit_btn:
            if urun_kodu and ad and barkod:
                # Önce ana ürün var mı diye kontrol edelim
                conn = sqlite3.connect('cloudstock.db')
                c = conn.cursor()
                c.execute("SELECT id FROM urunler WHERE urun_kodu=?", (urun_kodu,))
                res = c.fetchone()
                conn.close()
                
                if res:
                    urun_id = res[0]
                else:
                    urun_id = db.ana_urun_ekle(urun_kodu, ad, kategori, marka)
                
                if urun_id:
                    basari = db.varyant_stok_ekle(urun_id, barkod, renk, beden, miktar, alis_fiyati, satis_fiyati, kritik)
                    if basari:
                        st.success(f"{ad} ({renk}-{beden}) sisteme eklendi!")
                        time.sleep(1)
                        # Ekledikten sonra otomatik olarak envanter sayfasına yönlendirelim
                        st.session_state.aktif_sayfa = "envanter"
                        st.rerun() 
                    else:
                        st.error("Hata: Bu barkod zaten sistemde kayıtlı!")
            else:
                st.error("Ürün Kodu, Ad ve Barkod alanları zorunludur!")