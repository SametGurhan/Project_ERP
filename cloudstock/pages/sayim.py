import streamlit as st
import pandas as pd
import database as db
import sqlite3
import time

def goster():
    st.subheader("📝 Fiziksel Envanter Sayım Modülü")
    st.markdown("Fiziksel depo sayım sonuçlarını aşağıdaki interaktif tabloya girerek sistem stokları ile mutabakat sağlayabilirsiniz.")
    
    veriler = db.tum_envanteri_getir()
    
    if veriler:
        df_sayim = pd.DataFrame(veriler)[['urun_kodu', 'barkod', 'urun_adi', 'renk', 'beden', 'miktar']]
        df_sayim.rename(columns={'miktar': 'Sistem_Stogu'}, inplace=True)
        df_sayim['Guncel_Sayim'] = df_sayim['Sistem_Stogu'] 
        
        duzenlenmis_df = st.data_editor(
            df_sayim,
            column_config={
                "Guncel_Sayim": st.column_config.NumberColumn(
                    "Güncel Sayım Adedi (Düzenlenebilir)", 
                    min_value=0, 
                    step=1
                )
            },
            disabled=["urun_kodu", "barkod", "urun_adi", "renk", "beden", "Sistem_Stogu"],
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        if st.button("💾 Sayım Sonuçlarını Veritabanına İşle", type="primary", use_container_width=True):
            fark_var = False
            conn = sqlite3.connect('cloudstock.db')
            c = conn.cursor()
            
            for index, row in duzenlenmis_df.iterrows():
                if row['Sistem_Stogu'] != row['Guncel_Sayim']:
                    fark_var = True
                    c.execute("UPDATE stoklar SET miktar=? WHERE barkod=?", (row['Guncel_Sayim'], row['barkod']))
                    
            conn.commit()
            conn.close()
            
            if fark_var:
                st.success("Sayım farkları tespit edildi, stoklar güncellendi!")
                time.sleep(1)
                st.rerun()
            else:
                st.info("Sistem stokları ile sayım adetleri arasında fark bulunamadı.")
    else:
        st.info("Sistemde henüz kayıtlı ürün bulunmuyor.")