import os
import uuid
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from faker import Faker

# --- 1. SETUP ---
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Pastikan SUPABASE_URL dan SUPABASE_KEY ada di file .env")

supabase: Client = create_client(url, key)
fake = Faker('id_ID')
Faker.seed(42)

print("🚀 Memulai Seeding ke Supabase...")

# --- 2. GENERATOR DATA (Logika Cerdas) ---

# A. ORGANIZATION
print("📦 Generating Organization...")
ORG_ID = str(uuid.uuid4())
org_data = [{
    "id": ORG_ID,
    "name": "PT Maju Mundur Tech",
    "code": "MMT",
    "description": "Perusahaan Teknologi Dummy",
    "createdAt": datetime.now().isoformat()
}]

# B. USERS
print("👤 Generating Users...")
users_ids = [str(uuid.uuid4()) for _ in range(3)]
users_data = []
for uid in users_ids:
    users_data.append({
        "id": uid,
        "name": fake.name(),
        "email": fake.email(),
        "passwordHash": "dummy_hash_123",
        "createdAt": datetime.now().isoformat()
    })

# C. DIVISIONS
print("🏢 Generating Divisions...")
div_ids = [str(uuid.uuid4()) for _ in range(2)]
div_data = [
    {"id": div_ids[0], "orgId": ORG_ID, "name": "IT Infrastructure"},
    {"id": div_ids[1], "orgId": ORG_ID, "name": "Marketing Dept"}
]

# D. CATEGORIES
print("🏷️  Generating Categories...")
id_cat1 = str(uuid.uuid4())
id_cat2 = str(uuid.uuid4())
id_cat3 = str(uuid.uuid4())
cats = [
    {"id": id_cat1, "name": "Konsumsi"},
    {"id": id_cat2, "name": "Perjalanan Dinas"},
    {"id": id_cat3, "name": "Equipment IT"}
]
cat_data = []
for c in cats:
    cat_data.append({
        "id": c["id"],
        "orgId": ORG_ID,
        "categoryName": c["name"]
    })

# E. PROJECTS
print("scrum Generating Projects...")
id_proj1 = str(uuid.uuid4())
id_proj2 = str(uuid.uuid4())
proj_data = [
    # Project Besar (IT)
    {"id": id_proj1, "orgId": ORG_ID, "divisionId": div_ids[0], "projectName": "Upgrade Server", "budgetAllocated": 500_000_000},
    # Project Kecil (Marketing)
    {"id": id_proj2, "orgId": ORG_ID, "divisionId": div_ids[1], "projectName": "Outing Bali", "budgetAllocated": 10_000_000}
]

# F. TRANSACTIONS (Dengan Anomali)
print("💰 Generating Transactions...")
trx_data = []

def add_trx(proj_id, cat_id, amount, desc, user_idx=0, date_offset=None):
    if date_offset is None:
        date_offset = random.randint(1, 30)
        
    trx_data.append({
        "id": str(uuid.uuid4()),
        "userId": users_ids[user_idx],
        "orgId": ORG_ID,
        "projectId": proj_id,
        "categoryId": cat_id,
        "amount": amount,
        "type": "EXPENSE",       # Pastikan sesuai Enum di DB
        "description": desc,
        "transactionDate": (datetime.now() - timedelta(days=date_offset)).isoformat(),
        "status": "Pending",     # Pastikan sesuai Enum di DB
        "createdAt": datetime.now().isoformat()
    })

# 1. Normal Data (Outing - Makan Murah) -> Cluster Normal
for _ in range(15):
    add_trx(id_proj2, id_cat1, random.randint(40000, 70000), "Makan Siang Tim")

# 2. ANOMALI 1: Contextual (Makan Mahal di Project Kecil)
# Ini bakal kena detect Isolation Forest
add_trx(id_proj2, id_cat1, 4_500_000, "Makan Siang Sultan (Anomali)", user_idx=1)

# 3. ANOMALI 2: Budget Overrun (Project Small cuma 10jt, ini nambah 6jt)
add_trx(id_proj2, id_cat2, 6_000_000, "Tiket Pesawat Mendadak", user_idx=2)

# 4. ANOMALI 3: Duplikat
trx_amount = 2_500_000
trx_desc = "Tiket Kereta Eksekutif"
# Transaksi Asli
trx_id_asli = str(uuid.uuid4())
trx_data.append({
    "id": trx_id_asli,
    "userId": users_ids[0],
    "orgId": ORG_ID,
    "projectId": id_proj1,
    "categoryId": id_cat2,
    "amount": trx_amount,
    "type": "EXPENSE",
    "description": trx_desc,
    "transactionDate": datetime.now().isoformat(),
    "status": "Pending",
    "createdAt": datetime.now().isoformat()
})
# Transaksi Palsu (Duplikat)
trx_data.append({
    "id": str(uuid.uuid4()),      # ID Baru
    "userId": users_ids[0],       # User Sama
    "orgId": ORG_ID,
    "projectId": id_proj1,
    "categoryId": id_cat2,
    "amount": trx_amount,         # Jumlah Sama
    "type": "EXPENSE",
    "description": trx_desc,      # Deskripsi Sama
    "transactionDate": datetime.now().isoformat(), # Waktu Sama/Mirip
    "status": "Pending",
    "createdAt": (datetime.now() + timedelta(minutes=2)).isoformat()
})


# --- 3. EKSEKUSI INSERT KE SUPABASE ---
# Helper function biar rapi
def safe_insert(table_name, data):
    try:
        response = supabase.table(table_name).insert(data).execute()
        print(f"✅ {table_name}: Sukses insert {len(data)} baris.")
        return response
    except Exception as e:
        print(f"❌ {table_name}: Gagal! Error: {e}")
        # Lanjut terus biar gak stop total (opsional)

print("\n--- Sending Data to Supabase ---")

# Urutan HARUS sesuai Foreign Key
safe_insert("Organization", org_data)
safe_insert("User", users_data)       # Asumsi tabel User publik, bukan auth.users
safe_insert("Division", div_data)
safe_insert("Category", cat_data)
safe_insert("Project", proj_data)
safe_insert("Transaction", trx_data)

print("\n🎉 Selesai! Cek dashboard Supabase kamu.")