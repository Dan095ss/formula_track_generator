"""Extract pages from a PDF, parse running headers, return column-ordered text.

The Mitsubishi Mirage 1999 service manual prints a running header on every
content page in the form:

    ENGINE <1.5L> - On-vehicle Service
    BRAKES - Service Specifications/Sealants

Body extraction uses the blocks API with column-aware sorting (left column
fully, then right column) so a 2-column page reads top-to-bottom-then-right.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import fitz

HEADER_DASH_RE = re.compile(r"^(.*?)\s*[-–—]\s*(.+)$")
PAGE_NUMBER_RE = re.compile(r"^\s*[0-9]{1,3}\s*[A-Z]?\s*-\s*[0-9]{1,4}\s*$")


@dataclass
class PageRecord:
    index: int
    raw_text: str
    header_left: str
    header_right: str
    is_title_page: bool


def extract_pages(pdf_path: Path) -> list[PageRecord]:
    pages: list[PageRecord] = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            header_left, header_right, is_title = _classify_page(page)
            text = _read_body(page)
            pages.append(PageRecord(
                index=i,
                raw_text=text,
                header_left=header_left.strip(),
                header_right=header_right.strip(),
                is_title_page=is_title,
            ))
    return pages


def _read_body(page: "fitz.Page") -> str:
    """Extract body text in column-aware reading order."""
    width = page.rect.width
    raw_blocks = page.get_text("blocks") or []
    blocks: list[tuple[float, float, str]] = []
    for b in raw_blocks:
        if len(b) < 5:
            continue
        x0, y0, _x1, _y1, text = b[0], b[1], b[2], b[3], b[4]
        if not isinstance(text, str):
            continue
        text = text.strip()
        if not text:
            continue
        blocks.append((x0, y0, text))

    column_split = width * 0.5
    blocks.sort(key=lambda t: (0 if t[0] < column_split else 1, t[1], t[0]))
    return "\n\n".join(b[2] for b in blocks)


def _classify_page(page: "fitz.Page") -> tuple[str, str, bool]:
    header_line = _find_running_header(page)
    if not header_line:
        return "", "", _looks_like_title_page(page)

    m = HEADER_DASH_RE.match(header_line)
    if not m:
        return header_line, "", False
    return m.group(1), m.group(2), False


def _find_running_header(page: "fitz.Page") -> str:
    height = page.rect.height
    blocks = page.get_text("dict")["blocks"]

    candidates: list[tuple[float, str]] = []
    for b in blocks:
        if "lines" not in b:
            continue
        for line in b["lines"]:
            spans = [s for s in line["spans"] if s["text"].strip()]
            if not spans:
                continue
            y = min(s["bbox"][1] for s in spans)
            if y > height * 0.12:
                continue
            text = " ".join(s["text"] for s in spans).strip()
            text = re.sub(r"\s+", " ", text)
            if PAGE_NUMBER_RE.match(text) or len(text) < 4:
                continue
            if "-" not in text and "–" not in text:
                continue
            candidates.append((y, text))

    if not candidates:
        return ""
    candidates.sort()
    return candidates[0][1]


def _looks_like_title_page(page: "fitz.Page") -> bool:
    blocks = page.get_text("dict")["blocks"]
    big_text = 0
    total_text = 0
    for b in blocks:
        if "lines" not in b:
            continue
        for line in b["lines"]:
            for span in line["spans"]:
                t = span["text"].strip()
                if not t:
                    continue
                total_text += len(t)
                if span["size"] >= 30:
                    big_text += len(t)
    if total_text == 0:
        return True
    return big_text / total_text > 0.4
