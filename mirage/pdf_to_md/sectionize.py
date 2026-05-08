"""Group consecutive PDF pages with the same running-header section into Sections."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .clean import clean_page_text, join_section_pages
from .extract import PageRecord


@dataclass
class Section:
    title: str
    page_start: int       # 1-based
    page_end: int         # 1-based, inclusive
    body_md: str = ""
    pages: list[int] = field(default_factory=list)


def build_sections(pages: list[PageRecord]) -> list[Section]:
    """Walk pages, group runs that share a header_right, emit Sections."""
    sections: list[Section] = []
    current: Section | None = None
    current_parts: list[str] = []

    for p in pages:
        if p.is_title_page:
            continue

        section_key = _section_key(p.header_right)
        if not section_key:
            section_key = "_unsectioned"

        if current is None or _section_key(current.title) != section_key:
            if current is not None:
                current.body_md = join_section_pages(current_parts)
                sections.append(current)
            current = Section(
                title=_pretty_title(p.header_right) or "Untitled section",
                page_start=p.index + 1,
                page_end=p.index + 1,
                pages=[p.index + 1],
            )
            current_parts = []
        else:
            current.page_end = p.index + 1
            current.pages.append(p.index + 1)

        cleaned = clean_page_text(p.raw_text, p.header_left, p.header_right)
        if cleaned:
            current_parts.append(cleaned)

    if current is not None:
        current.body_md = join_section_pages(current_parts)
        sections.append(current)

    if not sections:
        merged_body = join_section_pages([
            clean_page_text(p.raw_text, p.header_left, p.header_right)
            for p in pages if not p.is_title_page
        ])
        if merged_body:
            sections.append(Section(
                title="Полный текст",
                page_start=1,
                page_end=len(pages),
                body_md=merged_body,
                pages=list(range(1, len(pages) + 1)),
            ))

    return sections


_SECTION_ALIASES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^ON[ -]?VEHICLE( SERVICE)?$", re.I),       "On-vehicle Service"),
    (re.compile(r"^TROUBLE[ -]?SHOOTING.*$", re.I),          "Troubleshooting"),
    (re.compile(r"^GENERAL( INFORMATION)?$", re.I),          "General Information"),
    (re.compile(r"^SERVICE( SPECIFICATIONS?)?$", re.I),      "Service Specifications"),
    (re.compile(r"^SPECIAL TOOLS?$", re.I),                  "Special Tools"),
    (re.compile(r"^LUBRICANTS?$", re.I),                     "Lubricants"),
    (re.compile(r"^SEALANTS?( AND ADHESIVES?)?$", re.I),     "Sealants and Adhesives"),
]


def _section_key(title: str) -> str:
    s = re.sub(r"[/_,.]+", " ", title)
    s = re.sub(r"\s+", " ", s).strip().upper()
    for pat, canon in _SECTION_ALIASES:
        if pat.match(s):
            return canon.upper()
    return s


def _pretty_title(raw: str) -> str:
    if not raw:
        return ""
    s = re.sub(r"\s+", " ", raw).strip()
    s = s.split("/")[0].strip()
    s_upper = s.upper()
    for pat, canon in _SECTION_ALIASES:
        if pat.match(s_upper):
            return canon
    if s.isupper() or s.islower():
        return s.title()
    return s
