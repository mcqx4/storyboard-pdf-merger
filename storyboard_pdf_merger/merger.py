"""Core layout + PDF assembly logic."""
from __future__ import annotations
import csv
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# A4 in points (72dpi): 595 x 842 — universal printable size
PAGE_W, PAGE_H = 595, 842
MARGIN = 36


@dataclass
class Layout:
    name: str
    panels_per_page: int
    cols: int
    rows: int
    aspect_w: float
    aspect_h: float
    annotation_lines: int


LAYOUTS: dict[str, Layout] = {
    "6-panel": Layout("6-panel", 6, 2, 3, 16, 9, 4),
    "9-panel": Layout("9-panel", 9, 3, 3, 16, 9, 3),
    "12-panel-widescreen": Layout("12-panel-widescreen", 12, 3, 4, 2.39, 1, 2),
    "4-panel-detail": Layout("4-panel-detail", 4, 1, 4, 16, 9, 6),
    "8-panel-vertical": Layout("8-panel-vertical", 8, 4, 2, 9, 16, 3),
}


def _load_annotations(csv_path: str) -> dict[str, dict]:
    """Returns {filename: {scene, shot, type, intent, dialogue}}."""
    notes = {}
    if not csv_path or not os.path.exists(csv_path):
        return notes
    with open(csv_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fn = (row.get("filename") or "").strip()
            if fn:
                notes[fn] = row
    return notes


def _list_frames(input_dir: str) -> list[str]:
    """Return frame filenames sorted naturally."""
    exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    files = [f for f in os.listdir(input_dir)
             if os.path.splitext(f)[1].lower() in exts]
    # Natural sort: 1.png < 2.png < 10.png (not lexicographic)
    import re
    def nkey(s):
        return [int(t) if t.isdigit() else t.lower()
                for t in re.split(r"(\d+)", s)]
    files.sort(key=nkey)
    return [os.path.join(input_dir, f) for f in files]


def merge(input_dir: str, output_path: str,
          layout: str = "6-panel",
          aspect: Optional[str] = None,
          title: Optional[str] = None,
          annotations_csv: Optional[str] = None,
          dpi: int = 300) -> dict:
    """Merge image frames into a multi-page storyboard PDF.

    Returns: {"pages": int, "frames": int, "output": str, "size_kb": int}
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise RuntimeError("PyMuPDF not installed. Run: pip install PyMuPDF")

    if layout not in LAYOUTS:
        raise ValueError(f"Unknown layout: {layout}. Available: {list(LAYOUTS)}")

    lay = LAYOUTS[layout]

    # Optional aspect override (e.g., "16:9" -> 16/9)
    if aspect:
        try:
            aw, ah = aspect.split(":")
            lay = Layout(lay.name, lay.panels_per_page, lay.cols, lay.rows,
                          float(aw), float(ah), lay.annotation_lines)
        except Exception:
            pass

    frames = _list_frames(input_dir)
    if not frames:
        raise RuntimeError(f"No image files found in {input_dir}")

    notes = _load_annotations(annotations_csv) if annotations_csv else {}

    doc = fitz.open()
    content_top = MARGIN + 50
    content_w = PAGE_W - 2 * MARGIN
    content_h = PAGE_H - MARGIN - content_top - 30

    cell_w = (content_w - (lay.cols - 1) * 12) / lay.cols
    frame_w = cell_w
    frame_h = frame_w * lay.aspect_h / lay.aspect_w
    row_h = frame_h + 12 * lay.annotation_lines + 18

    page = None
    panel_index = 0  # within current page
    page_count = 0

    for idx, frame_path in enumerate(frames):
        if panel_index == 0:
            page = doc.new_page(width=PAGE_W, height=PAGE_H)
            page_count += 1
            # Header
            page.insert_text(fitz.Point(MARGIN, MARGIN + 14),
                              title or "Storyboard",
                              fontname="helv", fontsize=14, color=(0.18, 0.18, 0.18))
            page.insert_text(fitz.Point(PAGE_W - MARGIN - 80, MARGIN + 14),
                              f"Page {page_count}",
                              fontname="helv", fontsize=10, color=(0.18, 0.18, 0.18))
            page.draw_line(fitz.Point(MARGIN, MARGIN + 30),
                            fitz.Point(PAGE_W - MARGIN, MARGIN + 30),
                            color=(0.18, 0.18, 0.18), width=0.5)
            # Footer
            page.insert_text(fitz.Point(MARGIN, PAGE_H - MARGIN + 12),
                              "Generated with storyboard-pdf-merger · storyliner.online",
                              fontname="helv", fontsize=8, color=(0.5, 0.5, 0.5))

        col = panel_index % lay.cols
        row = panel_index // lay.cols
        x = MARGIN + col * (cell_w + 12)
        y = content_top + row * row_h

        # Frame number label
        fname = os.path.basename(frame_path)
        note = notes.get(fname, {})
        label = f"#{idx + 1}"
        if note.get("scene") and note.get("shot"):
            label = f"#{note['scene']}-{note['shot']}"
        page.insert_text(fitz.Point(x, y - 4), label,
                          fontname="hebo", fontsize=9, color=(0.18, 0.18, 0.18))

        # Insert image
        rect = fitz.Rect(x, y, x + frame_w, y + frame_h)
        try:
            page.insert_image(rect, filename=frame_path)
        except Exception as e:
            # Fallback — draw empty frame
            page.draw_rect(rect, color=(0.18, 0.18, 0.18), width=1.0)
            page.insert_text(fitz.Point(x + 4, y + 12),
                              f"[image error: {e}]",
                              fontname="helv", fontsize=7, color=(0.5, 0.5, 0.5))
        page.draw_rect(rect, color=(0.18, 0.18, 0.18), width=1.0)

        # Annotation lines
        ann_y = y + frame_h + 10
        for ln in range(lay.annotation_lines):
            line_y = ann_y + ln * 12
            page.draw_line(fitz.Point(x, line_y),
                            fitz.Point(x + frame_w, line_y),
                            color=(0.92, 0.91, 0.86), width=0.4)
        # If we have annotations, render shot type / intent
        if note:
            if note.get("type"):
                page.insert_text(fitz.Point(x + 2, ann_y + 8),
                                  note["type"],
                                  fontname="hebo", fontsize=7, color=(0.18, 0.18, 0.18))
            if note.get("intent"):
                page.insert_text(fitz.Point(x + 2, ann_y + 20),
                                  note["intent"][:60],
                                  fontname="helv", fontsize=7, color=(0.18, 0.18, 0.18))

        panel_index += 1
        if panel_index >= lay.panels_per_page:
            panel_index = 0

    doc.save(output_path)
    doc.close()

    size = os.path.getsize(output_path)
    return {
        "pages": page_count,
        "frames": len(frames),
        "output": output_path,
        "size_kb": round(size / 1024, 1),
    }
