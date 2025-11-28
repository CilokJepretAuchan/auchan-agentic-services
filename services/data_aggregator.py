from calendar import monthrange
from core.supabase import supabase
from core.models import FinancialContext, CategoryStat, ProjectStat


def get_monthly_financial_context(org_id: str, month: int, year: int) -> FinancialContext:
    # 1. Setup Tanggal
    start_date = f"{year}-{month:02d}-01"
    _, last_day = monthrange(year, month)
    end_date = f"{year}-{month:02d}-{last_day}"

    # 2. Query Data (Org + Project)
    org_res = supabase.table("Organization").select(
        "name, Project(id, projectName, budgetAllocated)"
    ).eq("id", org_id).execute()

    if not org_res.data:
        raise ValueError("Organization not found")
    
    org_data = org_res.data[0]

    # 3. Query Transaksi (Filtered by Date)
    # Mengambil transaksi spesifik bulan ini saja
    tx_res = supabase.table("Transaction").select(
        "amount, projectId, Category(categoryName)"
    ).eq("orgId", org_id)\
     .gte("transactionDate", start_date)\
     .lte("transactionDate", end_date)\
     .execute()

    transactions = tx_res.data

    # 4. Processing / Aggregation Logic
    total_spent = 0.0
    cat_map = {}
    proj_spent_map = {}

    for t in transactions:
        amt = float(t["amount"])
        total_spent += amt
        
        # Kategori
        c_obj = t.get("Category")
        c_name = c_obj["categoryName"] if c_obj else "Uncategorized"
        cat_map[c_name] = cat_map.get(c_name, 0) + amt

        # Project
        if t.get("projectId"):
            pid = t["projectId"]
            proj_spent_map[pid] = proj_spent_map.get(pid, 0) + amt

    # 5. Format Output: Categories
    top_categories = []
    for name, amt in cat_map.items():
        pct = (amt / total_spent * 100) if total_spent > 0 else 0
        top_categories.append(CategoryStat(name=name, amount=amt, percentage=round(pct, 2)))
    
    # Sortir kategori
    top_categories.sort(key=lambda x: x.amount, reverse=True)

    # 6. Format Output: Projects
    projects_stats = []
    for p in org_data.get("Project", []):
        budget = float(p["budgetAllocated"] or 0)
        spent = proj_spent_map.get(p["id"], 0)
        
        # Tentukan status sederhana untuk konteks
        status = "Safe"
        if budget > 0:
            if spent > budget: status = "Critical"
            elif spent > (budget * 0.8): status = "Warning"

        projects_stats.append(ProjectStat(
            id=p["id"],
            name=p["projectName"],
            budget=budget,
            spent_this_month=spent,
            status=status
        ))

    return FinancialContext(
        org_name=org_data["name"],
        period=f"{month}-{year}",
        total_spent=total_spent,
        top_categories=top_categories[:5], # Ambil top 5 saja
        projects=projects_stats
    )