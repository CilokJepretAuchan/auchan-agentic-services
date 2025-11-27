import pandas as pd
import uuid
from sklearn.ensemble import IsolationForest
from datetime import datetime

class TransactionAnomalyDetector:
    def __init__(self, transactions_df, projects_df):
        """
        Inisialisasi dengan data transaksi dan data project (untuk info budget).
        """
        self.df = transactions_df.copy()
        self.projects_df = projects_df.copy()
        
        # Pastikan format tanggal benar
        self.df['transactionDate'] = pd.to_datetime(self.df['transactionDate'])
        
        # Tempat menyimpan hasil temuan
        self.anomalies_found = []

    def _step_1_detect_duplicates(self):
        """
        Mencari transaksi ganda (User sama, Jumlah sama, Waktu berdekatan/sama).
        """
        print("--- Step 1: Memeriksa Duplikat ---")
        
        # Kita anggap duplikat jika userId dan amount sama persis
        # Dalam kasus nyata, kita bisa tambah toleransi waktu
        duplicates = self.df[self.df.duplicated(subset=['userId', 'amount'], keep=False)]
        
        for index, row in duplicates.iterrows():
            report = {
                "id" : str(uuid.uuid4()),
                "transactionId": row['id'],
                "aiScore": 1.0, # Skor 1.0 berarti PASTI anomali
                "reason": "Duplicate Transaction Detected",
                "status": "Pending"
            }
            self.anomalies_found.append(report)
            print(f"⚠️  Duplikat ditemukan: ID {row['id']} - Rp {row['amount']}")

    def _step_2_check_budget_overrun(self):
        """
        Memeriksa apakah transaksi menyebabkan project over-budget.
        """
        print("\n--- Step 2: Memeriksa Budget Overrun ---")
        
        # Hitung total pengeluaran per project
        project_spend = self.df.groupby('projectId')['amount'].sum().reset_index()
        
        # Gabungkan dengan data budget project
        merged = pd.merge(project_spend, self.projects_df, left_on='projectId', right_on='id')
        
        for index, row in merged.iterrows():
            total_spent = row['amount']
            budget = row['budgetAllocated']
            project_name = row['projectName']
            
            # Jika pengeluaran > 100% budget
            if total_spent > budget:
                # Cari semua transaksi di project ini untuk ditandai
                related_trxs = self.df[self.df['projectId'] == row['projectId']]
                
                # Kita tandai transaksi terakhir yang bikin jebol
                suspicious_trx = related_trxs.iloc[-1] 
                
                report = {
                    "id" : str(uuid.uuid4()),
                    "transactionId": suspicious_trx['id'],
                    "aiScore": 0.8,
                    "reason": f"Project {project_name} Over Budget (Used: {total_spent}/{budget})",
                    "status": "Pending"
                }
                self.anomalies_found.append(report)
                print(f"⚠️  Budget Jebol: Project {project_name} sudah habis {total_spent} dari {budget}")

    def _step_3_ai_isolation_forest(self):
            """
            Menggunakan AI (Isolation Forest) dengan Scope SANGAT SPESIFIK:
            Dikelompokkan per PROJECT dan per KATEGORI.

            Agar 'Biaya Makan' di Project A tidak dicampur dengan Project B.
            """
            print("\n--- Step 3: Menjalankan AI (Contextual Isolation Forest) ---")

            # Validasi kolom wajib
            if 'projectId' not in self.df.columns or 'categoryId' not in self.df.columns:
                print("⚠️ Error: Kolom 'projectId' atau 'categoryId' hilang. Skip AI step.")
                return

            # --- PERUBAHAN UTAMA DI SINI ---
            # Kita groupby menggunakan LIST: ['projectId', 'categoryId']
            groups = self.df.groupby(['projectId', 'categoryId'])

            for (project_id, category_id), group_data in groups:

                # 1. Cek Kecukupan Data PER KELOMPOK
                # Tantangannya: Semakin spesifik grouping, data per group makin sedikit.
                # Kita set minimal 3 data aja biar sensitif (tapi idealnya 5-10).
                if len(group_data) < 7:
                    # Opsi: Kalau data project ini dikit, bisa fallback ke rata-rata global kategori (Opsional)
                    # print(f"   -> Skip {project_id}-{category_id}: Data kurang ({len(group_data)}).")
                    continue

                # 2. Persiapan Data
                X = group_data[['amount']].values

                # 3. Latih Model Spesifik untuk Konteks Ini
                # n_estimators=50: Kita kurangi dikit biar enteng karena datanya kecil
                clf = IsolationForest(contamination='auto', n_estimators=50, random_state=42)

                clf.fit(X)
                preds = clf.predict(X)      
                scores = clf.decision_function(X) 

                # 4. Deteksi Anomali
                anomaly_indices = group_data.index[preds == -1]

                for idx in anomaly_indices:
                    row = self.df.loc[idx]
                    score = abs(scores[group_data.index.get_loc(idx)])

                    # Filter Manual: Hanya flag jika nilai > Rata-rata (Mahal)
                    if row['amount'] < group_data['amount'].mean():
                        continue 

                    # Cek duplikasi report
                    if not any(d['transactionId'] == row['id'] for d in self.anomalies_found):
                        report = {
                            "id" : str(uuid.uuid4()),
                            "transactionId": row['id'],
                            "aiScore": float(score),
                            # Alasannya sekarang lebih detail
                            "reason": f"Anomali Spesifik Project '{project_id}' Kategori '{category_id}': Rp {row['amount']:,}",
                            "status": "Pending"
                        }
                        self.anomalies_found.append(report)
                        print(f"⚠️  AI ALERT: Project {project_id} | Kat: {category_id} | ID {row['id']} | Rp {row['amount']:,}")

    def run_pipeline(self):
        """
        Jalankan semua langkah secara berurutan.
        """
        self._step_1_detect_duplicates()
        self._step_2_check_budget_overrun()
        self._step_3_ai_isolation_forest()
        
        return self.anomalies_found

