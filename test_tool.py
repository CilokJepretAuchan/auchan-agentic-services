
# from core.supabase import supabase

# def test_supabase_connection():
#     response = supabase.table("Category").select("*").execute()
#     return response


# from utils.custom_tools.docx_tool import DocxReaderTool

# def test_docx_reader_tool():
#     docx_tool = DocxReaderTool()
#     sample_path = "D:/CODING/PYTHON/AGENTIC AI/AuchanAgenticService/test/test.docx"  # Ganti dengan path file DOCX yang valid untuk testing
#     result = docx_tool._run(sample_path)
#     return result

# print(test_supabase_connection())

# from services.data_aggregator import get_monthly_financial_context

# import asyncio
# async def test_data_aggregator():
#     org_id = "dabb7758-4719-4c94-897c-a00fd6a7f218"  # Ganti dengan org_id yang valid untuk testing
#     month = 11
#     year = 2025
#     context = await get_monthly_financial_context(org_id, month, year)
#     return context

# print(asyncio.run(test_data_aggregator()))

from uuid import uuid4
from crew.report_builder_crew.models import MonthlyReport, CategoryStat, ProjectStat
from template.generator import generate_monthly_report_pdf

import uuid

# Asumsi Class/Model tetap sama seperti sebelumnya
# Kita hanya mengubah VALUE-nya agar output report terasa sangat cerdas/analitis.

report = MonthlyReport(
    org_name="PT Maju Mundur (Divisi Operasional)",
    period="11-2025",
    
    # Total Spending bulan ini
    total_spent=3710306.0,
    
    top_categories=[
        CategoryStat(
            name='Food & Beverages', 
            amount=2556000.0, 
            percentage=68.89
        ),
        CategoryStat(
            name='Utilities (Listrik & Air)', 
            amount=815000.0, 
            percentage=21.97
        ),
        CategoryStat(
            name='Raw Materials', 
            amount=279243.0, 
            percentage=7.53
        ),
        CategoryStat(
            name='Office Supplies', 
            amount=48063.0, 
            percentage=1.3
        ),
        CategoryStat(
            name='Decoration', 
            amount=12000.0, 
            percentage=0.32
        ),
    ],
    
    projects=[
        # Project 1: Sehat Walafiat (Under Budget)
        ProjectStat(
            id=str(uuid.uuid4()),
            name="Infest 1 (Annual Gathering)",
            budget=10000000.0,
            spent_this_month=2841243.0,
            status="Safe" 
        ),
        # Project 2: ANOMALI PARAH (Budget cuma 20rb, abis 800rb)
        ProjectStat(
            id=str(uuid.uuid4()),
            name="Infest 2 (Pilot Testing)",
            budget=20000.0,
            spent_this_month=869063.0,
            status="Critical"
        ),
    ],
    
    # --- BAGIAN INI KITA PERKAYA ISINYA (STRING NYA DI-BOMBARDIR INFO) ---
    summary_text=(
        "Laporan keuangan periode November 2025 menunjukkan total pengeluaran sebesar **IDR 3.710.306**. "
        "Struktur biaya didominasi secara signifikan oleh kategori **'Food & Beverages' (68.89%)**, "
        "yang mengindikasikan tingginya frekuensi kegiatan meeting atau konsumsi karyawan bulan ini. "
        "Secara operasional, Project 'Infest 1' berjalan sangat efisien dengan penyerapan anggaran baru mencapai 28%. "
        "Namun, perhatian khusus wajib diberikan pada Project 'Infest 2' yang mengalami **deviasi ekstrim**, "
        "dimana pengeluaran aktual melampaui anggaran sebesar 4.345%. Hal ini memicu alert anomali tingkat tinggi."
    ),
    
    optimization_suggestions=[
        "Lakukan konsolidasi vendor untuk kategori 'Food & Beverages'. Dengan volume transaksi IDR 2,5 Juta, perusahaan berpotensi mendapatkan diskon korporat 10-15% jika berlangganan pada satu katering tetap.",
        "Audit penggunaan listrik (Utilities) yang mencapai 21% dari total biaya. Pastikan kebijakan pemadaman AC & lampu otomatis setelah jam 18:00 diterapkan ketat untuk mengurangi beban biaya bulan depan.",
        "Segera lakukan 'Stop-Loss' atau pembekuan anggaran sementara pada Project 'Infest 2' sampai investigasi selisih biaya diselesaikan."
    ],
    
    risk_flags=[
        "CRITICAL ANOMALY: Project 'Infest 2' mengalami over-budget sebesar IDR 849.063 (Penggunaan 4345% dari budget IDR 20.000). Kemungkinan kesalahan input nominal atau indikasi fraud.",
        "HIGH CONCENTRATION RISK: 68% pengeluaran hanya bertumpu pada satu kategori (Food). Disarankan diversifikasi atau review kebijakan uang makan."
    ]
)


generate_monthly_report_pdf(report)

