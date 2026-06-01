"""CMDB OS Compliance Checker.

Checks all HOST and VM CIs in CMDB against the corporate OS regulation
(approved 2026-05-13). HOST os_name/owner takes priority over VM when
shorthost matches both types.

Usage:
    python cmdb_os_compliance.py --url https://cmdb.example.com --token <api_token>

Env vars (fallback): CMDB_URL, CMDB_TOKEN
Output: console table + CSV + HTML report
"""

import argparse
import csv
import html as html_lib
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Iterable, Iterator

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

log = logging.getLogger(__name__)


# ============================================================
# Exceptions
# ============================================================

class CmdbError(Exception):
    pass


class CmdbAuthError(CmdbError):
    pass


class CmdbHTTPError(CmdbError):
    def __init__(self, status: int, body: str) -> None:
        self.status = status
        self.body = body
        super().__init__(f"HTTP {status}: {body[:200]}")


# ============================================================
# Configuration
# ============================================================

@dataclass(frozen=True)
class Config:
    cmdb_url: str
    token: str
    page_size: int = 500
    output_path: Path = field(default_factory=lambda: Path(f"os_compliance_report_{date.today():%Y%m%d}.csv"))
    html_path: Path = field(default_factory=lambda: Path(f"os_compliance_report_{date.today():%Y%m%d}.html"))
    verify_ssl: bool = False
    timeout: int = 30


def load_config(argv: list[str] | None = None) -> Config:
    import os

    parser = argparse.ArgumentParser(description="CMDB OS Compliance Checker")
    parser.add_argument("--url", default=os.environ.get("CMDB_URL"), help="CMDB base URL")
    parser.add_argument("--token", default=os.environ.get("CMDB_TOKEN"), help="CMDB API token")
    parser.add_argument("--page-size", type=int, default=500)
    parser.add_argument("--output", type=Path, default=None, help="CSV output path")
    parser.add_argument("--html", type=Path, default=None, help="HTML output path")

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    missing = [name for name, val in [("--url/CMDB_URL", args.url), ("--token/CMDB_TOKEN", args.token)] if not val]
    if missing:
        parser.error(f"Required but not provided: {', '.join(missing)}")

    today = date.today().strftime("%Y%m%d")
    output = args.output or Path(f"os_compliance_report_{today}.csv")
    html_out = args.html or Path(f"os_compliance_report_{today}.html")
    return Config(
        cmdb_url=args.url.rstrip("/"),
        token=args.token,
        page_size=args.page_size,
        output_path=output,
        html_path=html_out,
    )


# ============================================================
# OS Classification
# ============================================================

class Status(str, Enum):
    OK            = "OK"
    WARNING       = "WARNING"
    NON_COMPLIANT = "NON_COMPLIANT"
    UNKNOWN       = "UNKNOWN"


@dataclass(frozen=True)
class ClassificationResult:
    status: Status
    reason: str
    family: str
    parsed_version: str | None = None


_STATUS_PRIORITY = {Status.NON_COMPLIANT: 0, Status.WARNING: 1, Status.UNKNOWN: 2, Status.OK: 3}

_WIN11_BUILD_RE     = re.compile(r"\b(\d{2})h([12])\b", re.IGNORECASE)
_WIN_SERVER_YEAR_RE = re.compile(r"\b(2008|2012|2016|2019|2022|2025)(?:\s*r2)?\b", re.IGNORECASE)
_UBUNTU_VER_RE      = re.compile(r"ubuntu\s+(\d+)\.(\d+)", re.IGNORECASE)
_DEBIAN_VER_RE      = re.compile(r"debian[^\d]*(\d+)")
_ALMA_VER_RE        = re.compile(r"alma\w*\s*(?:linux\s*)?(\d+)", re.IGNORECASE)
_RHEL_VER_RE        = re.compile(r"(?:rhel|red\s*hat[^0-9]*)\s*(\d+)", re.IGNORECASE)
_BRANCH_NUM_RE = re.compile(r'(?i)^[a-z]+-?(\d+)')


