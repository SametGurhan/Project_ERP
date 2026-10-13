# 📦 CloudStock ERP - Kurumsal Kaynak Planlama ve Yönetim Sistemi

Bu proje, 20 günlük staj sürecinde gerçek ticari operasyonlar ve KOBİ ihtiyaçları göz önünde bulundurularak geliştirilmiş bulut tabanlı bir **Kurumsal Kaynak Planlama (ERP)** ve Envanter Yönetimi sistemidir.

---

## 🚀 Öne Çıkan Özellikler

* **📊 Envanter & Stok Yönetimi:** Ürün kataloglama, renk/beden bazlı varyant takibi, kritik stok seviyesi uyarıları ve toplu envanter işlemleri.
* **🤖 Yapay Zeka Destekli Tahminleme:** Geçmiş satış verilerini analiz ederek stokların ne zaman tükeneceğini öngören **Lineer Regresyon** modeli (`analiz.py`).
* **💰 Dinamik Fiyat Listeleri:** Toptan, perakende ve bayi gruplarına özel özelleştirilebilir fiyat çarpanları (`pages/fiyat_listeleri.py`).
* **📋 Malzeme İhtiyaç Planlaması (MRP):** Kritik seviyenin altındaki ürünler için otomatik tedarik ve bütçe hesaplama (`pages/mrp.py`).
* **📝 Fiziksel Sayım Mutabakatı:** Depo sayım sonuçlarını sisteme işleyerek anlık stok düzeltme (`pages/sayim.py`).
* **📄 Faturalandırma & PDF Önizleme:** Müşteri satışı gerçekleştirme, stoktan otomatik düşme ve yazdırılabilir resmi fatura çıktısı (`pages/faturalandirma.py`).
* **📨 Otomatik Uyarı Sistemi:** Kritik stoklardaki ürünleri tespit ederek e-posta yoluyla yetkiliye bildirim gönderme (`otomasyon.py`).

---

## 🛠️ Kullanılan Teknolojiler

* **Dil:** Python 3.x
* **Arayüz (Frontend):** Streamlit
* **Veritabanı:** SQLite (`cloudstock.db`)
* **Veri Analizi & AI:** Pandas, NumPy, Scikit-Learn
* **Görselleştirme & Tasarım:** HTML, CSS, JavaScript (Dinamik parçacık efektleri ve canlı saat entegrasyonu)

---

## 📂 Proje Mimarisi

```text
├── app.py                 # Ana Uygulama & Dashboard (Streamlit)
├── database.py            # Veritabanı ve CRUD İşlemleri Katmanı
├── analiz.py              # Yapay Zeka Stok Tahmin Modülü
├── otomasyon.py           # E-posta Uyarı ve Kontrol Servisi
├── pages/
│   ├── fiyat_listeleri.py # Dinamik Fiyat Listesi Modülü
│   ├── mrp.py             # Malzeme İhtiyaç Planlaması Modülü
│   ├── sayim.py           # Fiziksel Envanter Sayım Modülü
│   └── faturalandirma.py  # Satış & Fatura Oluşturucu
└── cloudstock.db          # İlişkisel SQLite Veritabanı
```

---

## ⚙️ Kurulum ve Çalıştırma

1. Projeyi klonlayın veya indirin:
   ```bash
   git clone https://github.com/kullanici-adin/cloudstock-erp.git
   cd cloudstock-erp
   ```

2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install streamlit pandas numpy scikit-learn
   ```

3. Veritabanını kurun ve örnek verileri yükleyin:
   ```bash
   python database.py
   ```

4. Uygulamayı başlatın:
   ```bash
   streamlit run app.py