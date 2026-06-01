"""CMDB OS Compliance — Flask web app.

Usage:
    cd compliance_app
    python app.py
"""
import csv
import io
import logging
import threading
import webbrowser

from flask import Flask, Response, jsonify, request

from cmdb_os_compliance import (
    CmdbClient,
    ReportRow,
    Status,
    build_branch_maps,
    build_inventory,
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


# ── Helpers ──────────────────────────────────────────────────

def _filter_rows(args: dict) -> list[ReportRow]:
    rows = _rows
    if status := args.get("status"):
        rows = [r for r in rows if r.status.value == status]
    if family := args.get("family"):
        rows = [r for r in rows if r.family == family]
    if division := args.get("division"):
        rows = [r for r in rows if r.division == division]
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
    }


# ── Data loading ─────────────────────────────────────────────

def load_data() -> None:
    global _rows, _summary, _divisions
    config = load_config([])
    client = CmdbClient(config)

    print("Connecting to CMDB…")
    client.check_auth()

    print("Loading branches…")
    branch_uuid = client.get_ci_type_uuid("branches")
    bu, bn, bname = build_branch_maps(client.iter_cis(branch_uuid))
    print(f"  {len(bu)} branches loaded")

    host_uuid = client.get_ci_type_uuid("HOST")
    vm_uuid   = client.get_ci_type_uuid("VM")

    print("Loading HOST and VM CIs…")
    inventory = build_inventory(
        client.iter_cis(host_uuid),
        client.iter_cis(vm_uuid),
        bu, bn, bname,
    )
    print(f"  {len(inventory)} unique KEs")

    _rows     = build_report(inventory)
    _summary  = summarize(_rows)
    _divisions = sorted({r.division for r in _rows if r.division})

    nc = _summary["NON_COMPLIANT"]
    ok = _summary["OK"]
    print(f"Done — {len(_rows)} KEs | NON_COMPLIANT: {nc} | OK: {ok}")


# ── Routes ───────────────────────────────────────────────────

@app.route("/")
def index() -> str:
    return _HTML


@app.route("/api/stats")
def api_stats():
    return jsonify(_summary)


@app.route("/api/divisions")
def api_divisions():
    return jsonify({"divisions": _divisions})


@app.route("/api/data")
def api_data():
    args  = request.args
    rows  = _filter_rows(args)
    rows  = _sort_rows(rows, args.get("sort", ""), args.get("dir", "asc"))
    total = len(rows)
    size  = min(int(args.get("size", 100)), 500)
    page  = max(int(args.get("page", 1)), 1)
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
                "ke_type", "family", "status", "reason"])
    for r in rows:
        w.writerow([r.shorthost, r.os_name, r.owner, r.division,
                    r.ke_type, r.family, r.status.value, r.reason])
    return Response(
        "﻿" + buf.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=os_compliance_filtered.csv"},
    )


# Placeholder — replaced in Task 4
_HTML = "<html><body><h1>CMDB OS Compliance</h1></body></html>"
