"""Render diagram-only PDF pages as PNG and emit a single index Markdown note."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import fitz
import yaml

from .config import PdfTarget, VEHICLE_LINK, slugify

DPI = 150


@dataclass
class PageImage:
    index: int          # 0-based
    path: Path          # absolute path to the saved PNG


def render_pdf_as_images(pdf_path: Path, out_dir: Path, prefix: str = "") -> list[PageImage]:
    """Render every page of *pdf_path* to a PNG in *out_dir*.

    *prefix* is prepended to each filename so files from different chapters
    never clash when Obsidian resolves short wikilinks across the vault.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    images: list[PageImage] = []
    safe_prefix = (prefix.replace(" ", "_") + "_") if prefix else ""
    with fitz.open(pdf_path) as doc:
        mat = fitz.Matrix(DPI / 72, DPI / 72)
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=mat, alpha=False)
            fname = f"{safe_prefix}p{i + 1:03d}.png"
            dest = out_dir / fname
            pix.save(dest)
            images.append(PageImage(index=i, path=dest))
    return images


def render_image_note(target: PdfTarget, images: list[PageImage], out_dir: Path) -> tuple[str, str]:
    """Return (filename, markdown) for the index note of a diagram chapter."""
    frontmatter = {
        "type": "manual_section",
        "vehicle": VEHICLE_LINK,
        "title": target.chapter_title_ru,
        "title_en": target.chapter_title_en,
        "chapter_code": target.chapter_code,
        "chapter": target.chapter_title_ru,
        "section": "Диаграммы",
        "volume": target.volume,
        "source_pdf": target.file_name,
        "page_count": len(images),
        "topics": ["diagram", "reference"],
        "aliases": [
            f"{target.chapter_code} diagrams",
            f"{target.chapter_title_en}",
        ],
        "related_parts": [],
        "related_issues": [],
        "last_verified": date.today().isoformat(),
        "tags": ["manual", "diagram"],
    }

    yaml_block = yaml.safe_dump(
        frontmatter,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=120,
    ).strip()

    # Embed images relative to the out_dir (Obsidian picks up any wikilink in the vault)
    img_lines = "\n\n".join(
        f"## Страница {img.index + 1}\n\n![[{img.path.name}]]"
        for img in images
    )

    md = (
        f"---\n{yaml_block}\n---\n\n"
        f"# {target.chapter_title_ru}\n\n"
        f"> **Глава:** `{target.chapter_code}` {target.chapter_title_en}  \n"
        f"> **Источник:** `{target.file_name}` ({len(images)} страниц)  \n"
        f"> **Авто:** {VEHICLE_LINK}\n\n"
        f"---\n\n"
        f"{img_lines}\n"
    )
    fname = f"{target.chapter_code or slugify(target.chapter_title_en)}__diagrams.md"
    return fname, md
