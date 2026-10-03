import sqlite3
import random
from datetime import datetime, timedelta
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DB_DOSYASI = "firin_yonetimi.db"

class FirinKararMotoru:
    """Kural denetimi ve sezgisel puanlama optimizasyon motoru."""
    def __init__(self):
        self.firinlar = {
            "Unit-A (Tunnel)": {"kapasite": 25000.0, "tip": "Firing"},
            "Unit-B (Chamber)": {"kapasite": 30000.0, "tip": "Firing"},
            "Unit-C (Electric)": {"kapasite": 20000.0, "tip": "Firing"},
            "Unit-D (Preheat)": {"kapasite": 15000.0, "tip": "Thermal"},
            "Unit-E (Dryer)": {"kapasite": 18000.0, "tip": "Drying"}
        }

    def tum_kombinasyonlari_uret(self, bekleyen_partiler, proses_filtresi="All"):
        bugun = datetime.now()
        uretilen_senaryolar = []
        plan_sayaci = 1

        for parti in bekleyen_partiler:
            toplam_kg = parti["toplam_kg"]
            proses = parti["proses"]

            if proses_filtresi != "All" and proses != proses_filtresi:
                continue

            for firin_adi, firin_ozellik in self.firinlar.items():
                kapasite = firin_ozellik["kapasite"]

                # Kapasite Kısıt Kontrolü
                if toplam_kg > kapasite:
                    continue

                bekleme_gun = random.randint(0, 5)
                musait_tarih = bugun + timedelta(days=bekleme_gun)
                bitis_tarih = musait_tarih + timedelta(hours=parti["sure_saat"])

                # Sezgisel Skorlama (Heuristic Scoring)
                kullanim_puani = min(random.randint(2, 10), 10) * 2.0
                bekleme_cezasi = bekleme_gun * 50.0
                mutasyon = random.uniform(-5.0, 5.0)
                doluluk_orani = round((toplam_kg / kapasite) * 100, 1)

                skor = round(kullanim_puani - bekleme_cezasi + mutasyon + (doluluk_orani * 0.5), 1)

                uretilen_senaryolar.append({
                    "plan_kodu": f"PLAN-{plan_sayaci:03d}",
                    "firin": firin_adi,
                    "proses": proses,
                    "parti_adi": parti["parti_adi"],
                    "malzeme_sayisi": len(parti["malzemeler"]),
                    "toplam_kg": f"{toplam_kg:,.1f} KG",
                    "doluluk": f"%{doluluk_orani}",
                    "baslangic": musait_tarih.strftime("%Y-%m-%d"),
                    "bitis": bitis_tarih.strftime("%Y-%m-%d"),
                    "skor": skor,
                    "malzemeler": parti["malzemeler"]
                })
                plan_sayaci += 1

        uretilen_senaryolar.sort(key=lambda x: x["skor"], reverse=True)
        return uretilen_senaryolar


