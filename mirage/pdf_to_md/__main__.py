"""CLI entry point: convert the manual PDF tree into a vault of Markdown notes.

Usage:
    python -m pdf_to_md \
        --src "Mirage_1999_Service_Manual" \
        --out "vault/00_Manual"

    python -m pdf_to_md --src "..." --out "..." --only "35A"
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

from .config import PdfTarget, parse_pdf_filename
from .extract import extract_pages
from .render import render_note
from .sectionize import build_sections


@dataclass
class RunStats:
    pdfs_seen: int = 0
    pdfs_converted: int = 0
    notes_written: int = 0
    skipped: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.skipped is None:
            self.skipped = []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mirage manual PDF → Obsidian Markdown")
    parser.add_argument("--src", required=True, type=Path, help="Root folder with volume subdirs")
    parser.add_argument("--out", required=True, type=Path, help="Vault subfolder for notes")
    parser.add_argument("--only", default=None,
                        help="Substring filter on PDF filename (e.g. '35A', '11A 1.5L')")
    parser.add_argument("--dry-run", action="store_true", help="Plan only, write nothing")
    args = parser.parse_args(argv)

    stats = RunStats()
    targets = list(_iter_pdfs(args.src, args.only))

    if not targets:
        print("[!] No PDFs matched.", file=sys.stderr)
        return 1

    for src_path, target in targets:
        stats.pdfs_seen += 1
        try:
            _convert(src_path, target, args.out, args.dry_run, stats)
            stats.pdfs_converted += 1
        except Exception as exc:  # noqa: BLE001
            stats.skipped.append(f"{target.file_name}: {exc!r}")
            print(f"[skip] {target.file_name}: {exc!r}", file=sys.stderr)

    print()
    print(f"PDFs seen      : {stats.pdfs_seen}")
    print(f"PDFs converted : {stats.pdfs_converted}")
    print(f"Notes written  : {stats.notes_written}")
    if stats.skipped:
        print(f"Skipped        : {len(stats.skipped)}")
        for s in stats.skipped:
            print(f"   - {s}")
    return 0


def _iter_pdfs(root: Path, only: str | None):
    for vol_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for pdf in sorted(p for p in vol_dir.iterdir() if p.suffix.lower() == ".pdf"):
            if only and only.lower() not in pdf.name.lower():
                continue
            target = parse_pdf_filename(vol_dir.name, pdf.name)
            if target is None:
                continue
            yield pdf, target


def _convert(src_pdf: Path, target: PdfTarget, out_root: Path, dry_run: bool, stats: RunStats) -> None:
    pages = extract_pages(src_pdf)
    sections = build_sections(pages)
    if not sections:
        stats.skipped.append(f"{target.file_name}: no sections")
        return

    out_dir = out_root / target.out_subdir
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{target.chapter_code or '??'}] {target.file_name}  ->  {len(sections)} section(s)")

    seen: set[str] = set()
    for sec in sections:
        fname, md = render_note(target, sec, len(sections))
        unique = _ensure_unique(fname, seen)
        seen.add(unique)
        if dry_run:
            print(f"    DRY: {target.out_subdir}/{unique}  ({sec.page_end - sec.page_start + 1}p)")
            continue
        (out_dir / unique).write_text(md, encoding="utf-8")
        stats.notes_written += 1


def _ensure_unique(name: str, seen: set[str]) -> str:
    if name not in seen:
        return name
    stem, suf = name.rsplit(".", 1)
    i = 2
    while f"{stem}__{i}.{suf}" in seen:
        i += 1
    return f"{stem}__{i}.{suf}"


if __name__ == "__main__":
    raise SystemExit(main())
