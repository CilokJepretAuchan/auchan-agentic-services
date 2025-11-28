import re
from reportlab.platypus import (
    SimpleDocTemplate, 
    Paragraph, 
    Table, 
    TableStyle, 
    Spacer,
    PageBreak,
    HRFlowable
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from supabase_auth import datetime

# Import model kamu (sesuaikan path-nya)
from crew.report_builder_crew.models import MonthlyReport
from dotenv import load_dotenv
import os

load_dotenv()
# --- KONFIGURASI WARNA ---
PRIMARY_COLOR = colors.HexColor("#1a237e") # Navy Blue
ACCENT_COLOR = colors.HexColor("#e8eaf6")  # Very Light Blue
HEADER_BG = colors.HexColor("#3949ab")     # Lighter Navy
TEXT_COLOR = colors.HexColor("#212121")    # Almost Black
RISK_COLOR = colors.HexColor("#c62828")    # Red for Alert

def clean_markdown(text: str) -> str:
    """
    Helper untuk mengubah markdown **bold** menjadi tag <b>bold</b> 
    agar terbaca oleh ReportLab, dan handle newline.
    """
    # Ganti **text** jadi <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Ganti newline jadi <br/>
    text = text.replace('\n', '<br/>')
    return text

def header_footer(canvas, doc):
    """Fungsi untuk membuat Header & Footer di setiap halaman"""
    canvas.saveState()
    
    # --- HEADER ---
    canvas.setFont('Helvetica-Bold', 10)
    canvas.setFillColor(PRIMARY_COLOR)
    canvas.drawString(30, A4[1] - 30, "LAPORAN KEUANGAN & OPERASIONAL")
    
    canvas.setStrokeColor(colors.lightgrey)
    canvas.line(30, A4[1] - 35, A4[0] - 30, A4[1] - 35) # Garis Header
    
    # --- FOOTER ---
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.grey)
    page_num = canvas.getPageNumber()
    text = f"Halaman {page_num}"
    canvas.drawRightString(A4[0] - 30, 30, text)
    
    canvas.restoreState()

