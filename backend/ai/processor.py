import re
from ai.ocr import extract_text, extract_text_aadhaar, extract_text_pan
from ai.entity_extractor import extract_entities, extract_entities_aadhaar


def _detect_type_from_text(text):
    """Detect document type from already-extracted OCR text."""
    text_upper = text.upper()

    # Aadhaar detection
    aadhaar_score = 0
    aadhaar_keywords = ['AADHAAR', 'AADHAR', 'UIDAI', 'UNIQUE IDENTIFICATION',
                        'GOVERNMENT OF INDIA', 'ENROLMENT', 'VID',
                        'YEAR OF BIRTH', 'आधार']
    aadhaar_score = sum(1 for kw in aadhaar_keywords if kw in text_upper)
    if re.search(r'\b\d{4}\s*\d{4}\s*\d{4}\b', text):
        aadhaar_score += 2

    # PAN detection
    pan_score = 0
    pan_keywords = ['INCOME TAX', 'PERMANENT ACCOUNT', 'INCOME TAX DEPARTMENT']
    pan_score = sum(1 for kw in pan_keywords if kw in text_upper)
    if re.search(r'\b[A-Z]{5}\d{4}[A-Z]\b', text_upper):
        pan_score += 2

    if aadhaar_score >= 2:
        return 'aadhaar'
    elif pan_score >= 2:
        return 'pan'
    else:
        return 'generic'


def process_document(image_path: str):
    """
    Smart document processing with auto-detection.
    Does a single quick OCR pass for type detection, then uses the 
    specialized pipeline only if needed.
    """
    try:
        # Step 1: Quick single-pass OCR for detection
        quick_text = extract_text(image_path)
        doc_type = _detect_type_from_text(quick_text)

        # Step 2: Use specialized pipeline based on type
        if doc_type == 'aadhaar':
            # Aadhaar needs specialized OCR (full image, no crop)
            text = extract_text_aadhaar(image_path)
            entities = extract_entities_aadhaar(text)
        elif doc_type == 'pan':
            text = extract_text_pan(image_path)
            entities = extract_entities(text)
        else:
            # Generic — reuse the quick text we already have
            text = quick_text
            entities = extract_entities(text)

        return {
            "status": "success",
            "raw_text": text,
            "entities": entities,
            "doc_type": doc_type,
            "pan_required": False,
            "message": "Document processed successfully"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
