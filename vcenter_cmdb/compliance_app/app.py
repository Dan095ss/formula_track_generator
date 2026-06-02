"""CMDB OS Compliance — Flask web app.

Usage:
    cd compliance_app
    python app.py
"""
import csv
import io
import json
import logging
import re
import socket
import subprocess
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, request

from cmdb_os_compliance import (
    CmdbClient,
    ReportRow,
    Status,
    build_account_division_map,
    build_branch_maps,
    build_inventory,
    build_ip_map,
    build_report,
    load_config,
    summarize,
)

log = logging.getLogger(__name__)

app = Flask(__name__)

# ── In-memory data store ─────────────────────────────────────
_rows: list[ReportRow] = []
_summary: dict[str, int] = {"total": 0, "OK": 0, "WARNING": 0, "NON_COMPLIANT": 0, "UNKNOWN": 0}
_divisions: list[str] = []


# ── Scan state (global, multi-client) ────────────────────────
_scan_lock = threading.Lock()
_scan_state: dict = {
    "running":      False,
    "phase":        "",
    "phase_index":  0,
    "phase_total":  7,
    "percent":      0,
    "detail":       "",
    "started_at":   None,
    "finished_at":  None,
    "error":        None,
    "data_version": 0,
}

_SCAN_PHASES = [
    ("Авторизация", 2),
    ("Загрузка филиалов", 8),
    ("Карта host→branch (ref-скан)", 35),
    ("Загрузка ACCOUNT", 10),
    ("Загрузка HOST", 15),
    ("Загрузка VM", 15),
    ("Загрузка IP", 10),
    ("Сборка отчёта", 5),
]


class ScanProgress:
    """Writes weighted phase progress into the global _scan_state."""

    def __init__(self, phases=_SCAN_PHASES) -> None:
        self._phases = phases
        self._base = 0
        self._cur_weight = 0

    def phase(self, index: int, label: str | None = None) -> None:
        self._base = sum(w for _, w in self._phases[: index - 1])
        self._cur_weight = self._phases[index - 1][1]
        lbl = label or self._phases[index - 1][0]
        with _scan_lock:
            _scan_state["phase"] = lbl
            _scan_state["phase_index"] = index
            _scan_state["phase_total"] = len(self._phases)
            _scan_state["percent"] = int(self._base)
            _scan_state["detail"] = ""

    def tick(self, current: int, total: int) -> None:
        frac = (current / total) if total else 0
        pct = self._base + self._cur_weight * frac
        with _scan_lock:
            _scan_state["percent"] = int(min(pct, 100))
            _scan_state["detail"] = (
                f"страница {current}/{total}" if total else ""
            )


# ── Snapshot storage ─────────────────────────────────────────
SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"
_STATUS_PRIO  = {"NON_COMPLIANT": 0, "WARNING": 1, "UNKNOWN": 2, "OK": 3}


