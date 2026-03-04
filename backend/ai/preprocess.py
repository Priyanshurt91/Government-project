import cv2
import numpy as np


def crop_pan_region(img):
    """
    Crop the region where PAN number usually appears.
    PAN number is generally located in the lower-middle area of the card.
    """
    h, w = img.shape[:2]

    crop = img[
        int(h * 0.55):int(h * 0.80),
        int(w * 0.20):int(w * 0.80)
    ]

    return crop


def preprocess_for_pan(image_path):
    """
    Preprocessing pipeline optimized for PAN cards.
    Keeps the existing PAN-specific crop and thresholding.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not found or invalid image path")

    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    img = crop_pan_region(img)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 5
    )
    return thresh


def preprocess_for_aadhaar(image_path):
    """
    Preprocessing pipeline optimized for Aadhaar cards.
    - Uses FULL image (no cropping — Aadhaar data is spread across the card)
    - CLAHE for contrast enhancement (works better than equalizeHist on colored cards)
    - Gentle denoising to preserve text
    - Otsu thresholding for cleaner binarization
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not found or invalid image path")

    # Upscale for better OCR accuracy
    h, w = img.shape[:2]
    if w < 1000:
        scale = 2.0
    else:
        scale = 1.5
    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # CLAHE for better contrast on Aadhaar cards (handles uneven lighting)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Gentle denoising — preserve text edges
    gray = cv2.fastNlMeansDenoising(gray, h=10)

    # Otsu thresholding — auto-selects optimal threshold
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh


def preprocess_generic(image_path):
    """
    Generic preprocessing for other document types (certificates, etc.)
    Uses full image with adaptive thresholding.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not found or invalid image path")

    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)

    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 2
    )
    return thresh


# Keep backward compatibility
def preprocess_image(image_path):
    """Legacy function — defaults to generic preprocessing."""
    return preprocess_generic(image_path)
