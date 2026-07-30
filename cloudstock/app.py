import streamlit as st
import pandas as pd
import sqlite3
import database as db
import auth
import analiz as ai
import time
import locale
import hashlib

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="CloudStock ERP", layout="wide", page_icon="📦")

# Veritabanı ve tabloları kur
db.tablolari_kur()

# ==========================================
# 1. GİRİŞ KONTROLÜ VE AUTH (HAREKETLİ ÖRÜMCEK AĞI)
# ==========================================
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_adi = ""
    st.session_state.rol = ""

if not st.session_state.giris_yapildi:
    st.markdown("""
    <style>
    .stApp { background-color: transparent !important; }
    header { background-color: transparent !important; }
    
    .login-container {
        position: relative;
        z-index: 10;
        max-width: 420px;
        margin: 6vh auto;
        padding: 40px;
        background: rgba(30, 41, 59, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
        border: 1px solid #334155;
    }
    .login-title { text-align: center; color: #f8fafc; font-size: 26px; font-weight: 700; margin-bottom: 8px; }
    .login-subtitle { text-align: center; color: #38bdf8; font-size: 14px; margin-bottom: 30px; }
    </style>
    
    <div class="login-container">
        <div class="login-title">📦 CloudStock ERP</div>
        <div class="login-subtitle">Kurumsal Kaynak Planlama ve Yönetim Sistemi</div>
    </div>
    """, unsafe_allow_html=True)
    
    particle_js = """
    <style>
        body { margin: 0; overflow: hidden; background-color: #0f172a; }
        canvas { display: block; }
    </style>
    <canvas id="c"></canvas>
    <script>
        const frame = window.frameElement;
        if (frame) {
            frame.style.position = 'fixed';
            frame.style.top = '0';
            frame.style.left = '0';
            frame.style.width = '100vw';
            frame.style.height = '100vh';
            frame.style.zIndex = '-1';
            frame.style.pointerEvents = 'none';
        }
        const canvas = document.getElementById('c');
        const ctx = canvas.getContext('2d');
        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;
        
        window.addEventListener('resize', () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        });

        let mouse = { x: -1000, y: -1000 };
        window.parent.document.addEventListener('mousemove', (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        });
        window.parent.document.addEventListener('mouseleave', () => {
            mouse.x = -1000; mouse.y = -1000;
        });

        const particles = [];
        for (let i = 0; i < 100; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 1.5,
                vy: (Math.random() - 0.5) * 1.5,
                radius: Math.random() * 2 + 1
            });
        }

        function animate() {
            ctx.clearRect(0, 0, width, height);
            for (let i = 0; i < particles.length; i++) {
                let p = particles[i];
                p.x += p.vx; p.y += p.vy;
                if (p.x < 0 || p.x > width) p.vx *= -1;
                if (p.y < 0 || p.y > height) p.vy *= -1;
                
                let dx = mouse.x - p.x;
                let dy = mouse.y - p.y;
                let dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 150) {
                    p.x -= dx * 0.02;
                    p.y -= dy * 0.02;
                }
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = "#38bdf8";
                ctx.fill();
                
                for (let j = i + 1; j < particles.length; j++) {
                    let p2 = particles[j];
                    let dx2 = p.x - p2.x;
                    let dy2 = p.y - p2.y;
                    let dist2 = Math.sqrt(dx2*dx2 + dy2*dy2);
                    if (dist2 < 120) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(56, 189, 248, ${1 - dist2/120})`;
                        ctx.lineWidth = 1;
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animate);
        }
        animate();
    </script>
    """
    st.components.v1.html(particle_js, height=0)
    
    _, col_orta, _ = st.columns([1, 1.2, 1])
    with col_orta:
        with st.container():
            tab_giris, tab_kayit = st.tabs(["Giriş Yap", "Yeni Üye Kaydı"])
            with tab_giris:
                with st.form("giris_formu"):
                    k_adi = st.text_input("Kullanıcı Adı")
                    k_sifre = st.text_input("Şifre", type="password")
                    guncel_giris_btn = st.form_submit_button("Sisteme Giriş Yap", use_container_width=True)
                    if guncel_giris_btn:
                        sifre_hash = hashlib.sha256(k_sifre.encode()).hexdigest()
                        conn = sqlite3.connect('cloudstock.db')
                        c = conn.cursor()
                        c.execute("SELECT rol FROM kullanicilar WHERE kullanici_adi=? AND sifre=?", (k_adi, sifre_hash))
                        res = c.fetchone()
                        conn.close()
                        if res:
                            st.session_state.giris_yapildi = True
                            st.session_state.kullanici_adi = k_adi
                            st.session_state.rol = res[0]
                            st.rerun()
                        else:
                            st.error("Kullanıcı adı veya şifre hatalı!")
            with tab_kayit:
                with st.form("kayit_formu"):
                    y_adi = st.text_input("Yeni Kullanıcı Adı")
                    y_sifre = st.text_input("Yeni Şifre", type="password")
                    kayit_btn = st.form_submit_button("Hesap Oluştur", use_container_width=True)
                    if kayit_btn:
                        if y_adi and y_sifre:
                            if auth.kullanici_kaydet(y_adi, y_sifre, rol='Uye'):
                                st.success("Kayıt oluşturuldu! Giriş yapabilirsiniz.")
                            else:
                                st.error("Bu kullanıcı adı zaten alınmış!")
                        else:
                            st.error("Lütfen tüm alanları doldurun!")
    st.stop()

