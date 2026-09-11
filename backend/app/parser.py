import io
import logging
import re
from pypdf import PdfReader

logger = logging.getLogger("ResumeParser")

def audit_text_layer_integrity(raw_text: str) -> dict:
    """
    Audits the programmatic text layer of an ingested resume for Unicode integrity,
    broken font CMaps, and layout encoding traps (per ISO 19005-2 PDF/A standards).

    Detects:
    - Unicode Private Use Area (PUA) glyphs (\\uE000-\\uF8FF) caused by missing /ToUnicode mappings.
    - Unicode replacement characters (\\uFFFD) indicating text layer decode corruption.
    - Invisible / zero-width characters (\\u200B-\\u200D, \\uFEFF) that distort search indexing.

    :param raw_text: Raw or partially cleaned text extracted from the document
    :return: Dictionary containing text layer health score and detected anomalies
    """
    if not raw_text:
        return {
            "text_layer_health_score": 0,
            "is_searchable": False,
            "pua_glyph_count": 0,
            "replacement_char_count": 0,
            "zero_width_char_count": 0,
            "issues": ["Document contains no extractable text layer."]
        }

    # Detect Private Use Area glyphs (\uE000-\uF8FF)
    pua_matches = re.findall(r'[\uE000-\uF8FF]', raw_text)
    pua_count = len(pua_matches)

    # Detect Unicode replacement characters (\uFFFD)
    replacement_matches = re.findall(r'\uFFFD', raw_text)
    replacement_count = len(replacement_matches)

    # Detect zero-width characters
    zero_width_matches = re.findall(r'[\u200B\u200C\u200D\uFEFF]', raw_text)
    zero_width_count = len(zero_width_matches)

    score = 100
    issues = []

    if replacement_count > 0:
        penalty = min(40, replacement_count * 5)
        score -= penalty
        issues.append(
            f"Detected {replacement_count} replacement character(s) (\uFFFD). The PDF text stream may be corrupted or lack valid font encoding."
        )

    if pua_count > 0:
        penalty = min(40, pua_count * 4)
        score -= penalty
        issues.append(
            f"Detected {pua_count} Private Use Area (PUA) glyph(s) (\uE000-\uF8FF). Custom fonts without a /ToUnicode CMap render text unsearchable in ATS parsers."
        )

    if zero_width_count > 5:
        score -= 15
        issues.append(
            f"Detected {zero_width_count} zero-width or hidden characters. These can interfere with ATS tokenizer segmentation."
        )

    score = max(0, min(100, score))
    is_searchable = score >= 50 and len(raw_text.strip()) >= 30

    return {
        "text_layer_health_score": score,
        "is_searchable": is_searchable,
        "pua_glyph_count": pua_count,
        "replacement_char_count": replacement_count,
        "zero_width_char_count": zero_width_count,
        "issues": issues
    }


def audit_layout_linearization(raw_text: str) -> dict:
    """
    Audits the structural linearization of parsed resume text to detect
    multi-column reading-order traps, gutter collisions, and table fragmentation.

    Enterprise ATS engines (Taleo, Workday, Ashby, Daxtra) rely on vertical scanlines
    or recursive XY-cuts. Multi-column documents with horizontal gutters (<12pt) or
    divider rules often scramble left-and-right text streams into incoherent text soup.

    :param raw_text: Raw unnormalized text extracted directly from the document parser
    :return: Dictionary containing linearization score, risk tier, detected anomalies, and recommendations
    """
    if not raw_text or not raw_text.strip():
        return {
            "linearization_score": 0,
            "risk_tier": "Empty Document",
            "gutter_anomaly_lines": 0,
            "divider_count": 0,
            "is_linear_safe": False,
            "issues": ["No extractable text to audit layout linearization."]
        }

    lines = raw_text.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    non_empty_count = len(non_empty_lines)

    if non_empty_count == 0:
        return {
            "linearization_score": 0,
            "risk_tier": "Empty Document",
            "gutter_anomaly_lines": 0,
            "divider_count": 0,
            "is_linear_safe": False,
            "issues": ["Document contains only whitespace."]
        }

    gutter_anomaly_lines = 0
    divider_matches = 0
    issues = []

    for line in non_empty_lines:
        # Check for wide horizontal gutter spaces (>= 4 consecutive spaces or tabs between words)
        if re.search(r'\S+(\t| {4,})\S+', line):
            gutter_anomaly_lines += 1

        # Check for ASCII table borders or dividers: +---+, |---|, =====, _____
        if re.search(r'(\+{2,}|[\|\-_=]{4,})', line):
            divider_matches += 1

    score = 100

    # Calculate gutter penalty
    gutter_ratio = gutter_anomaly_lines / non_empty_count
    if gutter_ratio > 0.35:
        score -= 45
        issues.append(
            f"High multi-column density detected ({gutter_anomaly_lines} lines have wide gutter gaps). Standard ATS parsers may scramble reading order across columns."
        )
    elif gutter_ratio > 0.15:
        score -= 25
        issues.append(
            f"Moderate multi-column layout risk detected ({gutter_anomaly_lines} lines with wide spacing). Ensure critical contact information and skills are not in sidebars."
        )

    # Calculate table/divider penalty
    if divider_matches > 5:
        score -= 20
        issues.append(
            f"Detected {divider_matches} ASCII table or divider patterns. Complex tables frequently cause OCR bounding-box collapse."
        )
    elif divider_matches > 2:
        score -= 10
        issues.append(
            f"Detected {divider_matches} divider lines. Consider replacing ASCII dividers with native standard whitespace."
        )

    score = max(0, min(100, score))

    if score >= 80:
        risk_tier = "Safe Single-Column"
    elif score >= 55:
        risk_tier = "Moderate Multi-Column Risk"
    else:
        risk_tier = "High Reading-Order Trap Risk"

    return {
        "linearization_score": score,
        "risk_tier": risk_tier,
        "gutter_anomaly_lines": gutter_anomaly_lines,
        "divider_count": divider_matches,
        "is_linear_safe": score >= 75,
        "issues": issues
    }



