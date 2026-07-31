import io
import logging
from pypdf import PdfReader

logger = logging.getLogger("ResumeParser")

def extract_text_from_pdf(file_bytes: bytes, max_chars: int = 50000) -> str:
    """
    Extracts text content from a PDF file provided as bytes.
    Limits the total characters to max_chars to avoid excessive input lengths.
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        
        extracted_text = []
        char_count = 0
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if char_count + len(text) > max_chars:
                # Add partial text to fit limit
                text_slice = text[:max_chars - char_count]
                extracted_text.append(text_slice)
                logger.info(f"PDF text extraction truncated at page {i+1} due to character limit.")
                break
            
            extracted_text.append(text)
            char_count += len(text)
            
        full_text = "\n".join(extracted_text).strip()
        
        if not full_text:
            raise ValueError("No text could be extracted from the PDF. The file might be scanned or image-only.")
            
        return full_text
        
    except Exception as e:
        logger.error(f"Error extracting PDF: {str(e)}")
        raise e
