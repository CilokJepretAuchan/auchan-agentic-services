import os
import uuid
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from faker import Faker

# --- 1. SETUP ---
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
fake = Faker('id_ID')
random.seed(12345) # Seed biar hasil konsisten

print("🚀 Memulai Seeding: Full Stack Anomalies (Gaussian + Budget + Dupes)...")

# --- 2. MASTER DATA ---
ORG_ID = str(uuid.uuid4())
org_data = [{"id": ORG_ID, "name": "BEM Sains dan Teknologi Terbarukan ", "code": "BEM-SAINS", "description": "Kabinet Sinergi", "createdAt": datetime.now().isoformat()}]

div_id = str(uuid.uuid4())
div_data = [{"id": div_id, "orgId": ORG_ID, "name": "Departemen PSDM"}]

user_ids = [str(uuid.uuid4()) for _ in range(5)]
users_data = [{"id": uid, "name": fake.name(), "email": fake.email(), "passwordHash": "x", "createdAt": datetime.now().isoformat()} for uid in user_ids]

# KATEGORI
cat_konsumsi_id = str(uuid.uuid4())
cat_atk_id = str(uuid.uuid4())
cat_sewa_id = str(uuid.uuid4())
cat_data = [
    {"id": cat_konsumsi_id, "orgId": ORG_ID, "categoryName": "Konsumsi"},
    {"id": cat_atk_id, "orgId": ORG_ID, "categoryName": "Perlengkapan & ATK"},
    {"id": cat_sewa_id, "orgId": ORG_ID, "categoryName": "Sewa Alat & Venue"}
]

# PROJECT (PROKER)
# 1. Proker Besar (Buat mainan Isolation Forest)
proj_ldk_id = str(uuid.uuid4())
# 2. Proker Kecil (Buat dijebolin budgetnya)
proj_workshop_id = str(uuid.uuid4())

proker_data = [
    {"id": proj_ldk_id, "orgId": ORG_ID, "divisionId": div_id, "projectName": "LDK Mahasiswa Baru", "budgetAllocated": 50_000_000},
    {"id": proj_workshop_id, "orgId": ORG_ID, "divisionId": div_id, "projectName": "Workshop Python Dasar", "budgetAllocated": 5_000_000} # Budget Cuma 5 Juta
]

trx_data = []

# --- 3. GENERATOR FUNCTIONS ---
def generate_gaussian(count, base_mean, sigma, cat_id, proj_id, desc_list):
    """Generate data rapat (Normal)"""
    for _ in range(count):
        amount = int(random.gauss(base_mean, sigma))
        amount = max(5000, amount)
        amount = round(amount, -2)
        
        trx_data.append({
            "id": str(uuid.uuid4()),
            "userId": random.choice(user_ids),
            "orgId": ORG_ID,
            "projectId": proj_id,
            "categoryId": cat_id,
            "amount": amount,
            "type": "EXPENSE",
            "description": random.choice(desc_list),
            "transactionDate": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat(),
            "status": "Pending",
            "createdAt": datetime.now().isoformat()
        })

# --- SKENARIO 1: STATISTICAL ANOMALY (ISOLATION FOREST) ---
print("📊 [1/3] Generating Gaussian Data (LDK Project)...")

# Data Normal (Background Noise)
# Nasi Kotak Rapat di 22.000
generate_gaussian(200, 22000, 1500, cat_konsumsi_id, proj_ldk_id, ["Nasi Ayam Bakar", "Nasi Padang", "Paket Bebek"])
# ATK Rapat di 15.000
generate_gaussian(100, 15000, 2000, cat_atk_id, proj_ldk_id, ["Spidol", "Kertas Plano", "Lakban"])

# INJECT: Mark-up Tipis (Invisible Anomaly)
print("   -> Injecting: Mark-up Nasi (42rb vs 22rb)...")
trx_data.append({
    "id": str(uuid.uuid4()),
    "userId": user_ids[0], "orgId": ORG_ID, "projectId": proj_ldk_id, "categoryId": cat_konsumsi_id,
    "amount": 42_500, # <-- ANOMALI IF
    "type": "EXPENSE", "description": "Nasi Kotak Spesial (Mark Up)",
    "transactionDate": datetime.now().isoformat(), "status": "Pending", "createdAt": datetime.now().isoformat()
})

