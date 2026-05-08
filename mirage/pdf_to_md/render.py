"""Render a Section into a Markdown file with YAML frontmatter."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import yaml

from .config import PdfTarget, VEHICLE_LINK, slugify
from .sectionize import Section


def render_note(target: PdfTarget, section: Section, total_in_chapter: int) -> tuple[str, str]:
    """Return (filename, full_markdown_text) for one section."""
    fname = _make_filename(target, section)

    page_range = (
        f"{section.page_start}"
        if section.page_start == section.page_end
        else f"{section.page_start}-{section.page_end}"
    )

    frontmatter = {
        "type": "manual_section",
        "vehicle": VEHICLE_LINK,
        "title": f"{target.chapter_title_ru} — {section.title}",
        "title_en": f"{target.chapter_title_en} — {section.title}",
        "chapter_code": target.chapter_code,
        "chapter": target.chapter_title_ru,
        "section": section.title,
        "section_index": _section_index(section, total_in_chapter),
        "volume": target.volume,
        "source_pdf": target.file_name,
        "page_range": page_range,
        "page_count": section.page_end - section.page_start + 1,
        "topics": _guess_topics(target.chapter_code, section.title),
        "aliases": _aliases(target, section),
        "related_parts": [],
        "related_issues": [],
        "last_verified": date.today().isoformat(),
        "tags": _tags(target.chapter_code),
    }

    yaml_block = yaml.safe_dump(
        frontmatter,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=120,
    ).strip()

    body = section.body_md.strip() or "_(пустая секция — текст не извлечён)_"

    md = (
        f"---\n{yaml_block}\n---\n\n"
        f"# {target.chapter_title_ru} — {section.title}\n\n"
        f"> **Глава:** `{target.chapter_code}` {target.chapter_title_en}  \n"
        f"> **Источник:** `{target.file_name}` (стр. {page_range})  \n"
        f"> **Авто:** {VEHICLE_LINK}\n\n"
        f"---\n\n"
        f"{body}\n"
    )
    return fname, md


def _make_filename(target: PdfTarget, section: Section) -> str:
    code = target.chapter_code or "00"
    title_slug = slugify(section.title)[:60] or "section"
    return f"{code}__{title_slug}.md"


_TOPIC_BY_CHAPTER: dict[str, list[str]] = {
    "11A": ["engine"], "11B": ["engine", "overhaul"],
    "11C": ["engine"], "11D": ["engine", "overhaul"],
    "12":  ["engine", "lubrication"],
    "13A": ["fuel_injection"], "13B": ["fuel_injection"],
    "13C": ["fuel"],
    "14":  ["cooling"],
    "15":  ["intake", "exhaust"],
    "16":  ["engine", "electrical"],
    "17":  ["emissions"],
    "21A": ["clutch"], "21B": ["clutch", "overhaul"],
    "22A": ["transmission", "manual"], "22B": ["transmission", "manual", "overhaul"],
    "23A": ["transmission", "automatic"], "23B": ["transmission", "automatic", "overhaul"],
    "26":  ["axle", "front"],
    "27":  ["axle", "rear"],
    "31":  ["wheels", "tyres"],
    "32":  ["mounts"],
    "33A": ["suspension", "front"],
    "34":  ["suspension", "rear"],
    "35A": ["brakes"], "35B": ["brakes", "abs"],
    "36":  ["brakes", "parking"],
    "37A": ["steering"],
    "42":  ["body"],
    "51":  ["exterior"],
    "52A": ["interior"], "52B": ["srs", "safety"],
    "54":  ["electrical", "chassis"],
    "55":  ["hvac"],
    "70":  ["reference"],
    "80A": ["wiring"], "80B": ["wiring"], "90": ["wiring"],
}


def _guess_topics(chapter_code: str, section_title: str) -> list[str]:
    base = list(_TOPIC_BY_CHAPTER.get(chapter_code, []))
    t = section_title.lower()
    extras = []
    if "specification" in t: extras.append("specs")
    if "troubleshoot" in t: extras.append("diagnostics")
    if "removal" in t or "installation" in t: extras.append("rnr")
    if "inspection" in t: extras.append("inspection")
    if "service" in t: extras.append("service")
    if "torque" in t: extras.append("torque")
    if "special tool" in t: extras.append("tools")
    seen = set()
    return [x for x in base + extras if not (x in seen or seen.add(x))]


def _aliases(target: PdfTarget, section: Section) -> list[str]:
    aliases = {
        f"{target.chapter_code} {section.title}",
        f"{target.chapter_code}-{slugify(section.title)}",
        f"{target.chapter_title_en} {section.title}",
    }
    return sorted(a for a in aliases if a.strip())


def _tags(chapter_code: str) -> list[str]:
    base = ["manual"]
    base.extend(_TOPIC_BY_CHAPTER.get(chapter_code, []))
    return base


def _section_index(section: Section, total: int) -> str:
    return f"page-{section.page_start}"
