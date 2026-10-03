import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

EXCEL_DOSYASI = "synthetic_production_log.xlsx"
DB_DOSYASI = "firin_yonetimi.db"

def ornek_excel_olustur():
    """Tamamen kurgusal, anonim endüstriyel üretim verisi üretir."""
    np.random.seed(42)
    firinlar = ["Unit-A (Tunnel)", "Unit-B (Chamber)", "Unit-C (Electric)", "Unit-D (Preheat)", "Unit-E (Dryer)"]
    prosesler = ["PR-HOT-1400", "PR-MID-850", "PR-LOW-400", "PR-DRY-150"]
    malzemeler = [
        ("SKU-1001", "Industrial Component Type-A"),
        ("SKU-1002", "Industrial Component Type-B"),
        ("SKU-2001", "Refractory Shield Element"),
        ("SKU-2002", "Structural Support Block"),
        ("SKU-3001", "Ceramic Insulator Panel")
    ]
    
    satirlar = []
    baslangic = datetime(2026, 1, 1)
    
    for i in range(1, 201):
        firin = np.random.choice(firinlar)
        proses = np.random.choice(prosesler)
        stok_kod, mat_ad = malzemeler[np.random.randint(0, len(malzemeler))]
        adet = int(np.random.randint(10, 150))
        kg = round(adet * np.random.uniform(5.5, 40.0), 2)
        sure_saat = int(np.random.choice([24, 48, 72, 96]))
        bas_tarih = baslangic + timedelta(days=int(np.random.randint(0, 30)))
        bit_tarih = bas_tarih + timedelta(hours=sure_saat)
        
        satirlar.append({
            "ORDER_ID": f"ORD-2026-{1000+i}",
            "UNIT_TAG": firin,
            "PROCESS_CODE": proses,
            "SKU_CODE": stok_kod,
            "ITEM_DESC": mat_ad,
            "QUANTITY": adet,
            "TOTAL_WEIGHT_KG": kg,
            "START_DATE": bas_tarih.strftime("%Y-%m-%d"),
            "END_DATE": bit_tarih.strftime("%Y-%m-%d"),
            "DURATION_HOURS": sure_saat
        })
        
    df = pd.DataFrame(satirlar)
    df.to_excel(EXCEL_DOSYASI, index=False)
    print(f"-> [1/2] Sentetik üretim kütüğü '{EXCEL_DOSYASI}' olarak oluşturuldu.")
    return df

def excel_to_sqlite():
    """Excel verisini işleyip ilişkisel SQLite tablolarına yazar."""
    if not os.path.exists(EXCEL_DOSYASI):
        ornek_excel_olustur()
        
    df = pd.read_excel(EXCEL_DOSYASI)
    conn = sqlite3.connect(DB_DOSYASI)
    
    # 1. Ana Geçmiş Tablosu
    df.to_sql("raw_sap_history", conn, if_exists="replace", index_label="id")
    
    # 2. Ünite Performans Özeti
    f_ozet = df.groupby("UNIT_TAG").agg(
        total_working_days=("DURATION_HOURS", lambda x: round(x.sum() / 24, 2)),
        campaign_count=("ORDER_ID", "count"),
        total_production_weight_tons=("TOTAL_WEIGHT_KG", lambda x: round(x.sum() / 1000, 2))
    ).reset_index().rename(columns={"UNIT_TAG": "furnace_name"})
    f_ozet.to_sql("knowledge_furnace_summary", conn, if_exists="replace", index_label="id")
    
    # 3. Proses Dağılım Özeti
    p_ozet = df.groupby("PROCESS_CODE").agg(
        campaign_count=("ORDER_ID", "count")
    ).reset_index().rename(columns={"PROCESS_CODE": "process_label"})
    p_ozet["preference_rank"] = p_ozet["campaign_count"].rank(ascending=False, method="dense").astype(int)
    p_ozet.to_sql("knowledge_process_summary", conn, if_exists="replace", index_label="id")
    
    # 4. Stok ve Envanter Tablosu
    inv_ozet = df.groupby(["SKU_CODE", "ITEM_DESC"]).agg(
        current_stock_level=("QUANTITY", lambda x: int(x.sum() * 0.8)),
        daily_consumption=("QUANTITY", lambda x: round(x.mean() * 0.2, 1))
    ).reset_index().rename(columns={"SKU_CODE": "stock_code", "ITEM_DESC": "material_name"})
    inv_ozet["production_iterations"] = np.random.randint(1, 10, size=len(inv_ozet))
    inv_ozet.to_sql("inventory_stock", conn, if_exists="replace", index_label="id")
    
    conn.commit()
    conn.close()
    print(f"-> [2/2] SQLite veritabanı '{DB_DOSYASI}' hazırlandı.")

if __name__ == "__main__":
    ornek_excel_olustur()
    excel_to_sqlite()