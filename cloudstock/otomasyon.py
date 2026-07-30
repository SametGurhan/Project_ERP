import database as db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- MAİL AYARLARI ---
# DİKKAT: Güvenlik için Gmail şifrenizi değil, "Uygulama Şifresi" kullanmalısınız.
# Gmail -> Hesap Yönetimi -> Güvenlik -> İki Adımlı Doğrulama -> Uygulama Şifreleri kısmından alınır.
GONDEREN_MAIL = "samet.gurhan17@gmail.com"
UYGULAMA_SIFRESI = "szzt mpsg boip fmri" # Buraya 16 haneli uygulama şifreni gir
ALICI_MAIL = "samet.gurhan18@gmail.com" # Uyarıların kime gideceği (Kendi mailini yazarak test edebilirsin)

def kritik_stoklari_kontrol_et():
    """Veritabanına bakar ve kritik seviyedeki ürünleri listeler."""
    print("🔍 Otomasyon: Stoklar kontrol ediliyor...")
    tum_urunler = db.tum_envanteri_getir()
    
    kritik_liste = []
    for urun in tum_urunler:
        if urun['miktar'] <= urun['kritik_seviye']:
            kritik_liste.append(urun)
            
    return kritik_liste

def uyari_maili_gonder(kritik_urunler):
    """Kritik ürünler listesini alır ve e-posta olarak gönderir."""
    if not kritik_urunler:
        print("✅ Her şey yolunda, kritik seviyede stok yok.")
        return

    print(f"⚠️ {len(kritik_urunler)} adet ürün kritik seviyede! Mail hazırlanıyor...")
    
    # Mail İçeriği (HTML formatında şık bir tablo)
    tarih = datetime.now().strftime("%d.%m.%Y %H:%M")
    html_icerik = f"""
    <html>
      <body>
        <h2 style="color: #e74c3c;">🚨 CloudStock Kritik Stok Uyarısı</h2>
        <p>Tarih: <b>{tarih}</b></p>
        <p>Aşağıdaki ürünler kritik seviyeye ulaşmış veya tükenmiştir. Acil tedarik edilmesi gerekmektedir.</p>
        
        <table border="1" style="border-collapse: collapse; width: 100%; text-align: left;">
          <tr style="background-color: #f2f2f2;">
            <th style="padding: 8px;">Barkod</th>
            <th style="padding: 8px;">Ürün Adı</th>
            <th style="padding: 8px;">Varyant</th>
            <th style="padding: 8px; color: red;">Kalan Stok</th>
            <th style="padding: 8px;">Kritik Sınır</th>
          </tr>
    """
    
    for u in kritik_urunler:
        html_icerik += f"""
          <tr>
            <td style="padding: 8px;">{u['barkod']}</td>
            <td style="padding: 8px;">{u['urun_adi']}</td>
            <td style="padding: 8px;">{u['renk']} - {u['beden']}</td>
            <td style="padding: 8px; font-weight: bold; color: red;">{u['miktar']}</td>
            <td style="padding: 8px;">{u['kritik_seviye']}</td>
          </tr>
        """
        
    html_icerik += """
        </table>
        <p><br><i>Bu mail CloudStock Otomasyon Sistemi tarafından otomatik gönderilmiştir.</i></p>
      </body>
    </html>
    """
    
    # Mail Yapılandırması
    msg = MIMEMultipart()
    msg['From'] = GONDEREN_MAIL
    msg['To'] = ALICI_MAIL
    msg['Subject'] = f"ACİL TEDARİK: {len(kritik_urunler)} Ürün Kritik Seviyede!"
    msg.attach(MIMEText(html_icerik, 'html'))
    
    # Gmail Sunucusuna Bağlanıp Gönderme
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GONDEREN_MAIL, UYGULAMA_SIFRESI)
        server.send_message(msg)
        server.quit()
        print("📨 Mail başarıyla gönderildi!")
    except Exception as e:
        print(f"❌ Mail gönderilirken bir hata oluştu: {e}")

# Dosya çalıştırıldığında bu blok devreye girer
if __name__ == "__main__":
    print("-" * 40)
    kritikler = kritik_stoklari_kontrol_et()
    
    if kritikler:
        uyari_maili_gonder(kritikler)
    else:
        print("✅ Stoklar güvende. İşlem tamamlandı.")
    print("-" * 40)