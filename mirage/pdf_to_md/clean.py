"""Text cleanup: drop running headers, join wrapped lines into paragraphs."""

from __future__ import annotations

import re

PAGE_NUMBER_LINE = re.compile(r"^\s*[0-9]{1,3}[A-Z]?\s*-\s*[0-9]{1,4}\s*$")
HYPHEN_BREAK = re.compile(r"([A-Za-z])-\s*\n\s*([a-z])")
MULTI_BLANK = re.compile(r"\n{3,}")
TRAILING_DOTS = re.compile(r"\.{3,}")
MULTI_SPACE = re.compile(r"[ \t]{2,}")

PARAGRAPH_END = re.compile(r"[.!?:;]\s*$")
ENUMERATION_START = re.compile(r"^(\s*[\-•·●○◦▪]|\s*[0-9]{1,2}[.)]\s|\s*[a-zA-Z][.)]\s)")

UNDERSCORE_NOISE = re.compile(r"^[_\s]{2,}$")
PSEUDO_BULLET = re.compile(r"(?:(?<=^)|(?<=[\s.;:]))l\s+(?=[A-Z])")
LEADING_PSEUDO_BULLET = re.compile(r"^l\s+(?=[A-Z])", re.M)


def clean_page_text(raw: str, header_left: str, header_right: str) -> str:
    """Return readable Markdown body for one page.

    Pipeline: drop headers → drop page numbers → reflow short lines into
    paragraphs → trim dotted leaders and excessive whitespace.
    """
    if not raw:
        return ""

    paragraphs = raw.split("\n\n")
    out: list[str] = []
    header_left_norm = _norm(header_left)
    header_right_norm = _norm(header_right)
    for para in paragraphs:
        cleaned = _clean_paragraph(para, header_left_norm, header_right_norm)
        if cleaned:
            out.append(cleaned)

    text = "\n\n".join(out)
    text = HYPHEN_BREAK.sub(r"\1\2", text)
    text = LEADING_PSEUDO_BULLET.sub("- ", text)
    text = PSEUDO_BULLET.sub("\n- ", text)
    text = re.sub(r" {2,}", " ", text)
    text = MULTI_BLANK.sub("\n\n", text)
    return text.strip()


def _clean_paragraph(para: str, header_left_norm: str, header_right_norm: str) -> str:
    lines = [ln.rstrip() for ln in para.splitlines()]
    keep: list[str] = []
    for ln in lines:
        if not ln.strip():
            continue
        if PAGE_NUMBER_LINE.match(ln):
            continue
        if UNDERSCORE_NOISE.match(ln):
            continue
        n = _norm(ln)
        if header_left_norm and n == header_left_norm:
            continue
        if header_right_norm and n == header_right_norm:
            continue
        if header_left_norm and header_right_norm:
            combined = (
                f"{header_left_norm} - {header_right_norm}",
                f"{header_left_norm} {header_right_norm}",
            )
            if n in combined:
                continue
        ln = TRAILING_DOTS.sub(" … ", ln)
        ln = MULTI_SPACE.sub(" ", ln)
        keep.append(ln)

    if not keep:
        return ""

    return _reflow(keep)


def _reflow(lines: list[str]) -> str:
    """Join wrapped lines that belong to the same paragraph.

    Heuristic: a line continues the previous one when both:
      - the previous line did NOT end with sentence-final punctuation, AND
      - the current line does NOT start with an enumeration marker.
    """
    chunks: list[list[str]] = [[]]
    for ln in lines:
        if not chunks[-1]:
            chunks[-1].append(ln)
            continue
        prev = chunks[-1][-1]
        if ENUMERATION_START.match(ln) or PARAGRAPH_END.search(prev):
            chunks.append([ln])
        else:
            chunks[-1].append(ln)

    paragraphs: list[str] = []
    for c in chunks:
        joined = " ".join(s.strip() for s in c if s.strip())
        joined = re.sub(r"\s+", " ", joined).strip()
        if joined:
            paragraphs.append(joined)
    return "\n\n".join(paragraphs)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().upper()


def join_section_pages(parts: list[str]) -> str:
    return "\n\n".join(p.strip() for p in parts if p.strip())