def generate_monthly_report_pdf(data: MonthlyReport):
    load_dotenv()
    temp_path = os.getenv("TEMP_UPLOAD_DIR")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    unique_filename = f"monthly_report_{data.org_name}_{data.period.replace('-', '_')}_{ts}.pdf"
    output_path = os.path.join(temp_path, unique_filename)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    # --- STYLES ---
    styles = getSampleStyleSheet()
    
    # Custom Title
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=24,
        textColor=PRIMARY_COLOR,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    # Custom Header Section
    h2_style = ParagraphStyle(
        "CustomH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=PRIMARY_COLOR,
        spaceBefore=15,
        spaceAfter=10,
        borderPadding=(0, 0, 5, 0), # Garis bawah tipis
        borderColor=colors.lightgrey,
        borderWidth=0,
        borderRadius=0
    )

    # Body Text Normal
    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14, # Spasi antar baris lebih lega
        alignment=TA_JUSTIFY,
        textColor=TEXT_COLOR
    )

    # Info Box Style (Summary)
    summary_style = ParagraphStyle(
        "SummaryBox",
        parent=normal_style,
        backColor=ACCENT_COLOR,
        borderColor=PRIMARY_COLOR,
        borderWidth=1,
        borderPadding=10,
        borderRadius=5,
        textColor=TEXT_COLOR
    )

    story = []

    # ==========================================
    # 1. JUDUL & INFO DASAR
    # ==========================================
    story.append(Paragraph(f"Laporan Bulan {data.period}", title_style))
    story.append(Spacer(1, 10))

    # Info Organisasi dalam Tabel Kecil (Tanpa Border) biar rapi
    info_data = [
        [Paragraph("<b>Organisasi</b>", normal_style), Paragraph(f": {data.org_name}", normal_style)],
        [Paragraph("<b>Periode</b>", normal_style), Paragraph(f": {data.period}", normal_style)],
        [Paragraph("<b>Total Pengeluaran</b>", normal_style), Paragraph(f": <b>Rp {data.total_spent:,.0f}</b>", normal_style)]
    ]
    
    info_table = Table(info_data, colWidths=[4*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Spacer(1, 15))

    # ==========================================
    # 2. EXECUTIVE SUMMARY
    # ==========================================
    story.append(Paragraph("Ringkasan Eksekutif", h2_style))
    # Bersihkan markdown dari teks summary agar bolding-nya jalan
    clean_summary = clean_markdown(data.summary_text)
    story.append(Paragraph(clean_summary, summary_style))
    story.append(Spacer(1, 20))

    # ==========================================
    # 3. KATEGORI PENGELUARAN (Tabel)
    # ==========================================
    story.append(Paragraph("Analisis Kategori Pengeluaran", h2_style))
    
    cat_header = ["Kategori", "Jumlah (IDR)", "Porsi (%)"]
    cat_data = [cat_header]

    for cat in data.top_categories:
        cat_data.append([
            cat.name,
            f"Rp {cat.amount:,.0f}",
            f"{cat.percentage:.2f}%"
        ])

    t_cat = Table(cat_data, colWidths=[8*cm, 4*cm, 3*cm])
    
    # Style Tabel Modern (Belang-belang)
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),      # Header Biru
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),    # Teks Header Putih
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),            # Angka rata kanan
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),              # Nama rata kiri
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        # Row Striping (Belang)
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, ACCENT_COLOR]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    
    story.append(t_cat)
    story.append(Spacer(1, 20))

    # ==========================================
    # 4. STATUS PROYEK (Tabel)
    # ==========================================
    story.append(Paragraph("Status Anggaran Proyek", h2_style))
    
    proj_header = ["Nama Proyek", "Anggaran", "Terpakai", "Status"]
    proj_data = [proj_header]

    # Kita cek dulu baris mana yang Critical untuk diwarnai merah
    critical_rows = []

    for idx, proj in enumerate(data.projects):
        row_idx = idx + 1 # +1 karena ada header
        
        status_text = proj.status
        # Kalau Critical, teks statusnya kita warnai merah tebal
        if "Critical" in status_text or "Over" in status_text:
            status_text = f"<font color='red'><b>{proj.status}</b></font>"
            critical_rows.append(row_idx)
        
        proj_data.append([
            Paragraph(proj.name, normal_style), # Pakai Paragraph biar bisa wrap text panjang
            f"Rp {proj.budget:,.0f}",
            f"Rp {proj.spent_this_month:,.0f}",
            Paragraph(status_text, normal_style) # Pakai Paragraph biar bisa render tag warna
        ])

    t_proj = Table(proj_data, colWidths=[6*cm, 3.5*cm, 3.5*cm, 2.5*cm])
    
    proj_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (2, -1), 'RIGHT'), # Angka rata kanan
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, ACCENT_COLOR]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ])
    
    t_proj.setStyle(proj_style)
    story.append(t_proj)
    story.append(Spacer(1, 20))

    # ==========================================
    # 5. RISIKO & REKOMENDASI (List)
    # ==========================================
    
    # Layout 2 Kolom untuk Risiko dan Rekomendasi (Opsional)
    # Tapi biar simpel dan terbaca jelas ke bawah saja
    
    # --- RISIKO ---
    story.append(Paragraph("⚠️ Deteksi Risiko & Anomali", h2_style))
    if data.risk_flags:
        for risk in data.risk_flags:
            # Gunakan bullet point
            # Ambil value stringnya saja jika risk itu dict
            risk_text = risk['message'] if isinstance(risk, dict) else str(risk)
            clean_risk = clean_markdown(risk_text)
            
            p = Paragraph(f"• {clean_risk}", 
                          ParagraphStyle('Risk', parent=normal_style, textColor=RISK_COLOR))
            story.append(p)
            story.append(Spacer(1, 3))
    else:
        story.append(Paragraph("<i>Tidak ada risiko signifikan terdeteksi.</i>", normal_style))

    story.append(Spacer(1, 10))

    # --- REKOMENDASI ---
    story.append(Paragraph("💡 Rekomendasi Optimasi", h2_style))
    if data.optimization_suggestions:
        for tip in data.optimization_suggestions:
            clean_tip = clean_markdown(tip)
            p = Paragraph(f"• {clean_tip}", normal_style)
            story.append(p)
            story.append(Spacer(1, 3))

    # ==========================================
    # BUILD PDF
    # ==========================================
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"✅ PDF Report generated at: {output_path}")
    return output_path,unique_filename


def delete_temp_file(file_path: str):
    """Hapus file sementara setelah digunakan"""
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"🗑️ Temporary file deleted: {file_path}")