from crewai import Task
from crew.report_builder_crew.models import MonthlyReport
from crew.report_builder_crew.agent import financial_analysis



report_build_task = Task(
        description="""
        Analisis data keuangan Organisasi Mahasiswa/Kepanitiaan berikut ini.
        
        DATA AGREGASI:
        {aggregated_data}
        
        INSTRUKSI KHUSUS (CAMPUS CONTEXT):
        
        1. Summary Text (Evaluasi Umum):
           - Buat 1 paragraf rangkuman kondisi kas bulan ini.
           - Highlight total pengeluaran dan kategori paling dominan.
           - Apakah pola pengeluarannya wajar untuk kegiatan mahasiswa?
           - Jika ada Proker (Project) status "Critical", sebutkan namanya dan nyatakan sebagai "Lampaui RAB".
           
        2. Optimization Suggestions (Saran Penghematan):
           - Berikan saran yang relevan dengan organisasi kampus.
           - Contoh: "Kurangi jajan rapat", "Cari sponsor untuk dekorasi", "Gunakan aula kampus daripada sewa luar".
           - Fokus pada top_categories yang paling boros.
           
        3. Risk Flags (Peringatan LPJ):
           - Cek list 'projects'. Jika status = "Critical" atau spent_this_month > budget:
             Buat peringatan bahwa ini dapat menyulitkan LPJ ke Dekanat/Kemahasiswaan.
           - Hitung persentase overspending.
        
        Output wajib dalam format JSON sesuai skema MonthlyReport.
        """,

        expected_output="""
{
  "org_name": "Nama Organisasi / User",
  "period": "MM-YYYY",
  "total_spent": 0,
  "top_categories": [
    {
      "name": "category_name",
      "amount": 0,
      "percentage": 0
    }
  ],
  "projects": [
    {
      "id": "00000000-0000-0000-0000-000000000000",
      "name": "Project Name",
      "budget": 0,
      "spent_this_month": 0,
      "status": "Safe"
    }
  ],
  "summary_text": "Ringkasan otomatis dari AI...",
  "optimization_suggestions": [
    "Saran penghematan atau strategi optimalisasi..."
  ],
  "risk_flags": [
    "Flag risiko terkait overspending atau kategori tertentu..."
  ]
}
""",

        agent=financial_analysis,
        output_pydantic=MonthlyReport
    )
