#!/usr/bin/env python3
"""
Generate labels.txt (pipe format) and labels_lmdb.txt (tab format) for deep-text-recognition-benchmark.

Auto-detects common CVL / IAM-style ground-truth files if --label-file is omitted.

Supported line formats in the label file:
  - filename<TAB>text
  - filename|text
  - filename.ext text with spaces...   (first token = image id)
  - 0001-1-0 text...                  (no extension → tries .jpg / .png / .jpeg on disk)

Usage:
  python generate_labels.py
  python generate_labels.py --image-folder handwrittendataset --label-file words.txt
  python generate_labels.py --image-folder handwrittendataset --output-dir dataset
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


# Prefer these names when auto-searching (order matters)
DEFAULT_LABEL_NAMES = (
    "transcription.txt",
    "words.txt",
    "lines.txt",
    "gt.txt",
    "ground_truth.txt",
    "labels_source.txt",
)


def normalize_label_text(text: str) -> str:
    """Lowercase + single spaces (matches typical CTC training charset)."""
    text = " ".join(text.split())
    return text.lower()


def parse_ground_truth_line(line: str) -> tuple[str, str] | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    if "\t" in line:
        left, right = line.split("\t", 1)
        return left.strip(), normalize_label_text(right)

    if "|" in line and not line.startswith("<"):  # avoid breaking XML-ish lines
        left, right = line.split("|", 1)
        return left.strip(), normalize_label_text(right)

    # First token = filename or id; rest = transcription
    parts = line.split(None, 1)
    if len(parts) < 2:
        return None
    left, right = parts[0], parts[1]
    return left.strip(), normalize_label_text(right)


def ensure_image_extension(key: str) -> str:
    """If key has no image extension, keep as-is (resolved later against disk)."""
    lower = key.lower()
    if lower.endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")):
        return key
    return key


def build_filename_index(image_dir: Path) -> dict[str, str]:
    """
    Map lowercase basename -> actual filename on disk (preserves case).
    """
    index: dict[str, str] = {}
    for name in os.listdir(image_dir):
        p = image_dir / name
        if not p.is_file():
            continue
        if name.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")):
            index[name.lower()] = name
    return index


def resolve_key_to_disk_name(key: str, index: dict[str, str]) -> str | None:
    """Map a key from the GT file to an actual filename in image_dir."""
    key = key.strip()
    if not key:
        return None

    k = ensure_image_extension(key)
    kl = k.lower()
    if kl in index:
        return index[kl]

    # Try adding extensions
    for ext in (".jpg", ".jpeg", ".png"):
        cand = (k if k.lower().endswith(ext) else k + ext).lower()
        if cand in index:
            return index[cand]

    # Key might be "0001-1-0" without extension
    base = Path(k).stem if "." in k else k
    for ext in (".jpg", ".jpeg", ".png"):
        cand = (base + ext).lower()
        if cand in index:
            return index[cand]

    return None


def find_label_file(image_dir: Path, project_root: Path) -> Path | None:
    search_roots = [image_dir, image_dir.parent, project_root]
    for root in search_roots:
        if not root.is_dir():
            continue
        for name in DEFAULT_LABEL_NAMES:
            p = root / name
            if p.is_file():
                return p
        # Any single .txt that looks like ground truth (not our outputs)
        for p in sorted(root.glob("*.txt")):
            if p.name in ("labels.txt", "labels_lmdb.txt", "requirements.txt"):
                continue
            # Heuristic: file has multiple lines with tab or two+ parts
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            lines = [ln for ln in txt.splitlines() if ln.strip() and not ln.strip().startswith("#")]
            if len(lines) >= 3:
                return p
    return None


def iter_ground_truth_pairs(label_path: Path) -> list[tuple[str, str]]:
    """List of (key_from_file, normalized_label)."""
    raw = label_path.read_text(encoding="utf-8", errors="replace").splitlines()
    pairs: list[tuple[str, str]] = []
    for line in raw:
        parsed = parse_ground_truth_line(line)
        if parsed:
            pairs.append(parsed)
    return pairs


def build_resolved_map(pairs: list[tuple[str, str]], index: dict[str, str]) -> dict[str, str]:
    """actual_filename_lower -> label (each GT line matched to one on-disk file)."""
    out: dict[str, str] = {}
    for key, text in pairs:
        resolved = resolve_key_to_disk_name(key, index)
        if resolved:
            out[resolved.lower()] = text
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate labels.txt from CVL-style ground truth.")
    parser.add_argument(
        "--image-folder",
        default="handwrittendataset",
        help="Folder containing line/word images (default: handwrittendataset)",
    )
    parser.add_argument(
        "--label-file",
        default="",
        help="Ground-truth file (tab, pipe, or 'filename text'). Auto-detected if omitted.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Where to write labels.txt and labels_lmdb.txt (default: current directory)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    image_dir = (project_root / args.image_folder).resolve()
    if not image_dir.is_dir():
        raise SystemExit(f"Image folder not found: {image_dir}")

    label_path: Path | None
    if args.label_file:
        label_path = Path(args.label_file)
        if not label_path.is_absolute():
            label_path = project_root / label_path
    else:
        label_path = find_label_file(image_dir, project_root)

    if not label_path or not label_path.is_file():
        raise SystemExit(
            "Could not find a ground-truth .txt file.\n"
            "Put transcription.txt / words.txt / lines.txt next to your images or project root,\n"
            "or pass: --label-file path/to/your_gt.txt"
        )

    print(f"Using label file: {label_path}")
    print(f"Image folder:     {image_dir}")

    pairs = iter_ground_truth_pairs(label_path)
    index = build_filename_index(image_dir)
    resolved_gt = build_resolved_map(pairs, index)

    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = project_root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    lines_pipe: list[str] = []
    lines_tab: list[str] = []
    missing: list[str] = []

    for actual_name in sorted(index.values(), key=lambda x: x.lower()):
        actual_lower = actual_name.lower()
        label = resolved_gt.get(actual_lower)
        if label is None:
            missing.append(actual_name)
            continue

        lines_pipe.append(f"{actual_name}|{label}")
        lines_tab.append(f"{actual_name}\t{label}")

    out_pipe = out_dir / "labels.txt"
    out_tab = out_dir / "labels_lmdb.txt"

    out_pipe.write_text("\n".join(lines_pipe) + ("\n" if lines_pipe else ""), encoding="utf-8")
    out_tab.write_text("\n".join(lines_tab) + ("\n" if lines_tab else ""), encoding="utf-8")

    print(f"Wrote {len(lines_pipe)} lines → {out_pipe}")
    print(f"Wrote {len(lines_tab)} lines → {out_tab} (tab-separated for create_lmdb_dataset.py)")

    if missing:
        print(f"\n⚠️  {len(missing)} images had no matching label (skipped). First few:")
        for m in missing[:15]:
            print(f"   - {m}")
        if len(missing) > 15:
            print("   ...")


if __name__ == "__main__":
    main()
