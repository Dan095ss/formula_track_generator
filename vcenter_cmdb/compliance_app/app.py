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
