"""
EasyOCR wrapper for answer-sheet text extraction.

First call loads models (slow + may download weights). Reuse this module in FastAPI.
"""

from __future__ import annotations

from typing import Any

import easyocr
import numpy as np

# Lazy singleton — created on first use
_reader: easyocr.Reader | None = None


def _get_reader(languages: list[str] | None = None, gpu: bool | None = None) -> easyocr.Reader:
    global _reader
    if _reader is not None:
        return _reader

    if languages is None:
        languages = ["en"]

    if gpu is None:
        try:
            import torch

            gpu = bool(torch.cuda.is_available())
        except Exception:
            gpu = False

    # gpu=True requires CUDA; falls back safely if you force gpu=False
    _reader = easyocr.Reader(languages, gpu=gpu)
    return _reader


def extract_text_from_image(
    image: np.ndarray,
    *,
    languages: list[str] | None = None,
    gpu: bool | None = None,
) -> str:
    """
    Run EasyOCR on an in-memory image (NumPy array) and return one text string.
    """
    reader = _get_reader(languages=languages, gpu=gpu)
    results = reader.readtext(image)

    # Sort roughly top-to-bottom, left-to-right for multi-line / answer sheets
    def sort_key(item: tuple[Any, str, float]) -> tuple[float, float]:
        bbox, _text, _prob = item
        ys = [p[1] for p in bbox]
        xs = [p[0] for p in bbox]
        return (sum(ys) / len(ys), sum(xs) / len(xs))

    results = sorted(results, key=sort_key)

    parts: list[str] = []
    for _bbox, text, _prob in results:
        t = text.strip()
        if t:
            parts.append(t)

    return " ".join(parts).strip()


def extract_text(
    image_path: str,
    *,
    languages: list[str] | None = None,
    gpu: bool | None = None,
) -> str:
    """
    Backward-compatible helper: run OCR directly from image path.
    """
    import cv2

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")
    return extract_text_from_image(img, languages=languages, gpu=gpu)


def reset_reader() -> None:
    """Useful in tests to force reload with different gpu/lang settings."""
    global _reader
    _reader = None
