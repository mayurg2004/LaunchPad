import io
import pypdf
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_obj):
    """
    Extracts text from a given PDF file object.
    Returns the extracted text, or None if extraction fails.
    """
    try:
        # Read the file content into a bytes buffer
        # This works for both in-memory and disk-based Django File objects
        file_obj.seek(0)
        file_bytes = file_obj.read()
        
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        return text.strip()
    except pypdf.errors.PyPdfError as e:
        logger.error(f"PyPDF Error parsing PDF: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing PDF: {e}")
        return None