# ==========================================
# İLK GİRİŞTE DİL SEÇİMİ (POP-UP)
# ==========================================
if "lang" not in st.session_state:
    @st.dialog("🌍 Dil Seçimi / Language Selection")
    def dil_secim_kutusu():
        st.markdown("<p style='text-align: center;'>Lütfen sistem dilini seçin<br><i>Please select the system language</i></p>", unsafe_allow_html=True)
        st.write("") 
        c1, c2 = st.columns(2)
        if c1.button("🇹🇷 Türkçe", use_container_width=True):
            st.session_state.lang = "TR"
            st.rerun() 
        if c2.button("🇬🇧 English", use_container_width=True):
            st.session_state.lang = "EN"
            st.rerun() 
    dil_secim_kutusu()
    st.stop() 

try:
    locale.setlocale(locale.LC_TIME, 'tr_TR.UTF-8' if st.session_state.lang == "TR" else 'en_US.UTF-8')
except:
    pass 

if "aktif_sayfa" not in st.session_state:
    st.session_state.aktif_sayfa = "Envanter Yönetimi"

# ==========================================
# SOL YAN MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown(f"👤 **Oturum:** {st.session_state.kullanici_adi} `({st.session_state.rol})`")

    st.markdown("---")
    st.markdown("### 🧭 Menü Navigasyonu")
    
    if st.button("📊 Envanter & Yönetim", type="primary" if st.session_state.aktif_sayfa == "Envanter Yönetimi" else "secondary", use_container_width=True):
        st.session_state.aktif_sayfa = "Envanter Yönetimi"
        st.rerun()
        
    if st.button("💰 Fiyat Listeleri", type="primary" if st.session_state.aktif_sayfa == "Fiyat Listeleri" else "secondary", use_container_width=True):
        st.session_state.aktif_sayfa = "Fiyat Listeleri"
        st.rerun()
        
    if st.button("📋 MRP (İhtiyaç Planlama)", type="primary" if st.session_state.aktif_sayfa == "MRP" else "secondary", use_container_width=True):
        st.session_state.aktif_sayfa = "MRP"
        st.rerun()
        
    if st.button("📝 Envanter Sayımı", type="primary" if st.session_state.aktif_sayfa == "Sayım" else "secondary", use_container_width=True):
        st.session_state.aktif_sayfa = "Sayım"
        st.rerun()

    if st.button("📄 Faturalandırma", type="primary" if st.session_state.aktif_sayfa == "Faturalandırma" else "secondary", use_container_width=True):
        st.session_state.aktif_sayfa = "Faturalandırma"
        st.rerun()

    st.markdown("---")
    tema_acik = st.toggle("Açık Mod / Koyu Mod", value=False)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("📌 **Sistem Zamanı**")
    
    canli_saat_component = """
    <div style="font-family: monospace; font-size: 14px; font-weight: bold; text-align: center; background-color: #334155; padding: 10px; border-radius: 8px; color: #f8fafc; border: 1px solid #475569;">
        <div id="tarih_div" style="color: #38bdf8; margin-bottom: 4px;"></div>
        <div id="saat_div" style="font-size: 18px; color: #ffffff; letter-spacing: 1px;"></div>
    </div>
    <script>
    function updateClock() {
        const now = new Date();
        const optionsDate = { year: 'numeric', month: '2-digit', day: '2-digit' };
        document.getElementById('tarih_div').innerText = now.toLocaleDateString('tr-TR', optionsDate);
        
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        
        document.getElementById('saat_div').innerText = hours + ":" + minutes + ":" + seconds;
    }
    setInterval(updateClock, 1000);
    updateClock();
    </script>
    """
    st.components.v1.html(canli_saat_component, height=75)
    #Çıkış butonu
    if st.button("🚪 Çıkış Yap", use_container_width=True):
        st.session_state.giris_yapildi = False
        st.rerun()

