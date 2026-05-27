"""CMDB OS Compliance Checker.

Checks all HOST and VM CIs in CMDB against the corporate OS regulation
(approved 2026-05-13). HOST os_name takes priority over VM when shorthost
matches both types.

Usage:
    python cmdb_os_compliance.py --url https://cmdb.example.com \
        --user alice --password secret

Env vars (fallback): CMDB_URL, CMDB_USER, CMDB_PASSWORD
"""

import argparse
import csv
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import date
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
    username: str
    password: str
    page_size: int = 500
    output_path: Path = field(default_factory=lambda: Path(f"os_compliance_report_{date.today():%Y%m%d}.csv"))
    verify_ssl: bool = False
    timeout: int = 30


def load_config(argv: list[str] | None = None) -> Config:
    import os

    parser = argparse.ArgumentParser(description="CMDB OS Compliance Checker")
    parser.add_argument("--url", default=os.environ.get("CMDB_URL"), help="CMDB base URL")
    parser.add_argument("--user", default=os.environ.get("CMDB_USER"), help="CMDB username")
    parser.add_argument("--password", default=os.environ.get("CMDB_PASSWORD"), help="CMDB password")
    parser.add_argument("--page-size", type=int, default=500)
    parser.add_argument("--output", type=Path, default=None)

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    missing = [name for name, val in [("--url/CMDB_URL", args.url), ("--user/CMDB_USER", args.user), ("--password/CMDB_PASSWORD", args.password)] if not val]
    if missing:
        parser.error(f"Required but not provided: {', '.join(missing)}")

    output = args.output or Path(f"os_compliance_report_{date.today():%Y%m%d}.csv")
    return Config(
        cmdb_url=args.url.rstrip("/"),
        username=args.user,
        password=args.password,
        page_size=args.page_size,
        output_path=output,
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

# Windows build ordering: parse "NNHx" → (NN, x) where x: 1=H1, 2=H2
_WIN11_BUILD_RE = re.compile(r"\b(\d{2})h([12])\b", re.IGNORECASE)


def _parse_win11_build(text: str) -> tuple[int, int] | None:
    m = _WIN11_BUILD_RE.search(text)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def _build_ge(actual: tuple[int, int], minimum: tuple[int, int]) -> bool:
    return actual >= minimum


_WIN_SERVER_YEAR_RE = re.compile(r"\b(2008|2012|2016|2019|2022|2025)(?:\s*r2)?\b", re.IGNORECASE)
_UBUNTU_VER_RE      = re.compile(r"ubuntu\s+(\d+)\.(\d+)", re.IGNORECASE)
_DEBIAN_VER_RE      = re.compile(r"debian[^\d]*(\d+)")
_ALMA_VER_RE        = re.compile(r"alma\w*\s*(?:linux\s*)?(\d+)", re.IGNORECASE)
_RHEL_VER_RE        = re.compile(r"(?:rhel|red\s*hat[^0-9]*)\s*(\d+)", re.IGNORECASE)


def _normalize(os_name: str) -> tuple[str, str]:
    """Normalize os_name and split on first '|' → (head, tail)."""
    s = os_name.lower().strip()
    s = s.replace("майкрософт", "microsoft")
    s = re.sub(r"\s+", " ", s)
    if "|" in s:
        head, _, tail = s.partition("|")
    else:
        head, tail = s, ""
    return head.strip(), tail.strip()


def _classify_windows_client(head: str, tail: str) -> ClassificationResult:
    # Detect Windows version number
    if re.search(r"\bwindows\s*10\b", head):
        return ClassificationResult(Status.NON_COMPLIANT, "NON_COMPLIANT: Windows 10 not allowed", "windows_client")
    if re.search(r"\bwindows\s*(?:8|8\.1|7|xp|vista)\b", head):
        ver_m = re.search(r"\bwindows\s*(8\.1|8|7|xp|vista)\b", head)
        ver = ver_m.group(1) if ver_m else "legacy"
        return ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: Windows {ver} not allowed", "windows_client")
    if re.search(r"\bwindows\s*11\b", head):
        build = _parse_win11_build(tail) or _parse_win11_build(head)
        if build and _build_ge(build, (23, 2)):
            return ClassificationResult(Status.OK, f"OK: Windows 11 {build[0]}H{build[1]}", "windows_client", f"{build[0]}H{build[1]}")
        elif build:
            return ClassificationResult(Status.WARNING, f"WARNING: Windows 11 {build[0]}H{build[1]} — must be 23H2+", "windows_client", f"{build[0]}H{build[1]}")
        else:
            return ClassificationResult(Status.WARNING, "WARNING: Windows 11 build unknown — must be 23H2+", "windows_client")
    # Generic 'windows' with no version
    return ClassificationResult(Status.NON_COMPLIANT, "NON_COMPLIANT: Windows version not recognized", "windows_client")


def _classify_windows_server(head: str, tail: str) -> ClassificationResult:
    m = _WIN_SERVER_YEAR_RE.search(head)
    if not m:
        return ClassificationResult(Status.NON_COMPLIANT, "NON_COMPLIANT: Windows Server version not recognized", "windows_server")
    year = int(m.group(1))
    if year >= 2022:
        return ClassificationResult(Status.OK, f"OK: Windows Server {year}", "windows_server", str(year))
    if year == 2019:
        return ClassificationResult(Status.WARNING, "WARNING: Windows Server 2019 — conditional (legacy/migration only)", "windows_server", "2019")
    return ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: Windows Server {year} not allowed (minimum 2022)", "windows_server", str(year))


def _classify_ubuntu(head: str, tail: str) -> ClassificationResult:
    m = _UBUNTU_VER_RE.search(head) or _UBUNTU_VER_RE.search(tail)
    if not m:
        return ClassificationResult(Status.NON_COMPLIANT, "NON_COMPLIANT: Ubuntu version not parseable", "linux")
    major, minor = int(m.group(1)), int(m.group(2))
    is_lts = (major % 2 == 0) and (minor == 4)
    if not is_lts:
        return ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: Ubuntu {major}.{minor:02d} is non-LTS (forbidden)", "linux", f"{major}.{minor:02d}")
    if major >= 22:
        return ClassificationResult(Status.OK, f"OK: Ubuntu {major}.{minor:02d} LTS", "linux", f"{major}.{minor:02d}")
    return ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: Ubuntu {major}.{minor:02d} LTS — below 22.04 minimum", "linux", f"{major}.{minor:02d}")


def _classify_linux(head: str, tail: str) -> ClassificationResult:
    if re.search(r"\bubuntu\b", head):
        return _classify_ubuntu(head, tail)

    m = _DEBIAN_VER_RE.search(head)
    if m:
        v = int(m.group(1))
        if v >= 12:
            return ClassificationResult(Status.OK, f"OK: Debian {v}", "linux", str(v))
        return ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: Debian {v} — minimum Debian 12", "linux", str(v))

    m = _ALMA_VER_RE.search(head)
    if m:
        v = int(m.group(1))
        if v >= 9:
            return ClassificationResult(Status.OK, f"OK: AlmaLinux {v}", "linux", str(v))
        return ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: AlmaLinux {v} — minimum 9", "linux", str(v))

    m = _RHEL_VER_RE.search(head)
    if m:
        v = int(m.group(1))
        if v >= 9:
            return ClassificationResult(Status.OK, f"OK: RHEL {v}", "linux", str(v))
        return ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: RHEL {v} — minimum 9", "linux", str(v))

    if re.search(r"\bcentos\b", head):
        return ClassificationResult(Status.NON_COMPLIANT, "NON_COMPLIANT: CentOS not in allowed list", "linux")

    return ClassificationResult(Status.NON_COMPLIANT, "NON_COMPLIANT: Linux distribution not in allowed list", "linux")


def classify_os(os_name: str | None) -> ClassificationResult:
    """Classify an os_name string against the corporate OS regulation."""
    if not os_name:
        return ClassificationResult(Status.UNKNOWN, "UNKNOWN: os_name missing", "unknown")

    head, tail = _normalize(os_name)

    if re.search(r"\bwindows server\b", head):
        return _classify_windows_server(head, tail)
    if re.search(r"\bwindows\b", head):
        return _classify_windows_client(head, tail)
    if re.search(r"\b(?:ubuntu|debian|almalinux|alma linux|red hat|rhel|centos)\b", head):
        return _classify_linux(head, tail)

    return ClassificationResult(Status.NON_COMPLIANT, f"NON_COMPLIANT: unrecognized OS", "unknown")


# ============================================================
# CItem Parsers
# ============================================================

def extract_attrs(ci: dict) -> dict[str, str]:
    """Flatten ci['attrs'] into {type.name.lower(): bvalue}, skip empty values."""
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
    attrs = extract_attrs(ci)
    val = attrs.get("shorthost", "").strip().lower()
    return val or None


def os_name_of(ci: dict) -> str | None:
    attrs = extract_attrs(ci)
    return attrs.get("os_name") or None


# ============================================================
# Host Inventory
# ============================================================

@dataclass
class HostRecord:
    shorthost: str
    os_name: str | None
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
    """Build {shorthost: HostRecord} with HOST priority on os_name."""
    inv: dict[str, HostRecord] = {}

    skip_host = 0
    for ci in host_cis:
        sh = shorthost_of(ci)
        if not sh:
            skip_host += 1
            continue
        osn = os_name_of(ci)
        if sh in inv:
            log.warning("Duplicate HOST shorthost %r — keeping first os_name", sh)
            inv[sh].sources.add("HOST")
            if inv[sh].os_name is None and osn:
                inv[sh].os_name = osn
        else:
            inv[sh] = HostRecord(shorthost=sh, os_name=osn, sources={"HOST"})

    if skip_host:
        log.debug("Skipped %d HOST CIs without shorthost", skip_host)

    skip_vm = 0
    for ci in vm_cis:
        sh = shorthost_of(ci)
        if not sh:
            skip_vm += 1
            continue
        osn = os_name_of(ci)
        if sh in inv:
            inv[sh].sources.add("VM")
            # HOST os_name wins — do NOT overwrite
        else:
            inv[sh] = HostRecord(shorthost=sh, os_name=osn, sources={"VM"})

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
    COL = [40, 55, 10, 14]
    header = ["shorthost", "os_name", "ke_type", "status"]
    sep = "-" * (sum(COL) + len(COL) * 3 + 1)
    print(sep)
    print("  ".join(h.ljust(w) for h, w in zip(header, COL)))
    print(sep)
    for r in rows:
        cells = [r.shorthost[:COL[0]], r.os_name[:COL[1]], r.ke_type[:COL[2]], r.status]
        print("  ".join(str(c).ljust(w) for c, w in zip(cells, COL)))
    print(sep)
    print(f"\nTotal: {summary['total']}  OK: {summary['OK']}  "
          f"WARNING: {summary['WARNING']}  NON_COMPLIANT: {summary['NON_COMPLIANT']}  "
          f"UNKNOWN: {summary['UNKNOWN']}")


def write_csv(rows: list[ReportRow], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["shorthost", "os_name", "ke_type", "status", "reason"])
        for r in rows:
            writer.writerow([r.shorthost, r.os_name, r.ke_type, r.status, r.reason])


# ============================================================
# CMDB Client
# ============================================================

class CmdbClient:
    def __init__(self, config: Config) -> None:
        self._cfg = config
        self._session = requests.Session()
        self._session.verify = config.verify_ssl
        self._base = config.cmdb_url + "/api/v1"

    def login(self) -> None:
        resp = self._session.post(
            f"{self._base}/auth/login",
            data={"username": self._cfg.username, "password": self._cfg.password},
            timeout=self._cfg.timeout,
        )
        if resp.status_code != 200:
            raise CmdbAuthError(f"Login failed: HTTP {resp.status_code}")
        if "cmdb::access_token" not in self._session.cookies and "access_token" not in resp.text:
            # Some versions set cookies differently — check both
            if not any("token" in k.lower() for k in self._session.cookies):
                raise CmdbAuthError("Login succeeded HTTP-wise but no auth cookie received")
        log.info("Authenticated to CMDB as %s", self._cfg.username)

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
            raise CmdbError(f"CI type {name!r} not found in CMDB")
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
                log.info("CI type %s: %d total items, %d pages", ci_type_uuid, body.get("total_items", "?"), total_pages)
            for ci in body.get("page_data", []):
                yield ci
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
        client.login()
        host_uuid = client.get_ci_type_uuid("HOST")
        vm_uuid   = client.get_ci_type_uuid("VM")
        inventory = build_inventory(client.iter_cis(host_uuid), client.iter_cis(vm_uuid))
        rows = build_report(inventory)
        summary = summarize(rows)
        print_console_table(rows, summary)
        write_csv(rows, config.output_path)
        log.info("Report written: %s (%d rows)", config.output_path, len(rows))
    except CmdbAuthError as e:
        log.error("Authentication error: %s", e)
        return 2
    except CmdbError as e:
        log.error("CMDB error: %s", e)
        return 3
    except Exception as e:
        log.exception("Unexpected error: %s", e)
        return 3

    return 1 if summary.get("NON_COMPLIANT", 0) > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
