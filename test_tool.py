
from core.supabase import supabase

def test_supabase_connection():
    response = supabase.table("Category").select("*").execute()
    return response


from utils.custom_tools.docx_tool import DocxReaderTool

def test_docx_reader_tool():
    docx_tool = DocxReaderTool()
    sample_path = "D:/CODING/PYTHON/AGENTIC AI/AuchanAgenticService/test/test.docx"  # Ganti dengan path file DOCX yang valid untuk testing
    result = docx_tool._run(sample_path)
    return result

print(test_docx_reader_tool())