# --- SKENARIO 2: BUDGET OVERRUN (RULE BASED) ---
print("💸 [2/3] Generating Budget Overrun (Workshop Project)...")

# Budget Workshop cuma 5.000.000
# Kita isi dulu pengeluaran wajar sampai mendekati limit (misal 4.2 Juta)
# Sewa Lab Komputer (Total 4.2jt)
generate_gaussian(2, 2_100_000, 100_000, cat_sewa_id, proj_workshop_id, ["Sewa Lab Komputer Hari 1", "Sewa Lab Komputer Hari 2"])

# INJECT: Transaksi Penghancur Budget
# Sisa budget: 800rb. Kita masukin transaksi 1.5 Juta.
# Total jadi 5.7 Juta -> OVERRUN!
print("   -> Injecting: Transaksi yang bikin boncos...")
trx_data.append({
    "id": str(uuid.uuid4()),
    "userId": user_ids[1], "orgId": ORG_ID, "projectId": proj_workshop_id, "categoryId": cat_konsumsi_id,
    "amount": 1_500_000, # <-- Bikin total jadi > 5jt
    "type": "EXPENSE", "description": "Konsumsi Peserta Workshop (Over Budget)",
    "transactionDate": datetime.now().isoformat(), "status": "Pending", "createdAt": datetime.now().isoformat()
})

# --- SKENARIO 3: DUPLICATE DATA (RULE BASED) ---
print("👯 [3/3] Generating Duplicate Transactions...")

dupe_user = user_ids[2]
dupe_amount = 350_000
dupe_desc = "Cetak Sertifikat Workshop"
dupe_date = (datetime.now() - timedelta(days=5)).isoformat()

# Transaksi Asli
trx_data.append({
    "id": str(uuid.uuid4()),
    "userId": dupe_user, "orgId": ORG_ID, "projectId": proj_workshop_id, "categoryId": cat_atk_id,
    "amount": dupe_amount,
    "type": "EXPENSE", "description": dupe_desc,
    "transactionDate": dupe_date, # Tanggal sama
    "status": "Approved", # Yang asli udah diapprove
    "createdAt": datetime.now().isoformat()
})

# Transaksi Duplikat (Copy Paste)
print("   -> Injecting: Double Claim Sertifikat...")
trx_data.append({
    "id": str(uuid.uuid4()),
    "userId": dupe_user, "orgId": ORG_ID, "projectId": proj_workshop_id, "categoryId": cat_atk_id,
    "amount": dupe_amount, # <-- Persis sama
    "type": "EXPENSE", "description": dupe_desc, # <-- Persis sama
    "transactionDate": dupe_date, # <-- Persis sama
    "status": "Pending", # Coba klaim lagi
    "createdAt": (datetime.now() + timedelta(minutes=5)).isoformat() # Submit 5 menit kemudian
})

# --- 4. EXECUTE INSERT ---
def safe_bulk_insert(table, data):
    if not data: return
    print(f"   Writing {len(data)} rows to {table}...")
    try:
        supabase.table(table).insert(data).execute()
    except Exception as e:
        print(f"❌ Error {table}: {e}")

print("\n--- Sending Data to Supabase ---")
safe_bulk_insert("Organization", org_data)
safe_bulk_insert("Division", div_data)
safe_bulk_insert("User", users_data)
safe_bulk_insert("Category", cat_data)
safe_bulk_insert("Project", proker_data)
safe_bulk_insert("Transaction", trx_data)

print("\n🎉 Selesai! Dataset Ormawa kamu sekarang punya:")
print("   1. Mark-up Halus (Rp 42.500) -> Makanan Isolation Forest")
print("   2. Budget Boncos (Total 5.7jt / 5jt) -> Makanan Rule Checker")
print("   3. Nota Ganda (Rp 350.000) -> Makanan Duplicate Checker")