def branch_number_from_host(shorthost: str) -> str | None:
    """Extract numeric branch code from shorthost, stripping leading zeros.

    Examples: 'vl1212-kassa' -> '1212', 'irk020-srv' -> '20'.
    Returns None if no leading-letters+digits pattern found.
    """
    m = _BRANCH_NUM_RE.match(shorthost)
    if not m:
        return None
    return str(int(m.group(1)))


def _parse_win11_build(text: str) -> tuple[int, int] | None:
    m = _WIN11_BUILD_RE.search(text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def _build_ge(actual: tuple[int, int], minimum: tuple[int, int]) -> bool:
    return actual >= minimum


def _normalize(os_name: str) -> tuple[str, str]:
    s = os_name.lower().strip()
    s = s.replace("майкрософт", "microsoft")
    s = re.sub(r"\s+", " ", s)
    head, _, tail = s.partition("|")
    return head.strip(), tail.strip()


def _classify_windows_client(head: str, tail: str) -> ClassificationResult:
    if re.search(r"\bwindows\s*10\b", head):
        return ClassificationResult(Status.NON_COMPLIANT, "NON_COMPLIANT: Windows 10 не разрешён", "windows_client")
    m = re.search(r"\bwindows\s*(8\.1|8|7|xp|vista)\b", head)
    if m:
        return ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: Windows {m.group(1)} не разрешён", "windows_client")
    if re.search(r"\bwindows\s*11\b", head):
        build = _parse_win11_build(tail) or _parse_win11_build(head)
        if build and _build_ge(build, (23, 2)):
            return ClassificationResult(Status.OK, f"OK: Windows 11 {build[0]}H{build[1]}", "windows_client", f"{build[0]}H{build[1]}")
        if build:
            return ClassificationResult(Status.WARNING, f"WARNING: Windows 11 {build[0]}H{build[1]} — требуется 23H2+", "windows_client", f"{build[0]}H{build[1]}")
        return ClassificationResult(Status.WARNING, "WARNING: Windows 11 — версия сборки не определена (требуется 23H2+)", "windows_client")
    return ClassificationResult(Status.NON_COMPLIANT, "NON_COMPLIANT: Версия Windows не определена", "windows_client")


def _classify_windows_server(head: str, tail: str) -> ClassificationResult:
    m = _WIN_SERVER_YEAR_RE.search(head)
    if not m:
        return ClassificationResult(Status.NON_COMPLIANT, "NON_COMPLIANT: Версия Windows Server не определена", "windows_server")
    year = int(m.group(1))
    if year >= 2022:
        return ClassificationResult(Status.OK, f"OK: Windows Server {year}", "windows_server", str(year))
    if year == 2019:
        return ClassificationResult(Status.WARNING, "WARNING: Windows Server 2019 — допустим временно (только legacy/миграция)", "windows_server", "2019")
    return ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: Windows Server {year} — минимум 2022", "windows_server", str(year))


def _classify_ubuntu(head: str, tail: str) -> ClassificationResult:
    m = _UBUNTU_VER_RE.search(head) or _UBUNTU_VER_RE.search(tail)
    if not m:
        return ClassificationResult(Status.NON_COMPLIANT, "NON_COMPLIANT: Версия Ubuntu не определена", "linux")
    major, minor = int(m.group(1)), int(m.group(2))
    is_lts = (major % 2 == 0) and (minor == 4)
    if not is_lts:
        return ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: Ubuntu {major}.{minor:02d} — non-LTS запрещена", "linux", f"{major}.{minor:02d}")
    if major >= 22:
        return ClassificationResult(Status.OK, f"OK: Ubuntu {major}.{minor:02d} LTS", "linux", f"{major}.{minor:02d}")
    return ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: Ubuntu {major}.{minor:02d} LTS — ниже минимума 22.04", "linux", f"{major}.{minor:02d}")


def _classify_linux(head: str, tail: str) -> ClassificationResult:
    if re.search(r"\bubuntu\b", head):
        return _classify_ubuntu(head, tail)
    m = _DEBIAN_VER_RE.search(head)
    if m:
        v = int(m.group(1))
        return (ClassificationResult(Status.OK, f"OK: Debian {v}", "linux", str(v)) if v >= 12
                else ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: Debian {v} — минимум Debian 12", "linux", str(v)))
    m = _ALMA_VER_RE.search(head)
    if m:
        v = int(m.group(1))
        return (ClassificationResult(Status.OK, f"OK: AlmaLinux {v}", "linux", str(v)) if v >= 9
                else ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: AlmaLinux {v} — минимум 9", "linux", str(v)))
    m = _RHEL_VER_RE.search(head)
    if m:
        v = int(m.group(1))
        return (ClassificationResult(Status.OK, f"OK: RHEL {v}", "linux", str(v)) if v >= 9
                else ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: RHEL {v} — минимум 9", "linux", str(v)))
    if re.search(r"\bcentos\b", head):
        return ClassificationResult(Status.NON_COMPLIANT, "NON_COMPLIANT: CentOS не входит в список допустимых ОС", "linux")
    return ClassificationResult(Status.NON_COMPLIANT, "NON_COMPLIANT: Дистрибутив Linux не входит в список допустимых", "linux")


def classify_os(os_name: str | None) -> ClassificationResult:
    if not os_name:
        return ClassificationResult(Status.UNKNOWN, "UNKNOWN: os_name отсутствует в CMDB", "unknown")
    head, tail = _normalize(os_name)
    if re.search(r"\bwindows server\b", head):
        return _classify_windows_server(head, tail)
    if re.search(r"\bwindows\b", head):
        return _classify_windows_client(head, tail)
    if re.search(r"\b(?:ubuntu|debian|almalinux|alma linux|red hat|rhel|centos)\b", head):
        return _classify_linux(head, tail)
    return ClassificationResult(Status.NON_COMPLIANT, "NON_COMPLIANT: ОС не распознана", "unknown")


# ============================================================
# CItem Parsers
# ============================================================

def extract_attrs(ci: dict) -> dict[str, str]:
    attrs = ci.get("attrs") or []
    result: dict[str, str] = {}
    for attr in attrs:
        bvalue = attr.get("bvalue") or ""
        if not bvalue:
            continue
        type_info = attr.get("type") or {}
        name = type_info.get("name", "")
        if not name:
            continue
        key = name.lower()
        if key not in result:
            result[key] = bvalue
        else:
            log.debug("Duplicate attr %r in CI %s — keeping first", key, ci.get("uuid"))
    return result


def shorthost_of(ci: dict) -> str | None:
    val = extract_attrs(ci).get("shorthost", "").strip().lower()
    return val or None


def os_name_of(ci: dict) -> str | None:
    return extract_attrs(ci).get("os_name") or None


def owner_of(ci: dict) -> str | None:
    """Return owner display string: 'owner / owner_person' or just one of them."""
    attrs = extract_attrs(ci)
    owner = attrs.get("owner", "").strip()
    person = (attrs.get("owner_person") or attrs.get("admin_person") or "").strip()
    if owner and person:
        return f"{owner} / {person}"
    return owner or person or None


# ============================================================
# Host Inventory
# ============================================================

@dataclass
class HostRecord:
    shorthost: str
    os_name: str | None
    owner: str | None
    sources: set[str]

    @property
    def ke_type(self) -> str:
        if self.sources == {"HOST"}:
            return "HOST"
        if self.sources == {"VM"}:
            return "VM"
        return "HOST+VM"


def build_inventory(
    host_cis: Iterable[dict],
    vm_cis: Iterable[dict],
) -> dict[str, HostRecord]:
    """Build {shorthost: HostRecord}. HOST os_name and owner take priority over VM."""
    inv: dict[str, HostRecord] = {}

    skip_host = 0
    for ci in host_cis:
        sh = shorthost_of(ci)
        if not sh:
            skip_host += 1
            continue
        osn = os_name_of(ci)
        own = owner_of(ci)
        if sh in inv:
            log.warning("Duplicate HOST shorthost %r — keeping first values", sh)
            inv[sh].sources.add("HOST")
            if inv[sh].os_name is None and osn:
                inv[sh].os_name = osn
            if inv[sh].owner is None and own:
                inv[sh].owner = own
        else:
            inv[sh] = HostRecord(shorthost=sh, os_name=osn, owner=own, sources={"HOST"})

    if skip_host:
        log.debug("Skipped %d HOST CIs without shorthost", skip_host)

    skip_vm = 0
    for ci in vm_cis:
        sh = shorthost_of(ci)
        if not sh:
            skip_vm += 1
            continue
        osn = os_name_of(ci)
        own = owner_of(ci)
        if sh in inv:
            inv[sh].sources.add("VM")
            # HOST values win — do NOT overwrite
        else:
            inv[sh] = HostRecord(shorthost=sh, os_name=osn, owner=own, sources={"VM"})

    if skip_vm:
        log.debug("Skipped %d VM CIs without shorthost", skip_vm)

    return inv


# ============================================================
# Reporting
# ============================================================

@dataclass
class ReportRow:
    shorthost: str
    os_name: str
    owner: str
    ke_type: str
    status: Status
    reason: str


def build_report(inventory: dict[str, HostRecord]) -> list[ReportRow]:
    rows: list[ReportRow] = []
    for rec in inventory.values():
        result = classify_os(rec.os_name)
        rows.append(ReportRow(
            shorthost=rec.shorthost,
            os_name=rec.os_name or "",
            owner=rec.owner or "",
            ke_type=rec.ke_type,
            status=result.status,
            reason=result.reason,
        ))
    rows.sort(key=lambda r: (_STATUS_PRIORITY[r.status], r.shorthost))
    return rows


def summarize(rows: list[ReportRow]) -> dict[str, int]:
    counts: dict[str, int] = {"total": len(rows), "OK": 0, "WARNING": 0, "NON_COMPLIANT": 0, "UNKNOWN": 0}
    for r in rows:
        counts[r.status] = counts.get(r.status, 0) + 1
    return counts


def print_console_table(rows: list[ReportRow], summary: dict[str, int]) -> None:
    COL = [35, 50, 30, 10, 14]
    header = ["shorthost", "os_name", "owner", "ke_type", "status"]
    sep = "-" * (sum(COL) + len(COL) * 2 + 1)
    print(sep)
    print("  ".join(h.ljust(w) for h, w in zip(header, COL)))
    print(sep)
    for r in rows:
        cells = [r.shorthost[:COL[0]], r.os_name[:COL[1]], r.owner[:COL[2]], r.ke_type[:COL[3]], r.status]
        print("  ".join(str(c).ljust(w) for c, w in zip(cells, COL)))
    print(sep)
    print(f"\nИтого: {summary['total']}  |  OK: {summary['OK']}  "
          f"WARNING: {summary['WARNING']}  NON_COMPLIANT: {summary['NON_COMPLIANT']}  "
          f"UNKNOWN: {summary['UNKNOWN']}")


def write_csv(rows: list[ReportRow], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["shorthost", "os_name", "owner", "ke_type", "status", "reason"])
        for r in rows:
            writer.writerow([r.shorthost, r.os_name, r.owner, r.ke_type, r.status, r.reason])


# ============================================================
# HTML Report
# ============================================================

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Отчёт соответствия ОС регламенту — {report_date}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; color: #1a1a2e; }}
  .page {{ max-width: 1400px; margin: 0 auto; padding: 24px 20px; }}

  .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
             color: #fff; border-radius: 12px; padding: 28px 32px; margin-bottom: 24px; }}
  .header h1 {{ font-size: 22px; font-weight: 700; letter-spacing: .5px; }}
  .header .meta {{ margin-top: 6px; font-size: 13px; opacity: .7; }}

  .cards {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }}
  .card {{ flex: 1; min-width: 140px; background: #fff; border-radius: 10px;
           padding: 18px 20px; box-shadow: 0 1px 4px rgba(0,0,0,.08); cursor: pointer;
           transition: box-shadow .15s; }}
  .card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,.15); }}
  .card .num {{ font-size: 32px; font-weight: 700; line-height: 1; }}
  .card .lbl {{ font-size: 12px; color: #666; margin-top: 4px; text-transform: uppercase; letter-spacing: .6px; }}
  .card.total .num {{ color: #1a1a2e; }}
  .card.ok    .num {{ color: #16a34a; }}
  .card.warn  .num {{ color: #d97706; }}
  .card.fail  .num {{ color: #dc2626; }}
  .card.unk   .num {{ color: #6b7280; }}

  .filterbar {{ background: #fff; border-radius: 10px; padding: 14px 20px;
                margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.08);
                display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }}
  .filterbar input {{ flex: 1; min-width: 200px; padding: 8px 12px; border: 1px solid #d1d5db;
                      border-radius: 6px; font-size: 14px; outline: none; }}
  .filterbar input:focus {{ border-color: #0f3460; box-shadow: 0 0 0 3px rgba(15,52,96,.12); }}
  .filter-btn {{ padding: 8px 16px; border: 1px solid #d1d5db; border-radius: 6px;
                 background: #fff; cursor: pointer; font-size: 13px; font-weight: 500;
                 transition: all .15s; white-space: nowrap; }}
  .filter-btn:hover {{ background: #f3f4f6; }}
  .filter-btn.active {{ background: #0f3460; color: #fff; border-color: #0f3460; }}
  .page-size-sel {{ padding: 7px 10px; border: 1px solid #d1d5db; border-radius: 6px;
                    font-size: 13px; cursor: pointer; background: #fff; }}

  .table-wrap {{ background: #fff; border-radius: 10px; overflow: hidden;
                 box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; }}
  thead th {{ background: #1a1a2e; color: #fff; padding: 12px 14px; text-align: left;
              font-weight: 600; font-size: 12px; letter-spacing: .5px;
              text-transform: uppercase; white-space: nowrap; }}
  tbody tr {{ border-bottom: 1px solid #f0f0f0; transition: background .1s; }}
  tbody tr:last-child {{ border-bottom: none; }}
  td {{ padding: 10px 14px; vertical-align: top; }}
  td.host {{ font-family: 'Consolas', monospace; font-size: 13px; font-weight: 600; color: #0f3460; }}
  td.os   {{ color: #374151; }}
  td.own  {{ color: #4b5563; font-size: 13px; }}
  td.ke   {{ font-size: 12px; color: #6b7280; white-space: nowrap; }}
  td.reason {{ font-size: 12px; color: #6b7280; }}

  .row-fail    {{ background: #fff5f5; }}
  .row-warning {{ background: #fffbeb; }}
  .row-ok      {{ background: #f0fdf4; }}
  .row-unknown {{ background: #f9fafb; }}
  .row-fail:hover    {{ background: #fee2e2; }}
  .row-warning:hover {{ background: #fef3c7; }}
  .row-ok:hover      {{ background: #dcfce7; }}
  .row-unknown:hover {{ background: #f3f4f6; }}

  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px;
            font-size: 11px; font-weight: 700; letter-spacing: .4px; white-space: nowrap; }}
  .badge.ok      {{ background: #dcfce7; color: #15803d; }}
  .badge.warning {{ background: #fef3c7; color: #b45309; }}
  .badge.fail    {{ background: #fee2e2; color: #b91c1c; }}
  .badge.unknown {{ background: #f3f4f6; color: #6b7280; }}

  /* Pagination */
  .pagination {{ display: flex; align-items: center; justify-content: space-between;
                 padding: 14px 20px; background: #fff; border-top: 1px solid #f0f0f0;
                 flex-wrap: wrap; gap: 10px; }}
  .pag-info {{ font-size: 13px; color: #6b7280; }}
  .pag-controls {{ display: flex; gap: 4px; align-items: center; flex-wrap: wrap; }}
  .pag-btn {{ min-width: 34px; height: 34px; padding: 0 10px; border: 1px solid #d1d5db;
              border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px;
              display: flex; align-items: center; justify-content: center;
              transition: all .15s; white-space: nowrap; }}
  .pag-btn:hover:not(:disabled) {{ background: #f3f4f6; }}
  .pag-btn.active {{ background: #0f3460; color: #fff; border-color: #0f3460; font-weight: 700; }}
  .pag-btn:disabled {{ opacity: .4; cursor: default; }}
  .pag-ellipsis {{ padding: 0 6px; color: #9ca3af; font-size: 14px; }}

  .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #9ca3af; }}
  .empty {{ padding: 40px; text-align: center; color: #9ca3af; font-size: 14px; }}
</style>
</head>
<body>
<div class="page">

  <div class="header">
    <h1>Отчёт соответствия ОС корпоративному регламенту</h1>
    <div class="meta">Сформирован: {generated_at} &nbsp;·&nbsp; Всего КЕ: {total}</div>
  </div>

  <div class="cards">
    <div class="card total" onclick="filterByStatus('ALL')">
      <div class="num">{total}</div><div class="lbl">Всего</div></div>
    <div class="card ok"   onclick="filterByStatus('OK')">
      <div class="num">{ok}</div><div class="lbl">Соответствует</div></div>
    <div class="card warn" onclick="filterByStatus('WARNING')">
      <div class="num">{warning}</div><div class="lbl">Условно допустимо</div></div>
    <div class="card fail" onclick="filterByStatus('NON_COMPLIANT')">
      <div class="num">{fail}</div><div class="lbl">Не соответствует</div></div>
    <div class="card unk"  onclick="filterByStatus('UNKNOWN')">
      <div class="num">{unknown}</div><div class="lbl">Нет данных об ОС</div></div>
  </div>

  <div class="filterbar">
    <input type="text" id="search" placeholder="Поиск по хосту, ОС или владельцу…" oninput="applyFilters()">
    <button class="filter-btn active" data-status="ALL"           onclick="setStatus(this)">Все</button>
    <button class="filter-btn"        data-status="NON_COMPLIANT" onclick="setStatus(this)">Не соответствует</button>
    <button class="filter-btn"        data-status="WARNING"       onclick="setStatus(this)">Условно</button>
    <button class="filter-btn"        data-status="OK"            onclick="setStatus(this)">OK</button>
    <button class="filter-btn"        data-status="UNKNOWN"       onclick="setStatus(this)">Нет данных</button>
    <select class="page-size-sel" onchange="changePageSize(this.value)">
      <option value="50">50 / стр.</option>
      <option value="100" selected>100 / стр.</option>
      <option value="200">200 / стр.</option>
      <option value="500">500 / стр.</option>
    </select>
  </div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Хост</th><th>ОС</th><th>Владелец</th><th>Тип КЕ</th><th>Статус</th><th>Причина</th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
    <div class="pagination">
      <div class="pag-info" id="pag-info"></div>
      <div class="pag-controls" id="pag-controls"></div>
    </div>
  </div>

  <div class="footer">Регламент допустимых ОС от 13.05.2026 &nbsp;·&nbsp; CMDB OS Compliance Checker</div>
</div>

<script>
var DATA = {data_json};

var ROW_CLASS = {{
  'OK': 'row-ok', 'WARNING': 'row-warning',
  'NON_COMPLIANT': 'row-fail', 'UNKNOWN': 'row-unknown'
}};
var BADGE = {{
  'OK':            '<span class="badge ok">OK</span>',
  'WARNING':       '<span class="badge warning">WARNING</span>',
  'NON_COMPLIANT': '<span class="badge fail">NON_COMPLIANT</span>',
  'UNKNOWN':       '<span class="badge unknown">UNKNOWN</span>'
}};

var filtered = DATA.slice();
var currentPage = 1;
var pageSize = 100;
var activeStatus = 'ALL';

function esc(s) {{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function render() {{
  var tbody = document.getElementById('tbody');
  var start = (currentPage - 1) * pageSize;
  var page  = filtered.slice(start, start + pageSize);
  if (filtered.length === 0) {{
    tbody.innerHTML = '<tr><td colspan="6" class="empty">Ничего не найдено</td></tr>';
  }} else {{
    tbody.innerHTML = page.map(function(r) {{
      return '<tr class="' + ROW_CLASS[r.status] + '">' +
        '<td class="host">' + esc(r.shorthost) + '</td>' +
        '<td class="os">'   + esc(r.os_name)   + '</td>' +
        '<td class="own">'  + esc(r.owner)      + '</td>' +
        '<td class="ke">'   + esc(r.ke_type)    + '</td>' +
        '<td>' + BADGE[r.status] + '</td>' +
        '<td class="reason">' + esc(r.reason)   + '</td>' +
        '</tr>';
    }}).join('');
  }}
  renderPagination();
}}

function renderPagination() {{
  var total = filtered.length;
  var totalPages = Math.max(1, Math.ceil(total / pageSize));
  var start = total === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  var end   = Math.min(currentPage * pageSize, total);
  document.getElementById('pag-info').textContent =
    'Показано ' + start + '–' + end + ' из ' + total;

  var html = '';
  html += '<button class="pag-btn" onclick="goTo(1)" ' + (currentPage===1?'disabled':'') + '>&laquo;</button>';
  html += '<button class="pag-btn" onclick="goTo(' + (currentPage-1) + ')" ' + (currentPage===1?'disabled':'') + '>&lsaquo;</button>';

  var pages = pagesToShow(currentPage, totalPages);
  var prev = null;
  pages.forEach(function(p) {{
    if (prev !== null && p - prev > 1) html += '<span class="pag-ellipsis">…</span>';
    html += '<button class="pag-btn' + (p===currentPage?' active':'') + '" onclick="goTo(' + p + ')">' + p + '</button>';
    prev = p;
  }});

  html += '<button class="pag-btn" onclick="goTo(' + (currentPage+1) + ')" ' + (currentPage===totalPages?'disabled':'') + '>&rsaquo;</button>';
  html += '<button class="pag-btn" onclick="goTo(' + totalPages + ')" ' + (currentPage===totalPages?'disabled':'') + '>&raquo;</button>';
  document.getElementById('pag-controls').innerHTML = html;
}}

function pagesToShow(cur, total) {{
  var pages = [];
  var delta = 2;
  for (var p = 1; p <= total; p++) {{
    if (p === 1 || p === total || (p >= cur - delta && p <= cur + delta)) pages.push(p);
  }}
  return pages;
}}

function goTo(p) {{
  var totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  currentPage = Math.max(1, Math.min(p, totalPages));
  render();
  window.scrollTo({{top: 0, behavior: 'smooth'}});
}}

function applyFilters() {{
  var q = document.getElementById('search').value.toLowerCase();
  filtered = DATA.filter(function(r) {{
    var matchS = activeStatus === 'ALL' || r.status === activeStatus;
    var matchQ = !q || (r.shorthost+r.os_name+r.owner+r.reason).toLowerCase().includes(q);
    return matchS && matchQ;
  }});
  currentPage = 1;
  render();
}}

function setStatus(btn) {{
  document.querySelectorAll('.filter-btn').forEach(function(b) {{ b.classList.remove('active'); }});
  btn.classList.add('active');
  activeStatus = btn.dataset.status;
  applyFilters();
}}

function filterByStatus(status) {{
  activeStatus = status;
  document.querySelectorAll('.filter-btn').forEach(function(b) {{
    b.classList.toggle('active', b.dataset.status === status);
  }});
  applyFilters();
}}

function changePageSize(val) {{
  pageSize = parseInt(val);
  currentPage = 1;
  render();
}}

render();
</script>
</body>
</html>
"""


def write_html(rows: list[ReportRow], summary: dict[str, int], path: Path) -> None:
    import json as _json
    data = [
        {"shorthost": r.shorthost, "os_name": r.os_name, "owner": r.owner,
         "ke_type": r.ke_type, "status": r.status, "reason": r.reason}
        for r in rows
    ]
    content = _HTML_TEMPLATE.format(
        report_date=date.today().strftime("%d.%m.%Y"),
        generated_at=datetime.now().strftime("%d.%m.%Y %H:%M"),
        total=summary["total"],
        ok=summary["OK"],
        warning=summary["WARNING"],
        fail=summary["NON_COMPLIANT"],
        unknown=summary["UNKNOWN"],
        data_json=_json.dumps(data, ensure_ascii=False),
    )
    path.write_text(content, encoding="utf-8")


# ============================================================
# CMDB Client
# ============================================================

class CmdbClient:
    def __init__(self, config: Config) -> None:
        self._cfg = config
        self._session = requests.Session()
        self._session.verify = config.verify_ssl
        self._session.headers["Authorization"] = f"Bearer {config.token}"
        self._base = config.cmdb_url + "/api/v1"

    def check_auth(self) -> None:
        resp = self._session.get(f"{self._base}/user/me", timeout=self._cfg.timeout)
        if resp.status_code == 401:
            raise CmdbAuthError("Токен отклонён (401 Unauthorized)")
        if resp.status_code == 403:
            raise CmdbAuthError("Токен действителен, но недостаточно прав (403 Forbidden)")
        if resp.status_code not in (200, 404):
            raise CmdbHTTPError(resp.status_code, resp.text)
        log.info("CMDB token accepted")

    def get_ci_type_uuid(self, name: str) -> str:
        resp = self._session.get(
            f"{self._base}/ci_type/search/",
            params={"name": name},
            timeout=self._cfg.timeout,
        )
        if resp.status_code != 200:
            raise CmdbHTTPError(resp.status_code, resp.text)
        data = resp.json()
        items = data if isinstance(data, list) else data.get("data", [])
        matches = [it for it in items if it.get("name", "").upper() == name.upper()]
        if not matches:
            raise CmdbError(f"CI type {name!r} не найден в CMDB")
        if len(matches) > 1:
            log.warning("Multiple CI types match %r — using first: %s", name, matches[0]["uuid"])
        return matches[0]["uuid"]

    def iter_cis(self, ci_type_uuid: str) -> Iterator[dict]:
        page = 1
        total_pages = None
        while True:
            resp = self._session.get(
                f"{self._base}/ci/full/",
                params={"type": ci_type_uuid, "page": page, "size": self._cfg.page_size},
                timeout=self._cfg.timeout,
            )
            if resp.status_code != 200:
                raise CmdbHTTPError(resp.status_code, resp.text)
            body = resp.json()
            if total_pages is None:
                total_pages = body.get("total_pages", 1)
                log.info("CI type %s: %d items, %d pages", ci_type_uuid, body.get("total_items", "?"), total_pages)
            yield from body.get("page_data", [])
            log.debug("Fetched page %d/%d", page, total_pages)
            if page >= total_pages:
                break
            page += 1


# ============================================================
# Entry Point
# ============================================================

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main(argv: list[str] | None = None) -> int:
    config = load_config(argv)
    setup_logging()
    client = CmdbClient(config)
    try:
        client.check_auth()
        host_uuid = client.get_ci_type_uuid("HOST")
        vm_uuid   = client.get_ci_type_uuid("VM")
        inventory = build_inventory(client.iter_cis(host_uuid), client.iter_cis(vm_uuid))
        rows = build_report(inventory)
        summary = summarize(rows)
        print_console_table(rows, summary)
        write_csv(rows, config.output_path)
        write_html(rows, summary, config.html_path)
        log.info("CSV:  %s", config.output_path)
        log.info("HTML: %s", config.html_path)
    except CmdbAuthError as e:
        log.error("Ошибка аутентификации: %s", e)
        return 2
    except CmdbError as e:
        log.error("Ошибка CMDB: %s", e)
        return 3
    except Exception as e:
        log.exception("Неожиданная ошибка: %s", e)
        return 3

    return 1 if summary.get("NON_COMPLIANT", 0) > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
