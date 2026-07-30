import streamlit as st
import pandas as pd
import database as db

def goster():
    st.subheader("📋 Malzeme İhtiyaç Planlaması (MRP)")
    st.markdown("Stok miktarı kritik sınırın altına düşen ürünlerin otomatik satın alma ihtiyaç hesabı (Güvenli Stok Tamponu: +5 Adet):")
    
    veriler = db.tum_envanteri_getir()
    
    if veriler:
        df_mrp = pd.DataFrame(veriler)
        eksikler = df_mrp[df_mrp['miktar'] <= df_mrp['kritik_seviye']].copy()
        
        if len(eksikler) > 0:
            # İhtiyaç Mantığı: (Kritik Sınır - Mevcut Stok) + 5 Tampon Stok
            eksikler['siparis_miktari'] = (eksikler['kritik_seviye'] - eksikler['miktar']) + 5
            eksikler['toplam_maliyet'] = eksikler['siparis_miktari'] * eksikler['alis_fiyati']
            
            toplam_butce = eksikler['toplam_maliyet'].sum()
            toplam_siparis_adedi = eksikler['siparis_miktari'].sum()
            
            col1, col2 = st.columns(2)
            col1.metric("🚨 Tedarik Gereken Varyant", f"{len(eksikler)} Çeşit")
            col2.metric("💰 Toplam Tedarik Bütçesi İhtiyacı", f"{toplam_butce:,.2f} TL")
            
            st.markdown("---")
            goster_mrp = eksikler[['urun_kodu', 'barkod', 'urun_adi', 'renk', 'beden', 'miktar', 'kritik_seviye', 'siparis_miktari', 'alis_fiyati', 'toplam_maliyet']]
            
            st.dataframe(
                goster_mrp.style.format({
                    'alis_fiyati': '{:,.2f} TL',
                    'toplam_maliyet': '{:,.2f} TL'
                }), 
                width='stretch'
            )
        else:
            st.success("✅ Tüm stoklar güvenli seviyede. Şu anda satın alma yapılması gereken ürün yok.")
    else:
        st.info("Sistemde henüz ürün kaydı yok.")