def save_snapshot(rows: list[ReportRow], source: str = "cmdb") -> str:
    """Serialise rows to JSON and save to SNAPSHOTS_DIR. Returns snapshot id."""
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    now     = datetime.now()
    snap_id = now.strftime("%Y%m%d_%H%M%S_%f")
    payload = {
        "id":        snap_id,
        "timestamp": now.isoformat(timespec="milliseconds"),
        "source":    source,
        "summary":   summarize(rows),
        "hosts": {
            r.shorthost: {
                "status":   r.status.value,
                "os_name":  r.os_name,
                "owner":    r.owner,
                "division": r.division,
                "family":   r.family,
                "reason":   r.reason,
            }
            for r in rows
        },
    }
    (SNAPSHOTS_DIR / f"{snap_id}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log.info("Snapshot saved: %s (%d hosts)", snap_id, len(rows))
    return snap_id


def list_snapshots() -> list[dict]:
    """Return snapshot metadata (no hosts), sorted newest-first."""
    if not SNAPSHOTS_DIR.exists():
        return []
    result = []
    for p in sorted(SNAPSHOTS_DIR.glob("*.json"), reverse=True):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            result.append({k: d[k] for k in ("id", "timestamp", "source", "summary")})
        except Exception:
            pass
    return result


def load_snapshot(snap_id: str) -> dict:
    """Load full snapshot (including hosts) by id."""
    path = SNAPSHOTS_DIR / f"{snap_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def import_csv_snapshot(csv_bytes: bytes, filename: str = "") -> str:
    """Parse a compliance CSV file and save as a snapshot with source='csv'."""
    import re as _re
    text   = csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(text.splitlines())
    hosts  = {}
    for row in reader:
        sh = (row.get("shorthost") or "").strip()
        if not sh:
            continue
        hosts[sh] = {
            "status":   (row.get("status")   or "").strip(),
            "os_name":  (row.get("os_name")  or "").strip(),
            "owner":    (row.get("owner")    or "").strip(),
            "division": (row.get("division") or "").strip(),
            "family":   (row.get("family")   or "").strip(),
            "reason":   (row.get("reason")   or "").strip(),
        }
    # Extract date from filename (pattern YYYYMMDD)
    ts_str = None
    m = _re.search(r"(\d{8})", filename)
    if m:
        try:
            ts_str = datetime.strptime(m.group(1), "%Y%m%d").isoformat(timespec="seconds")
        except ValueError:
            pass
    if ts_str is None:
        ts_str = datetime.now().isoformat(timespec="seconds")

    snap_id = ts_str.replace("-", "").replace("T", "_").replace(":", "")[:15]
    counts: dict[str, int] = {"total": len(hosts), "OK": 0, "WARNING": 0, "NON_COMPLIANT": 0, "UNKNOWN": 0}
    for h in hosts.values():
        s = h["status"]
        counts[s] = counts.get(s, 0) + 1

    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    payload = {"id": snap_id, "timestamp": ts_str, "source": "csv",
               "summary": counts, "hosts": hosts}
    (SNAPSHOTS_DIR / f"{snap_id}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return snap_id


def compare_snapshots(snap_a: dict, snap_b: dict) -> dict:
    """Diff snap_b vs snap_a. snap_b assumed newer. Returns {new, removed, changed}."""
    hosts_a: dict = snap_a.get("hosts", {})
    hosts_b: dict = snap_b.get("hosts", {})
    keys_a, keys_b = set(hosts_a), set(hosts_b)

    new_hosts = [{"shorthost": h, **hosts_b[h]} for h in sorted(keys_b - keys_a)]
    removed   = [{"shorthost": h, "status_from": hosts_a[h]["status"], **hosts_a[h]}
                 for h in sorted(keys_a - keys_b)]
    changed   = []
    for h in sorted(keys_a & keys_b):
        sa, sb = hosts_a[h]["status"], hosts_b[h]["status"]
        if sa == sb:
            continue
        direction = "improved" if _STATUS_PRIO.get(sb, 2) > _STATUS_PRIO.get(sa, 2) else "worsened"
        changed.append({
            "shorthost":   h,
            "status_from": sa,
            "status_to":   sb,
            "direction":   direction,
            "os_name":     hosts_b[h].get("os_name", ""),
            "owner":       hosts_b[h].get("owner", ""),
            "division":    hosts_b[h].get("division", ""),
            "reason_to":   hosts_b[h].get("reason", ""),
        })
    return {"new": new_hosts, "removed": removed, "changed": changed}


# ── Helpers ──────────────────────────────────────────────────

def _filter_rows(args: dict) -> list[ReportRow]:
    rows = _rows
    if status := args.get("status"):
        rows = [r for r in rows if r.status.value == status]
    if family := args.get("family"):
        rows = [r for r in rows if r.family == family]
    if division := args.get("division"):
        rows = [r for r in rows if r.division == division]
    if resource_status := args.get("resource_status"):
        rows = [r for r in rows if r.resource_status == resource_status]
    if q := args.get("q", "").lower():
        rows = [r for r in rows
                if q in (r.shorthost + r.os_name + r.owner + r.division + r.reason).lower()]
    return rows


def _sort_rows(rows: list[ReportRow], sort: str, dir_: str) -> list[ReportRow]:
    if not sort:
        return rows
    return sorted(rows,
                  key=lambda r: (getattr(r, sort, "") or "").lower(),
                  reverse=(dir_ == "desc"))


def _row_to_dict(r: ReportRow) -> dict:
    return {
        "shorthost": r.shorthost,
        "os_name":   r.os_name,
        "owner":     r.owner,
        "division":  r.division,
        "ke_type":   r.ke_type,
        "family":    r.family,
        "status":    r.status.value,
        "reason":    r.reason,
        "resource_status": r.resource_status,
        "ip_address": r.ip_address,
    }


# ── Data loading ─────────────────────────────────────────────

def load_data(progress: "ScanProgress | None" = None) -> None:
    global _rows, _summary, _divisions
    if progress is None:
        progress = ScanProgress()
    config = load_config([])
    client = CmdbClient(config)

    progress.phase(1)                       # Авторизация
    client.check_auth()

    progress.phase(2)                       # Загрузка филиалов
    branch_uuid = client.get_ci_type_uuid("branches")
    bu, bn, bname = build_branch_maps(client.iter_cis(branch_uuid))
    log.info("%d branches loaded, %d names indexed", len(bu), len(bname))

    progress.phase(3)                       # Карта host→branch
    hbm = client.build_host_branch_map(bu, on_progress=progress.tick)
    log.info("host_branch_map: %d entries", len(hbm))

    progress.phase(4)                       # Загрузка ACCOUNT
    try:
        account_uuid = client.get_ci_type_uuid("ACCOUNT")
        adm = build_account_division_map(client.iter_cis(account_uuid), bname)
        log.info("account_division_map: %d entries", len(adm))
    except Exception as e:
        log.warning("Could not load ACCOUNT CIs: %s", e)
        adm = {}

    host_uuid = client.get_ci_type_uuid("HOST")
    vm_uuid   = client.get_ci_type_uuid("VM")

    progress.phase(5)                       # Загрузка HOST
    host_cis = list(client.iter_cis(host_uuid, on_page=progress.tick))
    progress.phase(6)                       # Загрузка VM
    vm_cis = list(client.iter_cis(vm_uuid, on_page=progress.tick))

    progress.phase(7)                       # Загрузка IP
    try:
        ip_uuid = client.get_ci_type_uuid("IP")
        ip_map = build_ip_map(client.iter_cis(ip_uuid, on_page=progress.tick))
        log.info("ip_map: %d entries", len(ip_map))
    except Exception as e:
        log.warning("Could not load IP CIs: %s", e)
        ip_map = {}

    inventory = build_inventory(host_cis, vm_cis, bu, bn, bname, hbm, adm, ip_map)
    log.info("%d unique KEs", len(inventory))

    progress.phase(8)                       # Сборка отчёта
    _rows      = build_report(inventory)
    _summary   = summarize(_rows)
    _divisions = sorted({r.division for r in _rows if r.division})
    log.info("Done — %d KEs | NON_COMPLIANT: %d | OK: %d",
             len(_rows), _summary["NON_COMPLIANT"], _summary["OK"])
    save_snapshot(_rows, source="cmdb")


def _run_scan() -> None:
    progress = ScanProgress()
    try:
        load_data(progress)
        with _scan_lock:
            _scan_state["data_version"] += 1
            _scan_state["error"] = None
    except Exception as e:
        with _scan_lock:
            _scan_state["error"] = str(e)
        log.exception("Scan failed")
    finally:
        with _scan_lock:
            _scan_state["running"] = False
            _scan_state["finished_at"] = datetime.now().isoformat(timespec="seconds")


# ── Routes ───────────────────────────────────────────────────

@app.route("/")
def index() -> str:
    return _HTML


@app.route("/api/scan/start", methods=["POST"])
def api_scan_start():
    with _scan_lock:
        if _scan_state["running"]:
            return jsonify({"error": "Сканирование уже выполняется"}), 409
        _scan_state.update(
            running=True, phase="", phase_index=0, percent=0, detail="",
            error=None, finished_at=None,
            started_at=datetime.now().isoformat(timespec="seconds"),
        )
    threading.Thread(target=_run_scan, daemon=True).start()
    return jsonify({"started": True}), 202


@app.route("/api/scan/status")
def api_scan_status():
    with _scan_lock:
        return jsonify(dict(_scan_state))


@app.route("/api/stats")
def api_stats():
    return jsonify(_summary)


@app.route("/api/divisions")
def api_divisions():
    return jsonify({"divisions": _divisions})


@app.route("/api/resource_statuses")
def api_resource_statuses():
    vals = sorted({r.resource_status for r in _rows if r.resource_status})
    return jsonify({"resource_statuses": vals})


_RTT_RE = re.compile(r"time[=<]\s*(\d+)\s*ms", re.IGNORECASE)


@app.route("/api/ping", methods=["POST"])
def api_ping():
    body = request.get_json(silent=True) or {}
    shorthost = (body.get("shorthost") or "").strip()
    if not shorthost:
        return jsonify({"error": "shorthost обязателен"}), 400
    if not any(r.shorthost == shorthost for r in _rows):
        return jsonify({"error": "Хост не найден в инвентаре"}), 400

    try:
        ip = socket.gethostbyname(shorthost)
    except socket.gaierror as e:
        return jsonify({"alive": False, "ip": None, "rtt_ms": None,
                        "error": f"DNS: {e}"})

    try:
        proc = subprocess.run(
            ["ping", "-n", "1", "-w", "1000", ip],
            capture_output=True, text=True, shell=False, timeout=5,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        return jsonify({"alive": False, "ip": ip, "rtt_ms": None,
                        "error": str(e)})

    alive = proc.returncode == 0
    rtt = None
    m = _RTT_RE.search(proc.stdout or "")
    if m:
        rtt = int(m.group(1))
    return jsonify({"alive": alive, "ip": ip, "rtt_ms": rtt, "error": None})


@app.route("/api/data")
def api_data():
    args  = request.args
    rows  = _filter_rows(args)
    rows  = _sort_rows(rows, args.get("sort", ""), args.get("dir", "asc"))
    total = len(rows)
    size  = min(max(int(args.get("size",  100) or 100), 1), 500)
    page  = max(int(args.get("page",    1)   or 1),   1)
    pages = max(1, -(-total // size))
    start = (page - 1) * size
    return jsonify({
        "data":  [_row_to_dict(r) for r in rows[start: start + size]],
        "total": total,
        "page":  page,
        "pages": pages,
    })


@app.route("/api/export")
def api_export():
    args  = request.args
    rows  = _filter_rows(args)
    rows  = _sort_rows(rows, args.get("sort", ""), args.get("dir", "asc"))
    buf   = io.StringIO()
    w     = csv.writer(buf)
    w.writerow(["shorthost", "os_name", "owner", "division",
                "ke_type", "family", "resource_status", "status", "reason"])
    for r in rows:
        w.writerow([r.shorthost, r.os_name, r.owner, r.division,
                    r.ke_type, r.family, r.resource_status, r.status.value, r.reason])
    return Response(
        "﻿" + buf.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=os_compliance_filtered.csv"},
    )


@app.route("/api/snapshots")
def api_snapshots():
    return jsonify(list_snapshots())


@app.route("/api/trend")
def api_trend():
    return jsonify({"snapshots": list_snapshots()})


@app.route("/api/compare")
def api_compare():
    id_a = request.args.get("a", "")
    id_b = request.args.get("b", "")
    if not id_a or not id_b:
        return jsonify({"error": "params a and b required"}), 400
    try:
        snap_a = load_snapshot(id_a)
        snap_b = load_snapshot(id_b)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify({
        "snap_a": {k: snap_a[k] for k in ("id", "timestamp", "source", "summary")},
        "snap_b": {k: snap_b[k] for k in ("id", "timestamp", "source", "summary")},
        "diff":   compare_snapshots(snap_a, snap_b),
    })


@app.route("/api/snapshots/import", methods=["POST"])
def api_import_snapshot():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "no file"}), 400
    snap_id = import_csv_snapshot(f.read(), f.filename or "")
    data    = load_snapshot(snap_id)
    return jsonify({k: data[k] for k in ("id", "timestamp", "source", "summary")})


_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CMDB OS Compliance</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; color: #1a1a2e; }
  .page { max-width: 1500px; margin: 0 auto; padding: 24px 20px; }
  .header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
            color: #fff; border-radius: 12px; padding: 28px 32px; margin-bottom: 16px; }
  .header h1 { font-size: 22px; font-weight: 700; }
  .header .meta { margin-top: 6px; font-size: 13px; opacity: .7; }
  .tabs { display: flex; gap: 4px; margin-bottom: 16px; }
  .tab-btn { padding: 10px 22px; border: none; border-radius: 8px 8px 0 0; background: #e5e7eb;
             cursor: pointer; font-size: 14px; font-weight: 500; color: #6b7280; transition: all .15s; }
  .tab-btn.active { background: #fff; color: #0f3460; box-shadow: 0 -2px 0 #0f3460 inset; }
  .tab-ico { width: 15px; height: 15px; vertical-align: -2px; margin-right: 2px; }
  .tab-content { display: none; }
  .tab-content.active { display: block; }
  .cards { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }
  .card { flex: 1; min-width: 140px; background: #fff; border-radius: 10px; padding: 18px 20px;
          box-shadow: 0 1px 4px rgba(0,0,0,.08); cursor: pointer; transition: box-shadow .15s; }
  .card:hover { box-shadow: 0 4px 12px rgba(0,0,0,.15); }
  .card .num { font-size: 32px; font-weight: 700; line-height: 1; }
  .card .lbl { font-size: 12px; color: #666; margin-top: 4px; text-transform: uppercase; letter-spacing: .6px; }
  .card.total .num { color: #1a1a2e; } .card.ok .num { color: #16a34a; }
  .card.warn  .num { color: #d97706; } .card.fail .num { color: #dc2626; }
  .card.unk   .num { color: #6b7280; }
  .filterbar { background: #fff; border-radius: 10px; padding: 14px 20px;
               margin-bottom: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
  .filter-row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 8px; }
  .filter-row:last-child { margin-bottom: 0; }
  .filter-label { font-size: 11px; font-weight: 600; color: #6b7280;
                  text-transform: uppercase; white-space: nowrap; min-width: 60px; }
  .filter-btn { padding: 7px 14px; border: 1px solid #d1d5db; border-radius: 6px;
                background: #fff; cursor: pointer; font-size: 13px; font-weight: 500; transition: all .15s; }
  .filter-btn:hover { background: #f3f4f6; }
  .filter-btn.active { background: #0f3460; color: #fff; border-color: #0f3460; }
  .filter-btn.fam-ws.active { background: #7c3aed; border-color: #7c3aed; }
  .filter-btn.fam-wc.active { background: #2563eb; border-color: #2563eb; }
  .filter-btn.fam-lx.active { background: #059669; border-color: #059669; }
  .filter-btn.fam-unk.active { background: #6b7280; border-color: #6b7280; }
  .sel { padding: 7px 10px; border: 1px solid #d1d5db; border-radius: 6px;
         font-size: 13px; cursor: pointer; background: #fff; max-width: 300px; }
  .filterbar input[type=text] { flex: 1; min-width: 200px; padding: 8px 12px;
                                  border: 1px solid #d1d5db; border-radius: 6px;
                                  font-size: 14px; outline: none; }
  .filterbar input[type=text]:focus { border-color: #0f3460; box-shadow: 0 0 0 3px rgba(15,52,96,.12); }
  .export-btn, .action-btn { padding: 7px 16px; border: 1px solid #0f3460; border-radius: 6px;
                background: #0f3460; color: #fff; cursor: pointer; font-size: 13px;
                font-weight: 500; white-space: nowrap; transition: background .15s; }
  .export-btn:hover, .action-btn:hover { background: #16213e; }
  .action-btn.secondary { background: #fff; color: #0f3460; }
  .action-btn.secondary:hover { background: #f0f2f5; }
  .table-wrap { background: #fff; border-radius: 10px; overflow: hidden;
                box-shadow: 0 1px 4px rgba(0,0,0,.08); }
  table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
  thead th { background: #1a1a2e; color: #fff; padding: 12px 14px; text-align: left;
             font-weight: 600; font-size: 12px; text-transform: uppercase; white-space: nowrap;
             cursor: pointer; user-select: none; }
  thead th:hover { background: #16213e; }
  thead th.sort-asc::after { content: ' \u25b2'; } thead th.sort-desc::after { content: ' \u25bc'; }
  tbody tr { border-bottom: 1px solid #f0f0f0; transition: background .1s; }
  tbody tr:last-child { border-bottom: none; }
  td { padding: 10px 14px; vertical-align: top; }
  td.host { font-family: Consolas,monospace; font-size: 13px; font-weight: 600; color: #0f3460; }
  td.os { color: #374151; } td.own { color: #4b5563; font-size: 13px; }
  td.div { font-size: 12px; color: #6b7280; } td.ke { font-size: 12px; color: #6b7280; white-space: nowrap; }
  td.fam { font-size: 11px; color: #9ca3af; white-space: nowrap; } td.reason { font-size: 12px; color: #6b7280; }
  .row-fail    { background: #fff5f5; } .row-fail:hover    { background: #fee2e2; }
  .row-warning { background: #fffbeb; } .row-warning:hover { background: #fef3c7; }
  .row-ok      { background: #f0fdf4; } .row-ok:hover      { background: #dcfce7; }
  .row-unknown { background: #f9fafb; } .row-unknown:hover { background: #f3f4f6; }
  .badge { display: inline-block; padding: 3px 10px; border-radius: 12px;
           font-size: 11px; font-weight: 700; white-space: nowrap; }
  .badge.ok      { background: #dcfce7; color: #15803d; }
  .badge.warning { background: #fef3c7; color: #b45309; }
  .badge.fail    { background: #fee2e2; color: #b91c1c; }
  .badge.unknown { background: #f3f4f6; color: #6b7280; }
  .badge.new     { background: #dbeafe; color: #1d4ed8; }
  .badge.removed { background: #f3f4f6; color: #374151; }
  .badge.worse   { background: #fee2e2; color: #b91c1c; }
  .badge.better  { background: #dcfce7; color: #15803d; }
  .pagination { display: flex; align-items: center; justify-content: space-between;
                padding: 14px 20px; border-top: 1px solid #f0f0f0; flex-wrap: wrap; gap: 10px; }
  .pag-info { font-size: 13px; color: #6b7280; }
  .pag-controls { display: flex; gap: 4px; align-items: center; flex-wrap: wrap; }
  .pag-btn { min-width: 34px; height: 34px; padding: 0 10px; border: 1px solid #d1d5db;
             border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px;
             display: flex; align-items: center; justify-content: center; }
  .pag-btn.active { background: #0f3460; color: #fff; border-color: #0f3460; font-weight: 700; }
  .pag-btn:disabled { opacity: .4; cursor: default; }
  .pag-ellipsis { padding: 0 6px; color: #9ca3af; }
  .history-table { width: 100%; border-collapse: collapse; }
  .history-table th { background: #1a1a2e; color: #fff; padding: 10px 14px;
                       text-align: left; font-size: 12px; text-transform: uppercase; }
  .history-table td { padding: 10px 14px; border-bottom: 1px solid #f0f0f0; font-size: 13px; }
  .history-table tr:hover td { background: #f9fafb; }
  .src-badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
  .src-cmdb { background: #dbeafe; color: #1d4ed8; } .src-csv { background: #fef3c7; color: #b45309; }
  .chart-wrap { background: #fff; border-radius: 10px; padding: 24px;
                box-shadow: 0 1px 4px rgba(0,0,0,.08); }
  .chart-legend { display: flex; gap: 20px; margin-bottom: 16px; font-size: 13px; }
  .legend-dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 6px; }
  .compare-controls { background: #fff; border-radius: 10px; padding: 20px;
                      box-shadow: 0 1px 4px rgba(0,0,0,.08); margin-bottom: 16px;
                      display: flex; gap: 16px; align-items: flex-end; flex-wrap: wrap; }
  .compare-controls label { font-size: 12px; font-weight: 600; color: #6b7280;
                             text-transform: uppercase; display: block; margin-bottom: 4px; }
  .diff-summary { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
  .diff-card { flex: 1; min-width: 120px; background: #fff; border-radius: 10px;
               padding: 14px 16px; box-shadow: 0 1px 4px rgba(0,0,0,.08); text-align: center;
               cursor: pointer; border: 2px solid transparent; transition: border-color .15s, transform .1s; }
  .diff-card:hover { transform: translateY(-1px); }
  .diff-card.active { border-color: #0f3460; }
  .diff-card .num { font-size: 28px; font-weight: 700; }
  .diff-card .lbl { font-size: 11px; color: #6b7280; text-transform: uppercase; margin-top: 4px; }
  .diff-card.worse .num { color: #dc2626; } .diff-card.better .num { color: #16a34a; }
  .diff-card.newc  .num { color: #2563eb; } .diff-card.remc  .num { color: #6b7280; }
  .panel { background: #fff; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
  .loading { padding: 60px; text-align: center; color: #9ca3af; font-size: 14px; }
  .empty   { padding: 40px; text-align: center; color: #9ca3af; font-size: 14px; }
  .footer  { text-align: center; margin-top: 20px; font-size: 12px; color: #9ca3af; }
  .scanbar { display:flex; justify-content:flex-end; margin-bottom:12px; }
  .scan-btn { display:inline-flex; align-items:center; gap:8px; padding:8px 16px;
              border:1px solid #0f3460; border-radius:8px; background:#0f3460;
              color:#fff; cursor:pointer; font-size:13px; font-weight:600; transition:background .15s; }
  .scan-btn:hover:not(:disabled) { background:#16213e; }
  .scan-btn:disabled { opacity:.5; cursor:default; }
  .scan-btn svg { display:block; }
  .scan-banner { display:none; background:#fff; border-radius:10px; padding:14px 20px;
                 margin-bottom:16px; box-shadow:0 1px 4px rgba(0,0,0,.08); border-left:4px solid #0f3460; }
  .scan-banner.error { border-left-color:#dc2626; }
  .scan-banner-row { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }
  .scan-phase { font-size:13px; font-weight:600; color:#1a1a2e; }
  .scan-pct { font-size:13px; color:#6b7280; font-variant-numeric:tabular-nums; }
  .scan-track { height:8px; background:#e5e7eb; border-radius:4px; overflow:hidden; }
  .scan-fill { height:100%; width:0%; background:linear-gradient(90deg,#0f3460,#2563eb);
               border-radius:4px; transition:width .4s ease; }
  .scan-retry { padding:4px 10px; font-size:12px; border:1px solid #dc2626;
                border-radius:6px; background:#fff; color:#dc2626; cursor:pointer; }
  .rbadge { display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600;
            white-space:nowrap; }
  .rbadge.active  { background:#dcfce7; color:#166534; }
  .rbadge.retired { background:#fee2e2; color:#991b1b; }
  .rbadge.reserve { background:#fef9c3; color:#854d0e; }
  .rbadge.other   { background:#e0e7ff; color:#3730a3; }
  .rbadge.none    { background:#f3f4f6; color:#9ca3af; }
  .host-link { cursor:pointer; border-bottom:1px dashed #94a3b8; }
  .host-link:hover { color:#2563eb; border-bottom-color:#2563eb; }
  .ping-res { margin-left:6px; }
  .ping-badge { display:inline-block; padding:1px 6px; border-radius:8px; font-size:10px; font-weight:700; }
  .ping-badge.wait { background:#e0e7ff; color:#3730a3; }
  .ping-badge.on   { background:#dcfce7; color:#166534; }
  .ping-badge.off  { background:#fee2e2; color:#991b1b; }
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <h1>CMDB OS Compliance</h1>
    <div class="meta" id="meta">\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u0434\u0430\u043d\u043d\u044b\u0445\u2026</div>
  </div>
  <div class="scanbar">
    <button class="scan-btn" id="scan-btn" onclick="startScan()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
      \u0421\u043a\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u0442\u044c
    </button>
  </div>
  <div class="scan-banner" id="scan-banner">
    <div class="scan-banner-row">
      <span class="scan-phase" id="scan-phase"></span>
      <span class="scan-pct" id="scan-pct"></span>
    </div>
    <div class="scan-track"><div class="scan-fill" id="scan-fill"></div></div>
  </div>
  <div class="tabs">
    <button class="tab-btn active" onclick="showTab('table')"><svg class="tab-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="16" rx="1"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="14" x2="21" y2="14"/><line x1="9" y1="9" x2="9" y2="20"/></svg>\u0422\u0430\u0431\u043b\u0438\u0446\u0430</button>
    <button class="tab-btn"        onclick="showTab('history')"><svg class="tab-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 16 14"/></svg>\u0418\u0441\u0442\u043e\u0440\u0438\u044f</button>
    <button class="tab-btn"        onclick="showTab('trend')"><svg class="tab-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 17 9 11 13 15 21 6"/><polyline points="14 6 21 6 21 13"/></svg>\u0422\u0440\u0435\u043d\u0434</button>
    <button class="tab-btn"        onclick="showTab('compare')"><svg class="tab-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="3" x2="12" y2="21"/><polyline points="5 7 12 5 19 7"/><path d="M5 7 L2 14 a3 3 0 0 0 6 0 Z"/><path d="M19 7 L16 14 a3 3 0 0 0 6 0 Z"/></svg>\u0421\u0440\u0430\u0432\u043d\u0435\u043d\u0438\u0435</button>
  </div>

  <div id="tab-table" class="tab-content active">
    <div class="cards">
      <div class="card total" onclick="setStatus('')" ><div class="num" id="cnt-total">\u2026</div><div class="lbl">\u0412\u0441\u0435\u0433\u043e</div></div>
      <div class="card ok"   onclick="setStatus('OK')" ><div class="num" id="cnt-ok">\u2026</div><div class="lbl">\u0421\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u0435\u0442</div></div>
      <div class="card warn" onclick="setStatus('WARNING')" ><div class="num" id="cnt-warn">\u2026</div><div class="lbl">\u0423\u0441\u043b\u043e\u0432\u043d\u043e</div></div>
      <div class="card fail" onclick="setStatus('NON_COMPLIANT')" ><div class="num" id="cnt-fail">\u2026</div><div class="lbl">\u041d\u0435 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u0435\u0442</div></div>
      <div class="card unk"  onclick="setStatus('UNKNOWN')" ><div class="num" id="cnt-unk">\u2026</div><div class="lbl">\u041d\u0435\u0442 \u0434\u0430\u043d\u043d\u044b\u0445</div></div>
    </div>
    <div class="filterbar">
      <div class="filter-row">
        <span class="filter-label">\u0421\u0442\u0430\u0442\u0443\u0441</span>
        <button class="filter-btn active" data-status="" onclick="setStatus('')" >\u0412\u0441\u0435</button>
        <button class="filter-btn" data-status="NON_COMPLIANT" onclick="setStatus('NON_COMPLIANT')" >\u041d\u0435 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u0435\u0442</button>
        <button class="filter-btn" data-status="WARNING" onclick="setStatus('WARNING')" >\u0423\u0441\u043b\u043e\u0432\u043d\u043e</button>
        <button class="filter-btn" data-status="OK" onclick="setStatus('OK')" >OK</button>
        <button class="filter-btn" data-status="UNKNOWN" onclick="setStatus('UNKNOWN')" >\u041d\u0435\u0442 \u0434\u0430\u043d\u043d\u044b\u0445</button>
      </div>
      <div class="filter-row">
        <span class="filter-label">\u041e\u0421</span>
        <button class="filter-btn active" data-fam="" onclick="setFamily('')" >\u0412\u0441\u0435</button>
        <button class="filter-btn fam-ws" data-fam="windows_server" onclick="setFamily('windows_server')" >Windows Server</button>
        <button class="filter-btn fam-wc" data-fam="windows_client" onclick="setFamily('windows_client')" >Windows Client</button>
        <button class="filter-btn fam-lx" data-fam="linux" onclick="setFamily('linux')" >Linux</button>
        <button class="filter-btn fam-unk" data-fam="unknown" onclick="setFamily('unknown')" >\u041d\u0435\u0438\u0437\u0432\u0435\u0441\u0442\u043d\u043e</button>
      </div>
      <div class="filter-row">
        <span class="filter-label">\u0414\u0438\u0432\u0438\u0437\u0438\u043e\u043d</span>
        <select class="sel" id="div-sel" onchange="setDivision(this.value)"><option value="">\u0412\u0441\u0435 \u0434\u0438\u0432\u0438\u0437\u0438\u043e\u043d\u044b</option></select>
        <span class="filter-label">\u0421\u0442\u0430\u0442\u0443\u0441 \u0440\u0435\u0441\u0443\u0440\u0441\u0430</span>
        <select class="sel" id="rstatus-sel" onchange="setResourceStatus(this.value)"><option value="">\u041b\u044e\u0431\u043e\u0439 \u0441\u0442\u0430\u0442\u0443\u0441</option></select>
        <select class="sel" onchange="changeSize(this.value)" style="margin-left:auto">
          <option value="50">50 / \u0441\u0442\u0440.</option><option value="100" selected>100 / \u0441\u0442\u0440.</option>
          <option value="200">200 / \u0441\u0442\u0440.</option><option value="500">500 / \u0441\u0442\u0440.</option>
        </select>
      </div>
      <div class="filter-row">
        <span class="filter-label">\u041f\u043e\u0438\u0441\u043a</span>
        <input type="text" id="search" placeholder="\u041f\u043e\u0438\u0441\u043a \u043f\u043e \u0445\u043e\u0441\u0442\u0443, \u041e\u0421, \u0432\u043b\u0430\u0434\u0435\u043b\u044c\u0446\u0443\u2026" oninput="debounceSearch(this.value)">
        <button class="export-btn" onclick="exportCSV()">&#11015; \u0421\u043a\u0430\u0447\u0430\u0442\u044c CSV</button>
      </div>
    </div>
    <div class="table-wrap">
      <table><thead id="thead"></thead>
      <tbody id="tbody"><tr><td class="loading" colspan="9">\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430\u2026</td></tr></tbody></table>
      <div class="pagination">
        <div class="pag-info" id="pag-info"></div>
        <div class="pag-controls" id="pag-controls"></div>
      </div>
    </div>
  </div>

  <div id="tab-history" class="tab-content">
    <div class="panel" style="margin-bottom:16px;padding:16px 20px;display:flex;gap:12px;align-items:center">
      <strong style="font-size:14px">\u0418\u043c\u043f\u043e\u0440\u0442 CSV-\u043e\u0442\u0447\u0451\u0442\u0430</strong>
      <input type="file" id="csv-file" accept=".csv" style="font-size:13px">
      <button class="action-btn" onclick="importCSV()">\u0417\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044c</button>
      <span id="import-status" style="font-size:13px;color:#6b7280"></span>
    </div>
    <div class="table-wrap">
      <table class="history-table">
        <thead><tr>
          <th>\u0414\u0430\u0442\u0430</th><th>\u0418\u0441\u0442\u043e\u0447\u043d\u0438\u043a</th><th>\u0412\u0441\u0435\u0433\u043e</th>
          <th style="color:#86efac">OK</th><th style="color:#fcd34d">WARNING</th>
          <th style="color:#fca5a5">NON_COMPLIANT</th><th></th>
        </tr></thead>
        <tbody id="history-tbody"><tr><td class="loading" colspan="7">\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430\u2026</td></tr></tbody>
      </table>
    </div>
  </div>

  <div id="tab-trend" class="tab-content">
    <div class="chart-wrap">
      <div class="chart-legend">
        <span><span class="legend-dot" style="background:#16a34a"></span>OK</span>
        <span><span class="legend-dot" style="background:#d97706"></span>WARNING</span>
        <span><span class="legend-dot" style="background:#dc2626"></span>NON_COMPLIANT</span>
      </div>
      <svg id="trend-svg" width="100%" height="340" style="display:block"></svg>
      <div id="trend-empty" class="empty" style="display:none">\u041d\u0435\u0434\u043e\u0441\u0442\u0430\u0442\u043e\u0447\u043d\u043e \u0434\u0430\u043d\u043d\u044b\u0445 \u2014 \u043d\u0443\u0436\u043d\u043e \u043c\u0438\u043d\u0438\u043c\u0443\u043c 2 \u0441\u043d\u0438\u043c\u043a\u0430</div>
    </div>
  </div>

  <div id="tab-compare" class="tab-content">
    <div class="compare-controls">
      <div><label>\u0421\u043d\u0438\u043c\u043e\u043a A (\u0441\u0442\u0430\u0440\u044b\u0439)</label><select class="sel" id="cmp-a" style="min-width:260px"></select></div>
      <div><label>\u0421\u043d\u0438\u043c\u043e\u043a B (\u043d\u043e\u0432\u044b\u0439)</label><select class="sel" id="cmp-b" style="min-width:260px"></select></div>
      <button class="action-btn" onclick="runCompare()">\u0421\u0440\u0430\u0432\u043d\u0438\u0442\u044c</button>
    </div>
    <div id="diff-summary" class="diff-summary" style="display:none">
      <div class="diff-card worse" data-diff="worsened" onclick="setDiffFilter(this)"><div class="num" id="diff-worse">0</div><div class="lbl">\u0423\u0445\u0443\u0434\u0448\u0438\u043b\u0438\u0441\u044c</div></div>
      <div class="diff-card better" data-diff="improved" onclick="setDiffFilter(this)"><div class="num" id="diff-better">0</div><div class="lbl">\u0423\u043b\u0443\u0447\u0448\u0438\u043b\u0438\u0441\u044c</div></div>
      <div class="diff-card newc" data-diff="new" onclick="setDiffFilter(this)"><div class="num" id="diff-new">0</div><div class="lbl">\u041d\u043e\u0432\u044b\u0435</div></div>
      <div class="diff-card remc" data-diff="removed" onclick="setDiffFilter(this)"><div class="num" id="diff-removed">0</div><div class="lbl">\u0423\u0434\u0430\u043b\u0451\u043d\u043d\u044b\u0435</div></div>
    </div>
    <div id="diff-filter-row" style="display:none;margin-bottom:12px">
      <div class="filterbar" style="padding:10px 16px">
        <div class="filter-row">
          <button class="filter-btn active" data-diff="all"      onclick="setDiffFilter(this)">\u0412\u0441\u0435</button>
          <button class="filter-btn"        data-diff="worsened" onclick="setDiffFilter(this)">\u0423\u0445\u0443\u0434\u0448\u0438\u043b\u0438\u0441\u044c</button>
          <button class="filter-btn"        data-diff="improved" onclick="setDiffFilter(this)">\u0423\u043b\u0443\u0447\u0448\u0438\u043b\u0438\u0441\u044c</button>
          <button class="filter-btn"        data-diff="new"      onclick="setDiffFilter(this)">\u041d\u043e\u0432\u044b\u0435</button>
          <button class="filter-btn"        data-diff="removed"  onclick="setDiffFilter(this)">\u0423\u0434\u0430\u043b\u0451\u043d\u043d\u044b\u0435</button>
        </div>
      </div>
    </div>
    <div class="table-wrap" id="diff-table-wrap" style="display:none">
      <table>
        <thead><tr style="background:#1a1a2e;color:#fff">
          <th style="padding:10px 14px;font-size:12px">\u0425\u043e\u0441\u0442</th>
          <th style="padding:10px 14px;font-size:12px">\u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435</th>
          <th style="padding:10px 14px;font-size:12px">\u041e\u0421</th>
          <th style="padding:10px 14px;font-size:12px">\u0412\u043b\u0430\u0434\u0435\u043b\u0435\u0446</th>
          <th style="padding:10px 14px;font-size:12px">\u0414\u0438\u0432\u0438\u0437\u0438\u043e\u043d</th>
          <th style="padding:10px 14px;font-size:12px">\u041f\u0440\u0438\u0447\u0438\u043d\u0430 (\u043d\u043e\u0432\u0430\u044f)</th>
        </tr></thead>
        <tbody id="diff-tbody"></tbody>
      </table>
    </div>
    <div id="diff-empty" class="empty" style="display:none">\u041d\u0435\u0442 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0439 \u043c\u0435\u0436\u0434\u0443 \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u043c\u0438 \u0441\u043d\u0438\u043c\u043a\u0430\u043c\u0438</div>
  </div>

  <div class="footer">\u0420\u0435\u0433\u043b\u0430\u043c\u0435\u043d\u0442 \u0434\u043e\u043f\u0443\u0441\u0442\u0438\u043c\u044b\u0445 \u041e\u0421 \u043e\u0442 13.05.2026 &nbsp;&middot;&nbsp; CMDB OS Compliance</div>
</div>
<script>
function esc(s){return String(s||''). replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function fmtTs(ts){return ts?ts.replace('T',' ').slice(0,16):'';}
const TABS=['table','history','trend','compare'];
function showTab(name){
  document.querySelectorAll('.tab-content').forEach(el=>el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el=>el.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  document.querySelectorAll('.tab-btn')[TABS.indexOf(name)].classList.add('active');
  if(name==='history')loadHistory();
  if(name==='trend')loadTrend();
  if(name==='compare')loadCompareSelects();
}
const COLS=[
  {f:'shorthost',label:'\u0425\u043e\u0441\u0442',cls:'host'},{f:'os_name',label:'\u041e\u0421',cls:'os'},
  {f:'owner',label:'\u0412\u043b\u0430\u0434\u0435\u043b\u0435\u0446',cls:'own'},{f:'division',label:'\u0414\u0438\u0432\u0438\u0437\u0438\u043e\u043d',cls:'div'},
  {f:'ke_type',label:'\u0422\u0438\u043f \u041a\u0415',cls:'ke'},{f:'family',label:'\u0421\u0435\u043c\u0435\u0439\u0441\u0442\u0432\u043e',cls:'fam'},
  {f:'resource_status',label:'\u0421\u0442\u0430\u0442\u0443\u0441 \u0440\u0435\u0441\u0443\u0440\u0441\u0430',cls:'rstatus'},
  {f:'status',label:'\u0421\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0438\u0435',cls:''},{f:'reason',label:'\u041f\u0440\u0438\u0447\u0438\u043d\u0430',cls:'reason'},
];
const ROW_CLASS={OK:'row-ok',WARNING:'row-warning',NON_COMPLIANT:'row-fail',UNKNOWN:'row-unknown'};
function resBadge(v){
  if(!v)return '<span class="rbadge none">\u2014</span>';
  const s=v.toLowerCase();
  let cls='other';
  if(/(\u044d\u043a\u0441\u043f\u043b\u0443\u0430\u0442|\u0430\u043a\u0442\u0438\u0432|\u0440\u0430\u0431\u043e\u0442|active|in use|production|prod)/.test(s))cls='active';
  else if(/(\u0432\u044b\u0432\u0435\u0434|\u0441\u043f\u0438\u0441\u0430\u043d|\u0434\u0435\u043a\u043e\u043c|\u0443\u0442\u0438\u043b\u0438\u0437|\u0430\u0440\u0445\u0438\u0432|decom|retired|disposed|inactive)/.test(s))cls='retired';
  else if(/(\u0440\u0435\u0437\u0435\u0440\u0432|\u0445\u0440\u0430\u043d|\u0441\u043a\u043b\u0430\u0434|storage|reserve|spare|stock)/.test(s))cls='reserve';
  return '<span class="rbadge '+cls+'">'+esc(v)+'</span>';
}
function pingHost(el){
  const shorthost=el.textContent;
  const cell=el.parentElement.querySelector('.ping-res');
  cell.innerHTML='<span class="ping-badge wait">…</span>';
  fetch('/api/ping',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({shorthost})})
    .then(r=>r.json()).then(d=>{
      if(d.error&&d.ip===null&&!d.alive){cell.innerHTML='<span class="ping-badge off" title="'+esc(d.error)+'">DNS?</span>';return;}
      if(d.alive){const rtt=(d.rtt_ms!=null)?(d.rtt_ms+' ms'):'online';cell.innerHTML='<span class="ping-badge on" title="'+esc(d.ip||'')+'">'+rtt+'</span>';}
      else{cell.innerHTML='<span class="ping-badge off" title="'+esc(d.ip||'')+'">offline</span>';}
    }).catch(()=>{cell.innerHTML='<span class="ping-badge off">ERR</span>';});
}
const BADGE={
  OK:'<span class="badge ok">OK</span>',WARNING:'<span class="badge warning">WARNING</span>',
  NON_COMPLIANT:'<span class="badge fail">NON_COMPLIANT</span>',UNKNOWN:'<span class="badge unknown">UNKNOWN</span>',
};
const FAM={windows_server:'Win Server',windows_client:'Win Client',linux:'Linux',unknown:'\u2014'};
let state={page:1,size:100,status:'',family:'',division:'',resource_status:'',q:'',sort:'',dir:'asc'};
let _searchTimer=null;
async function fetchStats(){
  const d=await(await fetch('/api/stats')).json();
  document.getElementById('cnt-total').textContent=d.total;
  document.getElementById('cnt-ok').textContent=d.OK;
  document.getElementById('cnt-warn').textContent=d.WARNING;
  document.getElementById('cnt-fail').textContent=d.NON_COMPLIANT;
  document.getElementById('cnt-unk').textContent=d.UNKNOWN;
  document.getElementById('meta').textContent='\u0412\u0441\u0435\u0433\u043e \u041a\u0415: '+d.total+'  |  NON_COMPLIANT: '+d.NON_COMPLIANT+'  |  OK: '+d.OK;
}
async function fetchDivisions(){
  const d=await(await fetch('/api/divisions')).json();
  const sel=document.getElementById('div-sel');
  const cur=sel.value;
  sel.innerHTML='<option value="">Все дивизионы</option>';
  d.divisions.forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;sel.appendChild(o);});
  if(cur)sel.value=cur;
}
async function fetchResourceStatuses(){
  const d=await(await fetch('/api/resource_statuses')).json();
  const sel=document.getElementById('rstatus-sel');
  const cur=sel.value;
  sel.innerHTML='<option value="">\u041b\u044e\u0431\u043e\u0439 \u0441\u0442\u0430\u0442\u0443\u0441</option>';
  d.resource_statuses.forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;sel.appendChild(o);});
  if(cur)sel.value=cur;
}
async function fetchData(){
  const p=new URLSearchParams({page:state.page,size:state.size});
  if(state.status)p.set('status',state.status);if(state.family)p.set('family',state.family);
  if(state.division)p.set('division',state.division);if(state.q)p.set('q',state.q);
  if(state.resource_status)p.set('resource_status',state.resource_status);
  if(state.sort){p.set('sort',state.sort);p.set('dir',state.dir);}
  document.getElementById('tbody').innerHTML='<tr><td class="loading" colspan="9">\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430\u2026</td></tr>';
  const d=await(await fetch('/api/data?'+p)).json();
  renderHeaders();renderRows(d.data);renderPagination(d.total,d.page,d.pages);
}
function renderHeaders(){
  document.getElementById('thead').innerHTML='<tr>'+COLS.map(c=>{
    const cls=state.sort===c.f?(state.dir==='asc'?' class="sort-asc"':'  class="sort-desc"'):'';
    return '<th'+cls+' onclick="toggleSort(\\''+c.f+'\\')">'+c.label+'</th>';
  }).join('')+'</tr>';
}
function renderRows(rows){
  const tbody=document.getElementById('tbody');
  if(!rows.length){tbody.innerHTML='<tr><td class="empty" colspan="9">\u041d\u0438\u0447\u0435\u0433\u043e \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043e</td></tr>';return;}
  tbody.innerHTML=rows.map(r=>
    '<tr class="'+(ROW_CLASS[r.status]||'')+'">' +
    '<td class="host"><span class="host-link" title="IP: '+esc(r.ip_address||'-')+'" onclick="pingHost(this)">'+esc(r.shorthost)+'</span><span class="ping-res"></span></td><td class="os">'+esc(r.os_name)+'</td>' +
    '<td class="own">'+esc(r.owner)+'</td><td class="div">'+esc(r.division||'\u2014')+'</td>' +
    '<td class="ke">'+esc(r.ke_type)+'</td><td class="fam">'+esc(FAM[r.family]||r.family)+'</td>' +
    '<td class="rstatus">'+resBadge(r.resource_status)+'</td>' +
    '<td>'+(BADGE[r.status]||esc(r.status))+'</td><td class="reason">'+esc(r.reason)+'</td></tr>'
  ).join('');
}
function renderPagination(total,page,pages){
  const start=total?(page-1)*state.size+1:0,end=Math.min(page*state.size,total);
  document.getElementById('pag-info').textContent='\u041f\u043e\u043a\u0430\u0437\u0430\u043d\u043e '+start+'\u2013'+end+' \u0438\u0437 '+total;
  let html='<button class="pag-btn" onclick="goTo(1)" '+(page===1?'disabled':'')+'>&laquo;</button>';
  html+='<button class="pag-btn" onclick="goTo('+(page-1)+')" '+(page===1?'disabled':'')+'>&lsaquo;</button>';
  for(let p=1;p<=pages;p++){
    if(p===1||p===pages||Math.abs(p-page)<=2)
      html+='<button class="pag-btn'+(p===page?' active':'')+'" onclick="goTo('+p+')">'+ p+'</button>';
    else if(Math.abs(p-page)===3)html+='<span class="pag-ellipsis">\u2026</span>';
  }
  html+='<button class="pag-btn" onclick="goTo('+(page+1)+')" '+(page===pages?'disabled':'')+'>&rsaquo;</button>';
  html+='<button class="pag-btn" onclick="goTo('+pages+')" '+(page===pages?'disabled':'')+'>&raquo;</button>';
  document.getElementById('pag-controls').innerHTML=html;
}
function goTo(p){state.page=p;fetchData();window.scrollTo({top:0,behavior:'smooth'});}
function changeSize(v){state.size=+v;state.page=1;fetchData();}
function setStatus(v){state.status=v;state.page=1;document.querySelectorAll('[data-status]').forEach(b=>b.classList.toggle('active',b.dataset.status===v));fetchData();}
function setFamily(v){state.family=v;state.page=1;document.querySelectorAll('[data-fam]').forEach(b=>b.classList.toggle('active',b.dataset.fam===v));fetchData();}
function setDivision(v){state.division=v;state.page=1;fetchData();}
function setResourceStatus(v){state.resource_status=v;state.page=1;fetchData();}
function debounceSearch(v){clearTimeout(_searchTimer);_searchTimer=setTimeout(()=>{state.q=v;state.page=1;fetchData();},300);}
function toggleSort(field){if(state.sort===field){if(state.dir==='asc')state.dir='desc';else{state.sort='';state.dir='asc';}}else{state.sort=field;state.dir='asc';}state.page=1;fetchData();}
function exportCSV(){const p=new URLSearchParams();if(state.status)p.set('status',state.status);if(state.family)p.set('family',state.family);if(state.division)p.set('division',state.division);if(state.resource_status)p.set('resource_status',state.resource_status);if(state.q)p.set('q',state.q);if(state.sort){p.set('sort',state.sort);p.set('dir',state.dir);}window.location='/api/export?'+p;}
async function loadHistory(){
  const snaps=await(await fetch('/api/snapshots')).json();
  const tbody=document.getElementById('history-tbody');
  if(!snaps.length){tbody.innerHTML='<tr><td class="empty" colspan="7">\u041d\u0435\u0442 \u0441\u043d\u0438\u043c\u043a\u043e\u0432</td></tr>';return;}
  tbody.innerHTML=snaps.map(s=>
    '<tr><td>'+esc(fmtTs(s.timestamp))+'</td>' +
    '<td><span class="src-badge src-'+esc(s.source)+'">'+(s.source==='cmdb'?'CMDB':'CSV')+'</span></td>' +
    '<td>'+s.summary.total+'</td><td style="color:#16a34a;font-weight:600">'+s.summary.OK+'</td>' +
    '<td style="color:#d97706;font-weight:600">'+s.summary.WARNING+'</td>' +
    '<td style="color:#dc2626;font-weight:600">'+s.summary.NON_COMPLIANT+'</td>' +
    '<td><button class="action-btn secondary" style="padding:4px 10px;font-size:12px" onclick="preselectCompare(\\''+esc(s.id)+'\\')" >\u0421\u0440\u0430\u0432\u043d\u0438\u0442\u044c</button></td></tr>'
  ).join('');
}
async function importCSV(){
  const input=document.getElementById('csv-file');
  const status=document.getElementById('import-status');
  if(!input.files.length){status.textContent='\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0444\u0430\u0439\u043b';return;}
  status.textContent='\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u044e\u2026';
  const fd=new FormData();fd.append('file',input.files[0]);
  const r=await fetch('/api/snapshots/import',{method:'POST',body:fd});
  const d=await r.json();
  if(d.error){status.textContent='\u041e\u0448\u0438\u0431\u043a\u0430: '+d.error;return;}
  status.textContent='\u0417\u0430\u0433\u0440\u0443\u0436\u0435\u043d \u0441\u043d\u0438\u043c\u043e\u043a \u043e\u0442 '+fmtTs(d.timestamp)+' ('+d.summary.total+' \u041a\u0415)';
  loadHistory();loadCompareSelects();
}
function preselectCompare(snapId){showTab('compare');setTimeout(()=>{const s=document.getElementById('cmp-b');if(s)s.value=snapId;},100);}
async function loadTrend(){
  const d=await(await fetch('/api/trend')).json();
  const snaps=d.snapshots.slice().reverse();
  const svg=document.getElementById('trend-svg');
  const empty=document.getElementById('trend-empty');
  if(snaps.length<2){svg.style.display='none';empty.style.display='block';return;}
  svg.style.display='block';empty.style.display='none';
  drawTrendChart(svg,snaps);
}
function drawTrendChart(svg,snaps){
  const W=svg.clientWidth||900,H=300;
  const PAD={top:20,right:20,bottom:60,left:70};
  const pw=W-PAD.left-PAD.right,ph=H-PAD.top-PAD.bottom;
  const maxVal=Math.max(...snaps.flatMap(s=>[s.summary.OK,s.summary.WARNING,s.summary.NON_COMPLIANT]),1);
  const n=snaps.length;
  function x(i){return PAD.left+(i/(n-1))*pw;}
  function y(v){return PAD.top+ph-(v/maxVal)*ph;}
  function poly(key,color){
    const pts=snaps.map((s,i)=>x(i)+','+y(s.summary[key])).join(' ');
    return '<polyline points="'+pts+'" fill="none" stroke="'+color+'" stroke-width="2.5" stroke-linejoin="round"/>'+
      snaps.map((s,i)=>'<circle cx="'+x(i)+'" cy="'+y(s.summary[key])+'" r="4" fill="'+color+'"><title>'+s.summary[key]+'</title></circle>').join('');
  }
  let grid='',yLbls='';
  for(let i=0;i<=4;i++){
    const yv=PAD.top+ph*(1-i/4),val=Math.round(maxVal*(i/4));
    grid+='<line x1="'+PAD.left+'" y1="'+yv+'" x2="'+( W-PAD.right)+'" y2="'+yv+'" stroke="#f0f0f0"/>';
    yLbls+='<text x="'+(PAD.left-8)+'" y="'+(yv+4)+'" text-anchor="end" font-size="11" fill="#9ca3af">'+val+'</text>';
  }
  const xLbls=snaps.map((s,i)=>'<text x="'+x(i)+'" y="'+(H-PAD.bottom+20)+'" text-anchor="middle" font-size="11" fill="#6b7280">'+esc((s.timestamp||''). slice(0,10))+'</text>').join('');
  svg.setAttribute('viewBox','0 0 '+W+' '+H);
  svg.innerHTML=grid+yLbls+xLbls+poly('OK','#16a34a')+poly('WARNING','#d97706')+poly('NON_COMPLIANT','#dc2626');
}
async function loadCompareSelects(){
  const snaps=await(await fetch('/api/snapshots')).json();
  ['cmp-a','cmp-b'].forEach(id=>{
    const sel=document.getElementById(id);const cur=sel.value;
    sel.innerHTML='<option value="">\u2014 \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0441\u043d\u0438\u043c\u043e\u043a \u2014</option>'+
      snaps.map(s=>'<option value="'+esc(s.id)+'">'+esc(fmtTs(s.timestamp))+' ('+s.source.toUpperCase()+') \u2014 '+s.summary.total+' \u041a\u0415</option>').join('');
    if(cur)sel.value=cur;
  });
}
let _diffData=null,_diffFilter='all';
async function runCompare(){
  const a=document.getElementById('cmp-a').value,b=document.getElementById('cmp-b').value;
  if(!a||!b){alert('\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043e\u0431\u0430 \u0441\u043d\u0438\u043c\u043a\u0430');return;}
  const d=await(await fetch('/api/compare?a='+a+'&b='+b)).json();
  if(d.error){alert('\u041e\u0448\u0438\u0431\u043a\u0430: '+d.error);return;}
  _diffData=d;_diffFilter='all';
  document.querySelectorAll('[data-diff]').forEach(b=>b.classList.toggle('active',b.dataset.diff==='all'));
  renderDiff();
}
function renderDiff(){
  if(!_diffData)return;
  const{diff}=_diffData;
  const worse=diff.changed.filter(h=>h.direction==='worsened');
  const better=diff.changed.filter(h=>h.direction==='improved');
  document.getElementById('diff-worse').textContent=worse.length;
  document.getElementById('diff-better').textContent=better.length;
  document.getElementById('diff-new').textContent=diff.new.length;
  document.getElementById('diff-removed').textContent=diff.removed.length;
  document.getElementById('diff-summary').style.display='flex';
  document.getElementById('diff-filter-row').style.display='block';
  let rows=[];
  if(_diffFilter==='all'||_diffFilter==='worsened')rows=rows.concat(worse.map(h=>diffRow(h,'worsened')));
  if(_diffFilter==='all'||_diffFilter==='improved')rows=rows.concat(better.map(h=>diffRow(h,'improved')));
  if(_diffFilter==='all'||_diffFilter==='new')rows=rows.concat(diff.new.map(h=>({...h,direction:'new'})).map(h=>diffRow(h,'new')));
  if(_diffFilter==='all'||_diffFilter==='removed')rows=rows.concat(diff.removed.map(h=>({...h,direction:'removed'})).map(h=>diffRow(h,'removed')));
  const wrap=document.getElementById('diff-table-wrap'),empty=document.getElementById('diff-empty');
  if(!rows.length){wrap.style.display='none';empty.style.display='block';}
  else{wrap.style.display='block';empty.style.display='none';document.getElementById('diff-tbody').innerHTML=rows.join('');}
}
function diffRow(h,kind){
  const CHANGE_BADGE={
    worsened:'<span class="badge worse">\u2b07 '+esc(h.status_from||h.status)+' \u2192 '+esc(h.status_to||h.status)+'</span>',
    improved:'<span class="badge better">\u2b06 '+esc(h.status_from||h.status)+' \u2192 '+esc(h.status_to||h.status)+'</span>',
    new:'<span class="badge new">\U0001f195 \u041d\u043e\u0432\u044b\u0439 ('+esc(h.status)+')</span>',
    removed:'<span class="badge removed">\u274c \u0423\u0434\u0430\u043b\u0451\u043d ('+esc(h.status_from||h.status)+')</span>',
  };
  return '<tr class="'+(kind==='worsened'?'row-fail':kind==='improved'?'row-ok':'')+'">' +
    '<td class="host">'+esc(h.shorthost)+'</td><td>'+(CHANGE_BADGE[kind]||'')+'</td>' +
    '<td class="os">'+esc(h.os_name||'')+'</td><td class="own">'+esc(h.owner||'')+'</td>' +
    '<td class="div">'+esc(h.division||'\u2014')+'</td><td class="reason">'+esc(h.reason_to||h.reason||'')+'</td></tr>';
}
function setDiffFilter(btn){
  _diffFilter=btn.dataset.diff;
  document.querySelectorAll('[data-diff]').forEach(b=>b.classList.toggle('active',b.dataset.diff===_diffFilter));
  renderDiff();
}
let _lastDataVersion=null;
async function startScan(){
  if(!confirm('Запустить полное сканирование CMDB?'))return;
  document.getElementById('scan-btn').disabled=true;
  try{await fetch('/api/scan/start',{method:'POST'});}catch(e){}
  pollScanStatus();
}
async function pollScanStatus(){
  let s;
  try{s=await(await fetch('/api/scan/status')).json();}catch(e){return;}
  if(_lastDataVersion===null)_lastDataVersion=s.data_version;
  const banner=document.getElementById('scan-banner');
  const btn=document.getElementById('scan-btn');
  const phase=document.getElementById('scan-phase');
  const pct=document.getElementById('scan-pct');
  const fill=document.getElementById('scan-fill');
  if(s.running){
    banner.style.display='block';banner.classList.remove('error');btn.disabled=true;
    phase.textContent=(s.phase_index?('['+s.phase_index+'/'+s.phase_total+'] '):'')+(s.phase||'Подготовка…')+(s.detail?(' — '+s.detail):'');
    pct.textContent=(s.percent||0)+'%';
    fill.style.width=(s.percent||0)+'%';
  }else{
    btn.disabled=false;
    if(s.error){
      banner.style.display='block';banner.classList.add('error');
      phase.textContent='Ошибка сканирования: '+s.error;
      pct.innerHTML='<button class="scan-retry" onclick="startScan()">Повторить</button>';
      fill.style.width='0%';
    }else if(s.data_version>_lastDataVersion){
      _lastDataVersion=s.data_version;
      banner.style.display='none';
      fetchStats();fetchDivisions();fetchData();
    }else{
      banner.style.display='none';
    }
  }
}
setInterval(pollScanStatus,1000);
pollScanStatus();
fetchStats();fetchDivisions();fetchResourceStatuses();fetchData();
</script>
</body>
</html>"""


if __name__ == "__main__":
    import sys
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    try:
        load_data(ScanProgress())
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}", file=sys.stderr)
        sys.exit(1)

    import socket
    port     = 5000
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"
    url = f"http://localhost:{port}"
    print(f"\nОткрываю браузер → {url}")
    print(f"Доступен в локальной сети → http://{local_ip}:{port}")
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    app.run(host="0.0.0.0", port=port, debug=False)
