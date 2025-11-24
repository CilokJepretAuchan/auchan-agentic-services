from datetime import datetime
from uuid import uuid4
from core.supabase import supabase
from crew.extractor_crew.models import ExtractedDocumentOutput  # supabase client sync

def map_transactions(
    extracted_doc: ExtractedDocumentOutput,
    user_id: str,
    org_id: str,
    project_id: str,
):
    """
    Mapping transaksi + auto-create kategori jika belum ada (sync version).
    """

    # ---------------------------------------------
    # 1. Ambil semua kategori existing
    # ---------------------------------------------
    category_res = supabase.table("Category") \
        .select("*") \
        .eq("orgId", org_id) \
        .execute()

    existing_categories = category_res.data or []

    # Map kategori: {"food": "uuid-123"}
    category_map = {c["categoryName"].lower(): c["id"] for c in existing_categories}

    mapped = []
    now = datetime.utcnow().isoformat()

    # ---------------------------------------------
    # Helper: create kategori jika belum ada
    # ---------------------------------------------
    def create_category_if_needed(type_name: str):
        key = type_name.lower()
        print("Checking category:", key)
        print("Existing categories:", category_map)
        # Jika sudah ada, kembalikan ID-nya
        if key in category_map:
            return category_map[key]

        # Buat kategori baru
        new_id = str(uuid4())
        payload = {
            "id": new_id,
            "categoryName": type_name,
            "orgId": org_id,
        }

        supabase.table("Category").insert(payload).execute()

        category_map[key] = new_id
        return new_id

    # ---------------------------------------------
    # 2. Proses transaksi
    # ---------------------------------------------
    for t in extracted_doc.transactions:
        category = t.category or "Uncategorized"

        category_id = create_category_if_needed(category)

        mapped.append({
            "id": str(uuid4()),
            "amount": t.amount,
            "type": t.type,
            "description": t.description,
            "transactionDate": now,
            "userId": user_id,
            "orgId": org_id,
            "projectId": project_id,
            "categoryId": category_id,
            "aiAnomalyScore": None,
            "blockchainHash": None,
            "blockchainTxId": None,
            "createdAt": now,
        })

    return mapped
