"""
Image preprocessing utilities for OCR.
"""

from __future__ import annotations

import cv2
import numpy as np


def preprocess(image_path: str, mode: str = "basic") -> np.ndarray:
    """
    OCR-friendly preprocessing for handwritten images.

    Modes
    -----
    basic:
      grayscale -> gaussian blur -> fixed threshold
    adaptive:
      grayscale -> CLAHE contrast -> adaptive threshold -> light morphology
    """
    mode = (mode or "basic").strip().lower()
    if mode not in {"basic", "adaptive"}:
        raise ValueError(f"Unsupported preprocess mode: {mode}. Use 'basic' or 'adaptive'.")

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if mode == "basic":
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _ret, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)
        return thresh

    # adaptive mode
    # CLAHE helps with low-contrast scans (common in answer sheets).
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Adaptive threshold handles uneven lighting/shadows.
    # Use THRESH_BINARY to keep black text on white background generally.
    thresh = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,  # blockSize
        5,   # C
    )

    # Small cleanup to reduce speckle noise.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    return thresh

