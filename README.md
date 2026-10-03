# Endüstriyel Fırın Kampanya Planlama ve Karar Destek Sistemi (Prototip / Şablon)

> **Gizlilik ve Güvenlik Notu:**  
> Bu depodaki kaynak kodlar ve veri setleri, **şirket verilerinin gizliliği ve ticari sırların korunması** amacıyla tamamen anonimleştirilmiş ve sentetik verilerle yeniden kurgulanmıştır. Depo, gerçek üretim tesisindeki fırın operasyonlarının planlama mimarisini, veri işleme mantığını ve kural motorunu teknik olarak sergileyen fonksiyonel bir **şablon (mock-up/prototype)** niteliğindedir.

---

### 📌 Proje Kapsamı ve Amacı
Endüstriyel refrakter üretim tesislerinde; yüksek sıcaklıklı fırınların kapasite kısıtları, proses tipleri, fırın doluluk oranları ve bekleme süreleri göz önüne alınarak en uygun kampanya çizelgesinin otomatik olarak oluşturulmasını amaçlayan karar destek prototipidir.

---

### ⚙️ Sistem Neler İçerir ve Nasıl Çalışır?

1. **ETL ve Veri Ön İşleme Modülü (`excel_to_db.py` / `TumUrunlerKombinasyonRaporu`):**
   * SAP/ERP sistemlerinden gelen ham üretim dökümlerini okur.
   * Dinamik sütun eşleme (`MAKTX` / `MAKTX2`) yaparak veri standardizasyonu sağlar.
   * Aykırı değerleri (hatalı fırınlama süreleri, eksik stok kayıtları) filtreleyerek veriyi ilişkisel veritabanı şemasına (`SQLite`) aktarır.

2. **Sezgisel Karar ve Kural Motoru (`FirinKararMotoru`):**
   * **Kapasite ve Tonaj Kontrolü:** Toplam parti ağırlığının hedef fırının azami taşıma kapasitesini aşıp aşmadığını denetler; aşan senaryoları eler.
   * **Sezgisel Puanlama (Heuristic Scoring):** Fırın kullanım sıklığı, bekleme süresi cezası, doluluk yüzdesi ve stok öncelik katsayılarını birleştirerek her alternatif fırın için başarı skoru hesaplar.
   * **Çoklu Senaryo Üretimi:** Tek bir öneri yerine tüm fırın alternatiflerini tarayarak en yüksek puandan en düşüğe doğru sıralı plan havuzu üretir.

3. **Görselleştirme ve Yönetici Paneli (`firin_planlama_app.py`):**
   * **İkili Tablo Mimarisi (Treeview):** Üst tabloda fırın senaryolarını listeler; herhangi bir senaryoya tıklandığında alt tabloda o kampanyaya ait malzeme detaylarını (stok kodu, parça tanımı, adet, kg) dinamik olarak gösterir.
   * **Dinamik Fırın Gantt Çizelgesi:** Fırınların güncel doluluk ve zaman aralıklarını canlı olarak simüle eder.
   * **Analitik Dashboard:** Fırın bazlı kümülatif çalışma günleri, kampanya adetleri, proses tercih sıklıkları ve toplam üretim tonajlarını `Matplotlib` grafikleriyle sunar.
   * **Sistem Günlüğü (Log Console):** Karar motorunun adımlarını ve filtreleme süreçlerini gerçek zamanlı takip eder.

---

### 🛠️ Kullanılan Teknolojiler
* **Dil:** Python 3.x
* **Veri Analizi & Manipülasyon:** Pandas, NumPy
* **Veritabanı:** SQLite3
* **Arayüz (GUI) & Grafik:** Tkinter, Matplotlib
