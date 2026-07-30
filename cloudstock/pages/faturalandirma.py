import streamlit as st
import pandas as pd
import database as db
import sqlite3
import time
from datetime import datetime

def goster():
    st.subheader("📄 Müşteri Satış & PDF Fatura Oluşturucu")
    st.markdown("Stoktaki ürünleri seçerek müşteri satışı yapın ve yazdırılabilir resmi fatura oluşturun.")
    
    veriler = db.tum_envanteri_getir()
    fiyat_listeleri = db.fiyat_listelerini_getir()
    
    if veriler:
        c_fat1, c_fat2 = st.columns(2)
        musteri_adi = c_fat1.text_input("Müşteri Ad Soyad / Unvan", placeholder="Örn: Ahmet Yılmaz Ticaret")
        
        liste_secenekleri = [f"{l['liste_adi']} (x{l['carpan']})" for l in fiyat_listeleri]
        secilen_liste_str = c_fat2.selectbox("Uygulanacak Fiyat Tarifesi", liste_secenekleri)
        carpan = fiyat_listeleri[liste_secenekleri.index(secilen_liste_str)]['carpan']
        
        st.markdown("---")
        st.markdown("#### 🛒 Faturaya Ürün Ekle")
        
        urun_secenekleri = [f"[{u['urun_kodu']}] {u['barkod']} - {u['urun_adi']} ({u['renk']}-{u['beden']}) | Stok: {u['miktar']}" for u in veriler]
        secilen_urun_str = st.selectbox("Satılacak Ürünü Seçin", urun_secenekleri)
        
        secilen_idx = urun_secenekleri.index(secilen_urun_str)
        secilen_urun = veriler[secilen_idx]
        
        c_adet, c_fiyat = st.columns(2)
        satilacak_adet = c_adet.number_input("Satış Adedi", min_value=1, max_value=int(secilen_urun['miktar']) if secilen_urun['miktar'] > 0 else 1, value=1)
        
        birim_fiyat = secilen_urun['satis_fiyati'] * carpan
        c_fiyat.number_input("Birim Satış Fiyatı (TL)", value=float(birim_fiyat), disabled=True)
        
        if "fatura_sepeti" not in st.session_state:
            st.session_state.fatura_sepeti = []
            
        if st.button("➕ Sepete Ekle", type="secondary"):
            if secilen_urun['miktar'] < satilacak_adet:
                st.error("Yetersiz stok!")
            else:
                st.session_state.fatura_sepeti.append({
                    "barkod": secilen_urun['barkod'],
                    "urun_adi": f"{secilen_urun['urun_adi']} ({secilen_urun['renk']}-{secilen_urun['beden']})",
                    "adet": satilacak_adet,
                    "birim_fiyat": birim_fiyat,
                    "toplam": satilacak_adet * birim_fiyat
                })
                st.success("Ürün faturaya eklendi.")

        if st.session_state.fatura_sepeti:
            st.markdown("---")
            st.markdown("#### 📋 Fatura Kalemleri")
            df_sepet = pd.DataFrame(st.session_state.fatura_sepeti)
            st.dataframe(df_sepet.style.format({'birim_fiyat': '{:,.2f} TL', 'toplam': '{:,.2f} TL'}), width='stretch')
            
            matrah = df_sepet['toplam'].sum()
            kdv = matrah * 0.20 # %20 KDV
            genel_toplam = matrah + kdv
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Ara Toplam (Matrah)", f"{matrah:,.2f} TL")
            col_m2.metric("KDV (%20)", f"{kdv:,.2f} TL")
            col_m3.metric("GENEL TOPLAM", f"{genel_toplam:,.2f} TL")
            
            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("📄 Faturayı Kes & Stoktan Düş", type="primary", use_container_width=True):
                if not musteri_adi:
                    st.error("Lütfen müşteri adı giriniz.")
                else:
                    # Stokları düş ve siparişi kaydet
                    fatura_no = f"FAT-{int(time.time())}"
                    conn = sqlite3.connect('cloudstock.db')
                    c = conn.cursor()
                    
                    for item in st.session_state.fatura_sepeti:
                        c.execute("UPDATE stoklar SET miktar = miktar - ? WHERE barkod = ?", (item['adet'], item['barkod']))
                    
                    c.execute("INSERT INTO siparisler (fatura_no, musteri_ad_soyad, toplam_tutar, durum) VALUES (?, ?, ?, ?)",
                              (fatura_no, musteri_adi, genel_toplam, 'Faturalandı'))
                    conn.commit()
                    conn.close()
                    
                    st.success(f"{fatura_no} numaralı fatura başarıyla kesildi ve stoklar düşüldü!")
                    st.session_state.son_fatura = {
                        "fatura_no": fatura_no,
                        "musteri": musteri_adi,
                        "tarih": datetime.now().strftime("%d.%m.%Y %H:%M"),
                        "kalemler": st.session_state.fatura_sepeti,
                        "matrah": matrah,
                        "kdv": kdv,
                        "toplam": genel_toplam
                    }
                    st.session_state.fatura_sepeti = []
                    time.sleep(1)
                    st.rerun()
                    
            if c_btn2.button("🗑️ Sepeti Temizle", use_container_width=True):
                st.session_state.fatura_sepeti = []
                st.rerun()

        # Kesilen Son Faturayı HTML/Yazdırılabilir Format Gösterimi
        if "son_fatura" in st.session_state:
            st.markdown("---")
            st.markdown("### 🖨️ Yazdırılabilir Fatura Önizleme")
            sf = st.session_state.son_fatura
            
            fatura_html = f"""
            <div style="background-color: white; color: black; padding: 30px; border-radius: 8px; border: 1px solid #ccc; font-family: Arial, sans-serif;">
                <div style="display: flex; justify-content: space-between; border-bottom: 2px solid #333; padding-bottom: 10px;">
                    <div>
                        <h2 style="margin:0; color:#0b57d0;">CloudStock ERP</h2>
                        <p style="margin:5px 0 0 0; color:#555;">Resmi Satış Faturası</p>
                    </div>
                    <div style="text-align: right;">
                        <h3 style="margin:0;">Fatura No: {sf['fatura_no']}</h3>
                        <p style="margin:5px 0 0 0; color:#555;">Tarih: {sf['tarih']}</p>
                    </div>
                </div>
                <div style="margin: 20px 0;">
                    <p><b>Müşteri / Unvan:</b> {sf['musteri']}</p>
                </div>
                <table style="width:100%; border-collapse: collapse; margin-top:10px;">
                    <thead>
                        <tr style="background-color:#f0f4f9; border-bottom:1px solid #ddd;">
                            <th style="text-align:left; padding:8px;">Ürün</th>
                            <th style="text-align:center; padding:8px;">Adet</th>
                            <th style="text-align:right; padding:8px;">Birim Fiyat</th>
                            <th style="text-align:right; padding:8px;">Toplam</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for k in sf['kalemler']:
                fatura_html += f"""
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding:8px;">{k['urun_adi']}</td>
                    <td style="text-align:center; padding:8px;">{k['adet']}</td>
                    <td style="text-align:right; padding:8px;">{k['birim_fiyat']:,.2f} TL</td>
                    <td style="text-align:right; padding:8px;">{k['toplam']:,.2f} TL</td>
                </tr>
                """
            fatura_html += f"""
                    </tbody>
                </table>
                <div style="text-align: right; margin-top: 20px; font-size: 14px;">
                    <p style="margin:4px 0;">Ara Toplam: <b>{sf['matrah']:,.2f} TL</b></p>
                    <p style="margin:4px 0;">KDV (%20): <b>{sf['kdv']:,.2f} TL</b></p>
                    <h3 style="margin:10px 0 0 0; color:#146c2e;">Genel Toplam: {sf['toplam']:,.2f} TL</h3>
                </div>
            </div>
            """
            st.components.v1.html(fatura_html, height=450, scrolling=True)
    else:
        st.info("Faturalandırılacak ürün bulunamadı.")