def clean_extracted_text(text: str) -> str:
    """
    Cleans and normalizes extracted text to optimize LLM token usage:
    - Removes null bytes and non-printable control characters.
    - Replaces 3 or more consecutive newlines with 2 newlines.
    - Replaces multiple whitespace/tabs with a single space.
    - Strips leading/trailing whitespaces.
    
    :param text: Raw extracted string from document
    :return: Normalized, token-efficient text string
    """
    # Remove null bytes and unwanted control characters (except newline and tab)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Remove zero-width characters that disrupt tokenization
    text = re.sub(r'[\u200B\u200C\u200D\uFEFF]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()



def extract_text_from_pdf(file_bytes: bytes, max_chars: int = 50000) -> tuple[str, int]:
    """
    Extracts text content and page metadata from a PDF file provided as bytes.
    Limits total character ingestion to max_chars to avoid excessive token overhead.

    :param file_bytes: Raw binary payload of the PDF document
    :param max_chars: Maximum character limit for ingestion (default: 50,000)
    :return: Tuple of (cleaned_extracted_text, total_page_count)
    :raises ValueError: When no extractable text is found (e.g., scanned/image-only PDF)
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        total_pages = len(reader.pages)
        
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
            
        full_text = clean_extracted_text("\n".join(extracted_text))
        
        if not full_text:
            raise ValueError("No text could be extracted from the PDF. The file might be scanned or image-only.")
            
        return full_text, total_pages
        
    except Exception as e:
        logger.error(f"Error extracting PDF: {str(e)}")
        raise e

def extract_text_from_docx(file_bytes: bytes, max_chars: int = 50000) -> str:
    """
    Extracts text content from a DOCX file provided as bytes.
    """
    try:
        import docx
        doc_file = io.BytesIO(file_bytes)
        doc = docx.Document(doc_file)
        
        extracted_text = []
        char_count = 0
        
        for paragraph in doc.paragraphs:
            text = paragraph.text or ""
            if char_count + len(text) + 1 > max_chars:
                text_slice = text[:max_chars - char_count]
                extracted_text.append(text_slice)
                break
            extracted_text.append(text)
            char_count += len(text) + 1
            
        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    row_text.append(cell.text.strip())
                text = " | ".join(row_text)
                if char_count + len(text) + 1 > max_chars:
                    text_slice = text[:max_chars - char_count]
                    extracted_text.append(text_slice)
                    break
                extracted_text.append(text)
                char_count += len(text) + 1
                
        full_text = clean_extracted_text("\n".join(extracted_text))
        
        if not full_text:
            raise ValueError("No text could be extracted from the DOCX file.")
            
        return full_text
    except Exception as e:
        logger.error(f"Error extracting DOCX: {str(e)}")
        raise e

def extract_text_from_txt(file_bytes: bytes, max_chars: int = 50000) -> str:
    """
    Extracts text content from a TXT file provided as bytes.
    """
    try:
        # Try decoding as utf-8, fallback to latin-1
        try:
            text = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            text = file_bytes.decode('latin-1')
            
        full_text = clean_extracted_text(text[:max_chars])
        
        if not full_text:
            raise ValueError("No text could be extracted from the TXT file.")
            
        return full_text
    except Exception as e:
        logger.error(f"Error extracting TXT: {str(e)}")
        raise e

