import sqlite3
import hashlib

def baglanti_olustur():
    """SQLite veritabanına bağlanır."""
    conn = sqlite3.connect('cloudstock.db')
    conn.row_factory = sqlite3.Row 
    return conn

def tablolari_kur():
    """DİA-Benzeri gelişmiş veritabanı tablolarını ve kullanıcı yetkilendirme tablosunu oluşturur."""
    conn = baglanti_olustur()
    cursor = conn.cursor()
    
    # 1. Ana Ürünler Tablosu (Katalog)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS urunler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        urun_kodu TEXT UNIQUE NOT NULL,
        ad TEXT NOT NULL,
        kategori TEXT,
        marka TEXT,
        vergi_orani REAL DEFAULT 20.0,
        olusturulma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. Varyant ve Stoklar Tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stoklar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        urun_id INTEGER NOT NULL,
        barkod TEXT UNIQUE NOT NULL,
        renk TEXT,
        beden TEXT,
        miktar INTEGER NOT NULL DEFAULT 0,
        kritik_seviye INTEGER NOT NULL DEFAULT 5,
        alis_fiyati REAL NOT NULL,
        satis_fiyati REAL NOT NULL,
        FOREIGN KEY (urun_id) REFERENCES urunler (id) ON DELETE CASCADE
    )
    ''')

    # 3. Siparişler Tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS siparisler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fatura_no TEXT UNIQUE,
        musteri_ad_soyad TEXT,
        toplam_tutar REAL,
        durum TEXT DEFAULT 'Bekliyor',
        tarih DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 4. Kullanıcılar ve Yetkilendirme Tablosu (Admin / Üye)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kullanicilar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_adi TEXT UNIQUE NOT NULL,
        sifre TEXT NOT NULL,
        rol TEXT DEFAULT 'Uye',
        olusturulma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 5. Fiyat Listeleri Tanımları (Örn: Toptan, Perakende, İndirimli)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fiyat_listeleri (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        liste_adi TEXT UNIQUE NOT NULL,
        carpan REAL NOT NULL DEFAULT 1.0, -- Stoktaki ana satış fiyatına uygulanacak çarpan (Örn Perakende için 1.2)
        olusturulma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Varsayılan admin hesabı yoksa oluştur
    cursor.execute("SELECT COUNT(*) FROM kullanicilar WHERE kullanici_adi=?", ('admin',))
    if cursor.fetchone()[0] == 0:
        sifre_hash = hashlib.sha256('1234'.encode()).hexdigest()
        cursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, rol) VALUES (?, ?, ?)", 
                       ('admin', sifre_hash, 'Admin'))
                       
    # Varsayılan fiyat listeleri yoksa oluştur
    cursor.execute("SELECT COUNT(*) FROM fiyat_listeleri")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO fiyat_listeleri (liste_adi, carpan) VALUES (?, ?)", ('Ana Satış (Toptan)', 1.0))
        cursor.execute("INSERT INTO fiyat_listeleri (liste_adi, carpan) VALUES (?, ?)", ('Perakende', 1.2))
        cursor.execute("INSERT INTO fiyat_listeleri (liste_adi, carpan) VALUES (?, ?)", ('İndirimli Kampanya', 0.8))
        cursor.execute("INSERT INTO fiyat_listeleri (liste_adi, carpan) VALUES (?, ?)", ('Premium Müşteri', 0.9))
    
    conn.commit()
    conn.close()
    print("Veritabanı tabloları hazır.")

def ana_urun_ekle(urun_kodu, ad, kategori, marka, vergi_orani=20.0):
    conn = baglanti_olustur()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO urunler (urun_kodu, ad, kategori, marka, vergi_orani) VALUES (?, ?, ?, ?, ?)", 
                       (urun_kodu, ad, kategori, marka, vergi_orani))
        conn.commit()
        urun_id = cursor.lastrowid
        return urun_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def varyant_stok_ekle(urun_id, barkod, renk, beden, miktar, alis_fiyati, satis_fiyati, kritik_seviye=5):
    conn = baglanti_olustur()
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO stoklar 
                          (urun_id, barkod, renk, beden, miktar, alis_fiyati, satis_fiyati, kritik_seviye) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (urun_id, barkod, renk, beden, miktar, alis_fiyati, satis_fiyati, kritik_seviye))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def tum_envanteri_getir():
    conn = baglanti_olustur()
    cursor = conn.cursor()
    sorgu = '''
        SELECT 
            u.urun_kodu, 
            u.ad as urun_adi, 
            u.kategori,
            s.barkod,
            s.renk,
            s.beden,
            s.miktar,
            s.alis_fiyati,
            s.satis_fiyati,
            s.kritik_seviye,
            (s.miktar * s.satis_fiyati) as toplam_deger
        FROM urunler u
        JOIN stoklar s ON u.id = s.urun_id
        ORDER BY u.urun_kodu, s.renk, s.beden
    '''
    cursor.execute(sorgu)
    veriler = cursor.fetchall()
    conn.close()
    return [dict(satir) for satir in veriler]

def stok_guncelle(barkod, renk, beden, miktar, alis, satis, kritik):
    conn = baglanti_olustur()
    cursor = conn.cursor()
    try:
        cursor.execute('''UPDATE stoklar 
                          SET renk=?, beden=?, miktar=?, alis_fiyati=?, satis_fiyati=?, kritik_seviye=? 
                          WHERE barkod=?''', 
                       (renk, beden, miktar, alis, satis, kritik, barkod))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def stok_sil(barkod):
    conn = baglanti_olustur()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM stoklar WHERE barkod=?", (barkod,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

# --- YENİ EKLENEN FİYAT LİSTESİ FONKSİYONLARI ---

def fiyat_listelerini_getir():
    """Sistemdeki tanımlı fiyat listesi çarpanlarını getirir."""
    conn = baglanti_olustur()
    cursor = conn.cursor()
    cursor.execute("SELECT id, liste_adi, carpan FROM fiyat_listeleri ORDER BY id")
    veriler = cursor.fetchall()
    conn.close()
    return [dict(satir) for satir in veriler]

def yeni_fiyat_listesi_ekle(liste_adi, carpan):
    conn = baglanti_olustur()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO fiyat_listeleri (liste_adi, carpan) VALUES (?, ?)", (liste_adi, carpan))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def fiyat_listesi_guncelle(liste_id, yeni_carpan):
    conn = baglanti_olustur()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE fiyat_listeleri SET carpan=? WHERE id=?", (yeni_carpan, liste_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def dinamik_fiyatli_envanter_getir(carpan=1.0):
    """Mevcut envanteri, seçilen fiyat listesinin çarpanı ile hesaplayarak getirir."""
    envanter = tum_envanteri_getir()
    for urun in envanter:
        # Alış fiyatı sabittir, satış fiyatı listeye göre (çarpanla) değişir.
        urun['liste_satis_fiyati'] = urun['satis_fiyati'] * carpan
    return envanter

# =========================================================================
# DETAYLI SİMÜLASYON VERİ TABANI (50 VARYANT)
# =========================================================================
def hizli_ornek_veri_ekle():
    print("Detaylı 50 Ürünlük Veritabanı Yükleniyor... Lütfen Bekleyin.")
    katalog = [
        # --- ÜST GİYİM ---
        {"kodu": "TSH-101", "ad": "Basic V Yaka Tişört", "kat": "Üst Giyim", "marka": "CloudBasic", "vars": [
            {"b": "8691011", "r": "Siyah", "bd": "S", "st": 15, "al": 80, "sa": 250},
            {"b": "8691012", "r": "Siyah", "bd": "M", "st": 3,  "al": 80, "sa": 250}, 
            {"b": "8691013", "r": "Siyah", "bd": "L", "st": 0,  "al": 80, "sa": 250}, 
            {"b": "8691014", "r": "Beyaz", "bd": "S", "st": 20, "al": 80, "sa": 250},
            {"b": "8691015", "r": "Beyaz", "bd": "M", "st": 12, "al": 80, "sa": 250},
            {"b": "8691016", "r": "Beyaz", "bd": "L", "st": 8,  "al": 80, "sa": 250}
        ]},
        {"kodu": "TSH-102", "ad": "Oversize Baskılı Tişört", "kat": "Üst Giyim", "marka": "StreetX", "vars": [
            {"b": "8691021", "r": "Gri Melanj", "bd": "M",  "st": 45, "al": 110, "sa": 350},
            {"b": "8691022", "r": "Gri Melanj", "bd": "L",  "st": 14, "al": 110, "sa": 350},
            {"b": "8691023", "r": "Gri Melanj", "bd": "XL", "st": 2,  "al": 110, "sa": 350}, 
            {"b": "8691024", "r": "Bordo",      "bd": "M",  "st": 5,  "al": 110, "sa": 350},
            {"b": "8691025", "r": "Bordo",      "bd": "L",  "st": 0,  "al": 110, "sa": 350}  
        ]},
        
        # --- ALT GİYİM ---
        {"kodu": "PNT-201", "ad": "Slim Fit Kot Pantolon", "kat": "Alt Giyim", "marka": "DenimX", "vars": [
            {"b": "8692011", "r": "Açık Mavi", "bd": "30", "st": 25, "al": 300, "sa": 800},
            {"b": "8692012", "r": "Açık Mavi", "bd": "32", "st": 30, "al": 300, "sa": 800},
            {"b": "8692013", "r": "Açık Mavi", "bd": "34", "st": 1,  "al": 300, "sa": 800}, 
            {"b": "8692014", "r": "Siyah",     "bd": "30", "st": 0,  "al": 300, "sa": 800}, 
            {"b": "8692015", "r": "Siyah",     "bd": "32", "st": 8,  "al": 300, "sa": 800},
            {"b": "8692016", "r": "Siyah",     "bd": "34", "st": 12, "al": 300, "sa": 800}
        ]},
        {"kodu": "PNT-202", "ad": "Cepli Kargo Pantolon", "kat": "Alt Giyim", "marka": "StreetX", "vars": [
            {"b": "8692021", "r": "Haki", "bd": "32", "st": 50, "al": 250, "sa": 650},
            {"b": "8692022", "r": "Haki", "bd": "34", "st": 45, "al": 250, "sa": 650},
            {"b": "8692023", "r": "Haki", "bd": "36", "st": 4,  "al": 250, "sa": 650}, 
            {"b": "8692024", "r": "Bej",  "bd": "32", "st": 10, "al": 250, "sa": 650},
            {"b": "8692025", "r": "Bej",  "bd": "34", "st": 0,  "al": 250, "sa": 650}  
        ]},

        # --- İÇ GİYİM ---
        {"kodu": "UND-301", "ad": "Dantelli Bralet Takım", "kat": "İç Giyim", "marka": "CloudSecret", "vars": [
            {"b": "8693011", "r": "Kırmızı", "bd": "75B", "st": 8,  "al": 180, "sa": 450},
            {"b": "8693012", "r": "Kırmızı", "bd": "80B", "st": 15, "al": 180, "sa": 450},
            {"b": "8693013", "r": "Kırmızı", "bd": "85B", "st": 2,  "al": 180, "sa": 450}, 
            {"b": "8693014", "r": "Siyah",   "bd": "75B", "st": 0,  "al": 180, "sa": 450}, 
            {"b": "8693015", "r": "Siyah",   "bd": "80B", "st": 22, "al": 180, "sa": 450},
            {"b": "8693016", "r": "Siyah",   "bd": "85B", "st": 5,  "al": 180, "sa": 450}  
        ]},
        {"kodu": "UND-302", "ad": "Erkek Boxer (3'lü Paket)", "kat": "İç Giyim", "marka": "Comfort+", "vars": [
            {"b": "8693021", "r": "Karışık", "bd": "S",  "st": 30, "al": 150, "sa": 300},
            {"b": "8693022", "r": "Karışık", "bd": "M",  "st": 0,  "al": 150, "sa": 300}, 
            {"b": "8693023", "r": "Karışık", "bd": "L",  "st": 18, "al": 150, "sa": 300},
            {"b": "8693024", "r": "Karışık", "bd": "XL", "st": 4,  "al": 150, "sa": 300}  
        ]},

        # --- DIŞ GİYİM ---
        {"kodu": "MNT-401", "ad": "Su Geçirmez Şişme Mont", "kat": "Dış Giyim", "marka": "CloudOutdoor", "vars": [
            {"b": "8694011", "r": "Lacivert", "bd": "M",  "st": 12, "al": 600, "sa": 1800},
            {"b": "8694012", "r": "Lacivert", "bd": "L",  "st": 8,  "al": 600, "sa": 1800},
            {"b": "8694013", "r": "Lacivert", "bd": "XL", "st": 1,  "al": 600, "sa": 1800}, 
            {"b": "8694014", "r": "Haki",     "bd": "M",  "st": 0,  "al": 600, "sa": 1800}, 
            {"b": "8694015", "r": "Haki",     "bd": "L",  "st": 15, "al": 600, "sa": 1800},
            {"b": "8694016", "r": "Haki",     "bd": "XL", "st": 4,  "al": 600, "sa": 1800}  
        ]},
        {"kodu": "JKT-402", "ad": "Klasik Suni Deri Ceket", "kat": "Dış Giyim", "marka": "StreetX", "vars": [
            {"b": "8694021", "r": "Siyah", "bd": "S", "st": 6,  "al": 450, "sa": 1200},
            {"b": "8694022", "r": "Siyah", "bd": "M", "st": 10, "al": 450, "sa": 1200},
            {"b": "8694023", "r": "Siyah", "bd": "L", "st": 2,  "al": 450, "sa": 1200}  
        ]},

        # --- AKSESUAR ---
        {"kodu": "AKS-501", "ad": "Hakiki Deri Klasik Kemer", "kat": "Aksesuar", "marka": "CloudBasic", "vars": [
            {"b": "8695011", "r": "Siyah",      "bd": "Standart", "st": 55, "al": 100, "sa": 350},
            {"b": "8695012", "r": "Kahverengi", "bd": "Standart", "st": 40, "al": 100, "sa": 350}
        ]},
        {"kodu": "AKS-502", "ad": "Kışlık Örme Bere", "kat": "Aksesuar", "marka": "CloudOutdoor", "vars": [
            {"b": "8695021", "r": "Siyah", "bd": "Standart", "st": 0,  "al": 40, "sa": 150}, 
            {"b": "8695022", "r": "Bordo", "bd": "Standart", "st": 18, "al": 40, "sa": 150},
            {"b": "8695023", "r": "Gri",   "bd": "Standart", "st": 3,  "al": 40, "sa": 150}  
        ]}
    ]

    for urun in katalog:
        u_id = ana_urun_ekle(urun["kodu"], urun["ad"], urun["kat"], urun["marka"])
        if u_id is None:
            conn = baglanti_olustur()
            c = conn.cursor()
            c.execute("SELECT id FROM urunler WHERE urun_kodu=?", (urun["kodu"],))
            res = c.fetchone()
            if res:
                u_id = res[0]
            conn.close()
        
        if u_id:
            for v in urun["vars"]:
                varyant_stok_ekle(u_id, v["b"], v["r"], v["bd"], v["st"], v["al"], v["sa"], kritik_seviye=5)
                
    print("✅ Tüm örnek veriler başarıyla veritabanına işlendi!")

if __name__ == "__main__":
    tablolari_kur()
    hizli_ornek_veri_ekle()