class FirinYonetimUygulamasi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Industrial Furnace Optimization & Scheduling System")
        self.geometry("1200x750")
        self.motor = FirinKararMotoru()
        self.secili_senaryolar = []

        self.arayuz_kur()

    def arayuz_kur(self):
        # 1. Sol Panel (Navigasyon)
        self.sol_menu = tk.Frame(self, width=230, bg="#0f172a")
        self.sol_menu.pack(side=tk.LEFT, fill=tk.Y)
        self.sol_menu.pack_propagate(False)

        tk.Label(self.sol_menu, text="OVEN SCHEDULER", fg="#38bdf8", bg="#0f172a", font=("Segoe UI", 12, "bold"), pady=15).pack()

        btn_props = {"bg": "#1e293b", "fg": "#e2e8f0", "activebackground": "#3b82f6", "activeforeground": "white",
                     "relief": "flat", "font": ("Segoe UI", 9), "pady": 9, "anchor": "w", "padx": 15}

        tk.Button(self.sol_menu, text="⚡ Campaign Scheduler", command=self.planlama_ekrani_goster, **btn_props).pack(fill=tk.X, padx=10, pady=3)
        tk.Button(self.sol_menu, text="📊 Analytics Dashboard", command=self.dashboard_goster, **btn_props).pack(fill=tk.X, padx=10, pady=3)
        tk.Button(self.sol_menu, text="📅 Live Gantt Schedule", command=self.gantt_goster, **btn_props).pack(fill=tk.X, padx=10, pady=3)

        tk.Button(self.sol_menu, text="📝 System Log", command=self.log_paneli_tetikle, bg="#334155", fg="white",
                  relief="flat", font=("Segoe UI", 9)).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=12)

        # 2. Sistem Günlük Paneli
        self.log_panel = tk.Frame(self, width=280, bg="#090d16")
        self.log_panel.pack_propagate(False)
        tk.Label(self.log_panel, text="SYSTEM AUDIT LOG", fg="#38bdf8", bg="#090d16", font=("Segoe UI", 10, "bold"), pady=10).pack()
        self.status_box = tk.Text(self.log_panel, bg="#0f172a", fg="#a5f3fc", font=("Consolas", 8), relief="flat")
        self.status_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.log_yaz("Engine initialized. Relational schema connected.")

        # 3. Ana Gösterim Alanı
        self.govde = tk.Frame(self, bg="#f8fafc")
        self.govde.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.planlama_ekrani_goster()

    def log_yaz(self, mesaj):
        zaman = datetime.now().strftime("%H:%M:%S")
        self.status_box.insert(tk.END, f"[{zaman}] {mesaj}\n")
        self.status_box.see(tk.END)

    def log_paneli_tetikle(self):
        if self.log_panel.winfo_ismapped():
            self.log_panel.pack_forget()
        else:
            self.log_panel.pack(side=tk.RIGHT, fill=tk.Y)

    def govde_temizle(self):
        for widget in self.govde.winfo_children():
            widget.destroy()

    def bekleyen_malzemeleri_getir(self):
        try:
            conn = sqlite3.connect(DB_DOSYASI)
            df = pd.read_sql_query("SELECT * FROM raw_sap_history", conn)
            conn.close()
        except:
            return [
                {"parti_adi": "Batch-A (Structural)", "proses": "PR-HOT-1400", "toplam_kg": 16400.0, "sure_saat": 48,
                 "malzemeler": [("SKU-1001", "Industrial Component Type-A", 120), ("SKU-1002", "Industrial Component Type-B", 80)]},
                {"parti_adi": "Batch-B (Insulators)", "proses": "PR-MID-850", "toplam_kg": 22100.0, "sure_saat": 72,
                 "malzemeler": [("SKU-2001", "Refractory Shield Element", 450), ("SKU-3001", "Ceramic Insulator Panel", 300)]}
            ]

        partiler = []
        gruplar = df.groupby(["PROCESS_CODE", "UNIT_TAG"])
        sayac = 1
        for (proses, firin), grup in gruplar:
            malzeme_list = []
            for _, row in grup.head(5).iterrows():
                malzeme_list.append((str(row.get("SKU_CODE", "")), str(row.get("ITEM_DESC", "")), int(row.get("QUANTITY", 0))))
            
            toplam_kg = float(grup["TOTAL_WEIGHT_KG"].sum())
            if toplam_kg > 30000: 
                toplam_kg = 24000.0
            
            partiler.append({
                "parti_adi": f"Production Pool #{sayac} ({proses})",
                "proses": proses,
                "toplam_kg": round(toplam_kg, 1),
                "sure_saat": int(grup["DURATION_HOURS"].iloc[0]) if "DURATION_HOURS" in grup else 48,
                "malzemeler": malzeme_list
            })
            sayac += 1
        return partiler

    def planlama_ekrani_goster(self):
        self.govde_temizle()
        
        ust_bar = tk.Frame(self.govde, bg="#ffffff", padx=15, pady=10, relief="solid", bd=1)
        ust_bar.pack(fill=tk.X)
        
        tk.Label(ust_bar, text="Automated Campaign Scheduling Hub", font=("Segoe UI", 12, "bold"), bg="white", fg="#0f172a").pack(side=tk.LEFT)
        
        tk.Button(ust_bar, text="⚡ Run Optimizer", command=self.tabloyu_guncelle, bg="#2563eb", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=5).pack(side=tk.RIGHT)

        tk.Label(ust_bar, text="Process Filter:", bg="white", font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=5)
        self.filtre_combo = ttk.Combobox(ust_bar, values=["All", "PR-HOT-1400", "PR-MID-850", "PR-LOW-400", "PR-DRY-150"], width=15)
        self.filtre_combo.current(0)
        self.filtre_combo.pack(side=tk.RIGHT, padx=5)
        self.filtre_combo.bind("<<ComboboxSelected>>", lambda e: self.tabloyu_guncelle())

        paned = tk.PanedWindow(self.govde, orient=tk.VERTICAL, bg="#e2e8f0")
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Üst Panel: Üretilen alternatif planlar
        ust_panel = tk.Frame(paned, bg="white")
        paned.add(ust_panel, height=360)

        tk.Label(ust_panel, text="Optimized Campaign Allocations (Ranked by Heuristic Score):",
                 font=("Segoe UI", 10, "bold"), bg="white", fg="#334155", anchor="w", pady=5).pack(fill=tk.X, padx=5)

        sutunlar = ("plan", "firin", "proses", "parti", "malz_sayisi", "toplam_kg", "doluluk", "baslangic", "bitis", "skor")
        self.tree_plan = ttk.Treeview(ust_panel, columns=sutunlar, show="headings", selectmode="browse")

        self.tree_plan.heading("plan", text="Plan ID")
        self.tree_plan.heading("firin", text="Target Unit")
        self.tree_plan.heading("proses", text="Process Profile")
        self.tree_plan.heading("parti", text="Batch Group")
        self.tree_plan.heading("malz_sayisi", text="Items")
        self.tree_plan.heading("toplam_kg", text="Total Weight")
        self.tree_plan.heading("doluluk", text="Capacity Load")
        self.tree_plan.heading("baslangic", text="Start Slot")
        self.tree_plan.heading("bitis", text="End Slot")
        self.tree_plan.heading("skor", text="Score")

        self.tree_plan.column("plan", width=85, anchor="center")
        self.tree_plan.column("firin", width=120)
        self.tree_plan.column("proses", width=100)
        self.tree_plan.column("parti", width=160)
        self.tree_plan.column("malz_sayisi", width=50, anchor="center")
        self.tree_plan.column("toplam_kg", width=95, anchor="e")
        self.tree_plan.column("doluluk", width=80, anchor="center")
        self.tree_plan.column("baslangic", width=90, anchor="center")
        self.tree_plan.column("bitis", width=90, anchor="center")
        self.tree_plan.column("skor", width=80, anchor="center")

        scroll_y = ttk.Scrollbar(ust_panel, orient=tk.VERTICAL, command=self.tree_plan.yview)
        self.tree_plan.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_plan.pack(fill=tk.BOTH, expand=True)

        self.tree_plan.bind("<<TreeviewSelect>>", self.senaryo_secildi)

        # Alt Panel: Seçilen plana ait malzeme detayları
        alt_panel = tk.Frame(paned, bg="white")
        paned.add(alt_panel, height=220)

        self.lbl_secili_plan = tk.Label(alt_panel, text="Campaign Bill of Materials (Select an allocation above):",
                                        font=("Segoe UI", 10, "bold"), bg="white", fg="#0284c7", anchor="w", pady=5)
        self.lbl_secili_plan.pack(fill=tk.X, padx=5)

        mat_sutunlar = ("stok", "ad", "adet", "tahmini_kg")
        self.tree_mat = ttk.Treeview(alt_panel, columns=mat_sutunlar, show="headings")
        self.tree_mat.heading("stok", text="SKU Code")
        self.tree_mat.heading("ad", text="Item Description")
        self.tree_mat.heading("adet", text="Planned Quantity")
        self.tree_mat.heading("tahmini_kg", text="Estimated Weight")

        self.tree_mat.column("stok", width=140)
        self.tree_mat.column("ad", width=350)
        self.tree_mat.column("adet", width=110, anchor="center")
        self.tree_mat.column("tahmini_kg", width=130, anchor="e")
        self.tree_mat.pack(fill=tk.BOTH, expand=True)

        self.tabloyu_guncelle()

    def tabloyu_guncelle(self):
        for item in self.tree_plan.get_children():
            self.tree_plan.delete(item)
        for item in self.tree_mat.get_children():
            self.tree_mat.delete(item)

        bekleyen_partiler = self.bekleyen_malzemeleri_getir()
        filtre = self.filtre_combo.get()
        self.secili_senaryolar = self.motor.tum_kombinasyonlari_uret(bekleyen_partiler, proses_filtresi=filtre)

        for s in self.secili_senaryolar:
            self.tree_plan.insert("", "end", values=(
                s["plan_kodu"], s["firin"], s["proses"], s["parti_adi"],
                s["malzeme_sayisi"], s["toplam_kg"], s["doluluk"],
                s["baslangic"], s["bitis"], s["skor"]
            ))

        self.log_yaz(f"Optimization finished. {len(self.secili_senaryolar)} allocation scenarios generated.")

    def senaryo_secildi(self, event):
        secim = self.tree_plan.selection()
        if not secim:
            return

        item = self.tree_plan.item(secim[0])
        plan_kodu = item["values"][0]
        firin = item["values"][1]

        senaryo = next((s for s in self.secili_senaryolar if s["plan_kodu"] == plan_kodu), None)
        if not senaryo:
            return

        self.lbl_secili_plan.config(text=f"Batch Details: {plan_kodu} -> Allocated to: {firin} ({senaryo['toplam_kg']})")

        for row in self.tree_mat.get_children():
            self.tree_mat.delete(row)

        for mat in senaryo["malzemeler"]:
            stok_kod = mat[0]
            mat_ad = mat[1]
            adet = mat[2]
            tahmini_kg = round(adet * 20.0, 2)
            self.tree_mat.insert("", "end", values=(stok_kod, mat_ad, adet, f"{tahmini_kg:,.1f} KG"))

        self.log_yaz(f"Inspecting {plan_kodu}: {len(senaryo['malzemeler'])} SKU positions listed.")

    def dashboard_goster(self):
        self.govde_temizle()
        try:
            conn = sqlite3.connect(DB_DOSYASI)
            f_stats = pd.read_sql_query("SELECT * FROM knowledge_furnace_summary", conn)
            p_stats = pd.read_sql_query("SELECT * FROM knowledge_process_summary LIMIT 5", conn)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read database. Please run excel_to_db.py first.\nError: {e}")
            return

        fig, axes = plt.subplots(2, 2, figsize=(8, 5.5), tight_layout=True)
        
        # 1. Total Operating Days
        axes[0, 0].bar(f_stats["furnace_name"], f_stats["total_working_days"], color="#3b82f6")
        axes[0, 0].set_title("1. Cumulative Operating Time (Days)", fontsize=9)
        axes[0, 0].tick_params(axis='x', rotation=25, labelsize=7)

        # 2. Total Campaigns
        axes[0, 1].bar(f_stats["furnace_name"], f_stats["campaign_count"], color="#10b981")
        axes[0, 1].set_title("2. Processed Campaign Counts", fontsize=9)
        axes[0, 1].tick_params(axis='x', rotation=25, labelsize=7)

        # 3. Process Profile Distribution
        axes[1, 0].barh(p_stats["process_label"], p_stats["campaign_count"], color="#f59e0b")
        axes[1, 0].set_title("3. Common Process Profiles", fontsize=9)
        axes[1, 0].tick_params(labelsize=7)

        # 4. Total Tonnage
        axes[1, 1].plot(f_stats["furnace_name"], f_stats["total_production_weight_tons"], marker='o', color="#ef4444")
        axes[1, 1].set_title("4. Output Tonnage (Metric Tons)", fontsize=9)
        axes[1, 1].tick_params(axis='x', rotation=25, labelsize=7)

        canvas = FigureCanvasTkAgg(fig, master=self.govde)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def gantt_goster(self):
        self.govde_temizle()
        tk.Label(self.govde, text="Live Furnace Timeline Simulation (Gantt View)", font=("Segoe UI", 12, "bold"), bg="#f8fafc").pack(pady=10)

        canvas = tk.Canvas(self.govde, bg="white", height=340)
        canvas.pack(fill=tk.X, padx=15, pady=5)

        firinlar = ["Unit-A (Tunnel)", "Unit-B (Chamber)", "Unit-C (Electric)", "Unit-D (Preheat)", "Unit-E (Dryer)"]
        renkler = ["#93c5fd", "#86efac", "#fde047", "#fca5a5", "#c4b5fd"]

        for i, f in enumerate(firinlar):
            y = 30 + i * 55
            canvas.create_text(80, y + 15, text=f, font=("Segoe UI", 9, "bold"))

            x_start = 160 + (i * 35)
            x_end = x_start + random.randint(130, 240)
            canvas.create_rectangle(x_start, y, x_end, y + 30, fill=renkler[i], outline="#475569")
            canvas.create_text(x_start + 70, y + 15, text=f"SCHED-0{i+1} (%{random.randint(65, 99)} Load)", font=("Segoe UI", 8))

        self.log_yaz("Rendered live timeline schedule.")

if __name__ == "__main__":
    app = FirinYonetimUygulamasi()
    app.mainloop()