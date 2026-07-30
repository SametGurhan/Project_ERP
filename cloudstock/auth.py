import sqlite3
import hashlib

def auth_tablosunu_kur():
    """Kullanıcılar ve roller için veritabanı tablosunu oluşturur."""
    conn = sqlite3.connect('cloudstock.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kullanicilar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_adi TEXT UNIQUE NOT NULL,
        sifre TEXT NOT NULL,
        rol TEXT DEFAULT 'Uye',
        olusturulma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Varsayılan bir admin hesabı yoksa oluşturalım (Kullanıcı: admin, Şifre: 1234)
    cursor.execute("SELECT COUNT(*) FROM kullanicilar WHERE kullanici_adi=?", ('admin',))
    if cursor.fetchone()[0] == 0:
        sifre_hash = hashlib.sha256('1234'.encode()).hexdigest()
        cursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, rol) VALUES (?, ?, ?)", 
                       ('admin', sifre_hash, 'Admin'))
    
    conn.commit()
    conn.close()

def kullanici_kaydet(kullanici_adi, sifre, rol='Uye'):
    """Yeni kullanıcı kaydı oluşturur."""
    conn = sqlite3.connect('cloudstock.db')
    cursor = conn.cursor()
    sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, rol) VALUES (?, ?, ?)", 
                       (kullanici_adi, sifre_hash, rol))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def giris_kontrol(kullanici_adi, sifre):
    """Giriş bilgilerini kontrol eder, başarılıysa rolü döndürür."""
    conn = sqlite3.connect('cloudstock.db')
    cursor = conn.cursor()
    sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
    
    cursor.execute("SELECT rol FROM kullanicilar WHERE kullanici_adi=? AND sifre=?", (kullanici_adi, sifre_hash))
    res = cursor.fetchone()
    conn.close()
    
    if res:
        return res[0] # 'Admin' veya 'Uye'
    return None