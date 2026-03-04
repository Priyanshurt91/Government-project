import cv2
import pytesseract
import numpy as np
from PIL import Image
import os

from ai.preprocess import preprocess_for_aadhaar, preprocess_for_pan, preprocess_generic


def _run_tesseract(processed_img, lang="eng", psm=6):
    """Run Tesseract with given config and return text."""
    custom_config = f"--oem 3 --psm {psm} -c preserve_interword_spaces=1"
    text = pytesseract.image_to_string(processed_img, lang=lang, config=custom_config)
    return text.strip()


def _best_ocr_pass(processed_img, lang="eng"):
    """
    Try multiple PSM modes and return the result with the most text.
    """
    best_text = ""
    for psm in [6, 3, 4]:
        text = _run_tesseract(processed_img, lang=lang, psm=psm)
        if len(text) > len(best_text):
            best_text = text
    return best_text


def extract_text_aadhaar(image_path: str):
    """
    OCR optimized for Aadhaar cards using multi-strategy approach.
    
    Runs 4 different preprocessing strategies and MERGES all results
    to maximize data extraction, since each strategy captures different
    parts of the card (name, father, DOB get garbled differently).
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not readable")

    h, w = img.shape[:2]
    scale = 2.0 if w < 1000 else 1.5
    resized = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    all_texts = []

    # Strategy 1: CLAHE + Otsu + PSM 4 (best overall on real cards)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(gray)
    _, thresh_clahe = cv2.threshold(cl, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text_clahe = _run_tesseract(thresh_clahe, lang="eng", psm=4)
    all_texts.append(text_clahe)

    # Strategy 2: Direct color image (captures DOB: label well)
    text_color = _run_tesseract(resized, lang="eng", psm=6)
    all_texts.append(text_color)

    # Strategy 3: Sharpened grayscale (gets Father name well)
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharp = cv2.filter2D(gray, -1, kernel)
    text_sharp = _run_tesseract(sharp, lang="eng", psm=6)
    all_texts.append(text_sharp)

    # Strategy 4: Aadhaar-specific preprocessing (CLAHE + denoise + Otsu)
    processed = preprocess_for_aadhaar(image_path)
    text_preprocess = _run_tesseract(processed, lang="eng", psm=6)
    all_texts.append(text_preprocess)

    # Merge: concatenate all unique lines from all strategies
    # This ensures we capture data from whichever strategy got it right
    seen_lines = set()
    merged_lines = []
    for text in all_texts:
        for line in text.split('\n'):
            line_stripped = line.strip()
            if line_stripped and line_stripped not in seen_lines:
                # Skip pure noise (less than 2 alphabetic chars)
                alpha_count = sum(1 for c in line_stripped if c.isalpha())
                if alpha_count >= 2 or any(c.isdigit() for c in line_stripped):
                    seen_lines.add(line_stripped)
                    merged_lines.append(line_stripped)

    merged_text = '\n'.join(merged_lines)
    return merged_text


def extract_text_pan(image_path: str):
    """
    OCR optimized for PAN cards.
    Uses PAN-specific preprocessing (crop to PAN region).
    """
    processed = preprocess_for_pan(image_path)
    return _best_ocr_pass(processed, lang="eng")


def extract_text(image_path: str):
    """
    Generic OCR function (backward compatible).
    Uses generic preprocessing with multi-pass OCR.
    """
    processed = preprocess_generic(image_path)
    text = _best_ocr_pass(processed, lang="eng")
    clean_text = " ".join(text.split())
    return clean_text
