from typing import Type, List, Union, Iterator
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
import json
import os

# ------------------------------------------------------
# 1. Input Schema
# ------------------------------------------------------
class DocxReaderInput(BaseModel):
    file_path: str = Field(..., description="Path lokal file .docx.")

# ------------------------------------------------------
# 2. Main Tool Class
# ------------------------------------------------------
class DocxReaderTool(BaseTool):
    name: str = "DOCX Smart Reader (Table & Structure Focus)"
    description: str = (
        "Membaca dokumen DOCX. Halaman pertama diambil lengkap. "
        "Untuk halaman selanjutnya, hanya mengambil Heading, Posisi Gambar, dan SEMUA TABEL. "
        "Paragraf teks biasa di halaman selanjutnya diabaikan untuk hemat token."
    )
    args_schema: Type[BaseModel] = DocxReaderInput

    # ------------------------------------------------------
    # Helper: Iterasi Linear (Agar Teks & Tabel urut)
    # ------------------------------------------------------
    def _iter_block_items(self, parent) -> Iterator[Union[Paragraph, Table]]:
        """
        Generator untuk mengambil Paragraf dan Tabel sesuai urutan kemunculan di dokumen.
        """
        if isinstance(parent, _Document):
            parent_elm = parent.element.body
        else:
            parent_elm = parent._element

        for child in parent_elm.iterchildren():
            if isinstance(child, CT_P):
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)

    # ------------------------------------------------------
    # Helper: Deteksi Gambar
    # ------------------------------------------------------
    def _find_images_in_paragraph(self, paragraph, doc_part) -> List[str]:
        image_names = []
        blip_namespace = 'http://schemas.openxmlformats.org/drawingml/2006/main'
        rel_namespace = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        try:
            blips = paragraph._element.findall(f'.//{{{blip_namespace}}}blip')
            for blip in blips:
                embed_attr = blip.get(f'{{{rel_namespace}}}embed')
                if embed_attr and embed_attr in doc_part.related_parts:
                    image_part = doc_part.related_parts[embed_attr]
                    image_names.append(os.path.basename(image_part.partname))
        except Exception:
            pass 
        return image_names

    # ------------------------------------------------------
    # Helper: Ekstrak Data Tabel
    # ------------------------------------------------------
    def _extract_table_data(self, table: Table) -> List[List[str]]:
        data = []
        for row in table.rows:
            # Mengambil text dari setiap sel, skip yang kosong banget biar rapi
            row_data = [cell.text.strip() for cell in row.cells]
            # Hanya masukkan row jika ada isinya (menghindari row kosong melompong)
            if any(row_data): 
                data.append(row_data)
        return data

    # ------------------------------------------------------
    # Main Execution
    # ------------------------------------------------------
    def _run(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return "Error: File not found."

        try:
            doc = Document(file_path)
        except Exception as e:
            return f"Error loading doc: {e}"

        output_data = {
            "metadata": "Extracted with Table-Focus Mode",
            "content_flow": [] 
        }

        current_section = "Start of Document"
        is_first_page = True
        item_counter = 0
        FIRST_PAGE_ITEM_LIMIT = 30 # Asumsi 30 elemen pertama adalah halaman 1

        # Kita pakai iter_block_items supaya urutan Teks dan Tabel terjaga
        for block in self._iter_block_items(doc):
            item_counter += 1
            
            # Cek apakah kita sudah lewat halaman pertama (Logic sederhana based on counter)
            # (Bisa ditambah logic Page Break 'w:br' jika ingin lebih presisi)
            if item_counter > FIRST_PAGE_ITEM_LIMIT:
                is_first_page = False

            # -------------------------------
            # A. JIKA BLOCK ADALAH PARAGRAF
            # -------------------------------
            if isinstance(block, Paragraph):
                text = block.text.strip()
                style = block.style.name

                # 1. Cek Heading (Selalu update section, biar konteks tabel/gambar jelas)
                if style.startswith("Heading") and text:
                    current_section = text
                    output_data["content_flow"].append({
                        "type": "heading",
                        "text": text,
                        "level": style
                    })
                    continue # Lanjut ke next block

                # 2. Cek Gambar (Selalu ambil posisinya)
                images = self._find_images_in_paragraph(block, doc.part)
                if images:
                    output_data["content_flow"].append({
                        "type": "image_detected",
                        "filenames": images,
                        "context_section": current_section
                    })

                # 3. Cek Teks Biasa
                # Jika Halaman 1: AMBIL
                # Jika Halaman >1: SKIP (Kecuali Heading tadi)
                if is_first_page and text:
                    output_data["content_flow"].append({
                        "type": "text_intro",
                        "text": text
                    })

            # -------------------------------
            # B. JIKA BLOCK ADALAH TABEL
            # -------------------------------
            elif isinstance(block, Table):
                # Tabel SELALU diambil, tidak peduli halaman berapa
                table_content = self._extract_table_data(block)
                if table_content:
                    output_data["content_flow"].append({
                        "type": "table",
                        "context_section": current_section, # Penting: Tabel ini milik bab apa
                        "data": table_content
                    })

        return json.dumps(output_data, indent=2, ensure_ascii=False)