if tema_acik:
    st.markdown("""
    <style>
    .stApp { background-color: #E8EEF4; }
    [data-testid="stSidebar"] { background-color: #D1E0EE; }
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div, [data-testid="stSidebar"] button { 
        background-color: #F0F4F8 !important; color: #1E293B !important; border: 1px solid #CBD5E1 !important;
    }
    .st-emotion-cache-10trblm, p, h1, h2, h3, h4, h5, h6, span, label, div { color: #1E293B !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# ANA EKRAN YÖNETİMİ
# ==========================================
st.title(f"📦 CloudStock ERP - {st.session_state.aktif_sayfa}")
veriler = db.tum_envanteri_getir()

# 1. SAYFA: ENVANTER & YÖNETİM (İÇİNDE YATAY SEKMELER İLE)
if st.session_state.aktif_sayfa == "Envanter Yönetimi":
    tab_env, tab_yeni, tab_ai = st.tabs([
        "📊 Güncel Envanter & Yönetim", 
        "➕ Yeni Ürün & Varyant Ekle", 
        "🤖 AI Stok Analizi"
    ])
    
    # --- YATAY SEKME 1: ENVANTER VE YÖNETİM ---
    with tab_env:
        if veriler:
            df = pd.DataFrame(veriler)
            
            toplam_varyant = len(df)
            toplam_stok = df['miktar'].sum()
            kritik_sayisi = len(df[(df['miktar'] <= df['kritik_seviye']) & (df['miktar'] > 0)])
            tukenen_sayisi = len(df[df['miktar'] == 0])
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📝 Toplam Varyant Çeşidi", toplam_varyant)
            col2.metric("📦 Toplam Stok Adedi", f"{toplam_stok} Adet")
            col3.metric("⚠️ Kritik Stok Uyarısı", kritik_sayisi, "-Sipariş Geçilmeli", delta_color="inverse")
            col4.metric("🚨 Tükenen Ürünler", tukenen_sayisi, "-Acil Tedarik", delta_color="inverse")
            
            st.markdown("---")
            
            def satiri_boya(satir):
                if satir['miktar'] == 0:
                    return ['background-color: #EF4444; color: white; font-weight: bold'] * len(satir)
                elif satir['miktar'] <= satir['kritik_seviye']:
                    return ['background-color: #F59E0B; color: black; font-weight: bold'] * len(satir)
                return [''] * len(satir)
            
            format_dict = {'alis_fiyati': '{:,.1f} TL', 'satis_fiyati': '{:,.1f} TL', 'toplam_deger': '{:,.1f} TL'}
            styled_df = df.style.apply(satiri_boya, axis=1).format(format_dict)
            
            if "secilen_index" not in st.session_state: st.session_state.secilen_index = 0
            if "onceki_tablo_secimi" not in st.session_state: st.session_state.onceki_tablo_secimi = []
                
            st.markdown("💡 *Tablodan düzenlemek istediğiniz ürüne tıklayarak aşağıdaki paneli otomatik doldurabilirsiniz:*")
            secim_sonucu = st.dataframe(styled_df, width='stretch', selection_mode="single-row", on_select="rerun", key="envanter_tablosu")
            
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

            if st.session_state.secilen_index >= len(edit_secenekler): st.session_state.secilen_index = 0

            def selectbox_guncelle(): st.session_state.secilen_index = edit_secenekler.index(st.session_state.yonetim_selectbox)

            secilen_edit = st.selectbox("İşlem Yapılacak Ürünü Seçin:", edit_secenekler, index=st.session_state.secilen_index, key="yonetim_selectbox", on_change=selectbox_guncelle)
            
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
                
                y_alis = c1.number_input("Alış Fiyatı", min_value=0.0, step=10.0, value=float(urun_detay['alis_fiyati']))
                y_satis = c2.number_input("Satış Fiyatı", min_value=0.0, step=10.0, value=float(urun_detay['satis_fiyati']))
                
                col_btn1, col_btn2 = st.columns(2)
                guncelle_btn = col_btn1.form_submit_button("🔄 Değişiklikleri Kaydet", type="primary", use_container_width=True)
                sil_btn = col_btn2.form_submit_button("🗑️ Ürünü Tamamen Sil", use_container_width=True)
                
                if guncelle_btn:
                    basari = db.stok_guncelle(urun_detay['barkod'], y_renk, y_beden, y_miktar, y_alis, y_satis, y_kritik)
                    if basari:
                        st.success("Ürün başarıyla güncellendi!"); time.sleep(1); st.rerun()
                if sil_btn:
                    basari = db.stok_sil(urun_detay['barkod'])
                    if basari:
                        st.session_state.secilen_index = 0
                        st.session_state.onceki_tablo_secimi = [] 
                        st.warning("Ürün sistemden silindi!"); time.sleep(1); st.rerun()
        else:
            st.info("Kayıtlı ürün yok.")

    # --- YATAY SEKME 2: YENİ ÜRÜN & VARYANT EKLE ---
    with tab_yeni:
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
                            st.rerun() 
                        else:
                            st.error("Hata: Bu barkod zaten sistemde kayıtlı!")
                else:
                    st.error("Ürün Kodu, Ad ve Barkod alanları zorunludur!")

    # --- YATAY SEKME 3: AI STOK ANALİZİ ---
    with tab_ai:
        st.write("Sistem, ürünlerin geçmiş satış hızını baz alarak **Lineer Regresyon** modeli ile gelecekteki stok tükenme tarihini hesaplar.")
        
        if veriler:
            secenekler = [f"{u['urun_adi']} ({u['renk']} - {u['beden']})" for u in veriler]
            secilen_urun = st.selectbox("Geleceğini Analiz Etmek İstediğiniz Ürünü Seçin:", secenekler)
            
            secilen_index = secenekler.index(secilen_urun)
            gercek_stok = veriler[secilen_index]['miktar']
            
            if st.button("🚀 Yapay Zeka Analizini Başlat", type="primary", use_container_width=True):
                if gercek_stok == 0:
                    st.error("Bu ürün zaten tükenmiş! Analiz edilecek stok kalmamış.")
                else:
                    with st.spinner("Yapay zeka modeli geçmiş verilerle eğitiliyor ve tahmin yapılıyor..."):
                        time.sleep(1.5)
                        df_grafik, ai_mesaji = ai.ai_stok_tahmini_yap(secilen_urun, gercek_stok)
                        
                        if "🚨" in ai_mesaji: st.error(ai_mesaji)
                        else: st.success(ai_mesaji)
                        
                        df_grafik.index = pd.to_datetime(df_grafik.index)
                        df_grafik = df_grafik.sort_index()
                        
                        st.line_chart(df_grafik, color=["#1E88E5", "#EF4444"], use_container_width=True)
                        st.caption("*Mavi Çizgi: Geçmiş 30 günün satış trendi. | Kırmızı Çizgi: Yapay zekanın önümüzdeki 15 gün için öngörüsü.*")
        else:
            st.warning("Sistemde kayıtlı veri yok.")

# 2. SAYFA: FİYAT LİSTELERİ (PAGES/ KONTROLÜ)
elif st.session_state.aktif_sayfa == "Fiyat Listeleri":
    import pages.fiyat_listeleri as sayfa_fiyat
    sayfa_fiyat.goster()

# 3. SAYFA: MRP (PAGES/ KONTROLÜ)
elif st.session_state.aktif_sayfa == "MRP":
    import pages.mrp as sayfa_mrp
    sayfa_mrp.goster()

# 4. SAYFA: SAYIM (PAGES/ KONTROLÜ)
elif st.session_state.aktif_sayfa == "Sayım":
    import pages.sayim as sayfa_sayim
    sayfa_sayim.goster()

# 5. SAYFA: FATURALANDIRMA (PAGES/ KONTROLÜ)
elif st.session_state.aktif_sayfa == "Faturalandırma":
    import pages.faturalandirma as sayfa_fatura
    sayfa_fatura.goster()