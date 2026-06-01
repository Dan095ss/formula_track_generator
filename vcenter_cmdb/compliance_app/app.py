"""CMDB OS Compliance — Flask web app.

Usage:
    cd compliance_app
    python app.py
"""
import csv
import io
import json
import logging
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

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
                "ke_type", "family", "status", "reason"])
    for r in rows:
        w.writerow([r.shorthost, r.os_name, r.owner, r.division,
                    r.ke_type, r.family, r.status.value, r.reason])
    return Response(
        "﻿" + buf.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=os_compliance_filtered.csv"},
    )


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
            color: #fff; border-radius: 12px; padding: 28px 32px; margin-bottom: 24px; }
  .header h1 { font-size: 22px; font-weight: 700; }
  .header .meta { margin-top: 6px; font-size: 13px; opacity: .7; }

  .cards { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
  .card { flex: 1; min-width: 140px; background: #fff; border-radius: 10px;
          padding: 18px 20px; box-shadow: 0 1px 4px rgba(0,0,0,.08); cursor: pointer;
          transition: box-shadow .15s; }
  .card:hover { box-shadow: 0 4px 12px rgba(0,0,0,.15); }
  .card .num { font-size: 32px; font-weight: 700; line-height: 1; }
  .card .lbl { font-size: 12px; color: #666; margin-top: 4px; text-transform: uppercase; letter-spacing: .6px; }
  .card.total .num { color: #1a1a2e; }
  .card.ok    .num { color: #16a34a; }
  .card.warn  .num { color: #d97706; }
  .card.fail  .num { color: #dc2626; }
  .card.unk   .num { color: #6b7280; }

  .filterbar { background: #fff; border-radius: 10px; padding: 14px 20px;
               margin-bottom: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
  .filter-row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 8px; }
  .filter-row:last-child { margin-bottom: 0; }
  .filter-label { font-size: 11px; font-weight: 600; color: #6b7280;
                  text-transform: uppercase; letter-spacing: .5px; white-space: nowrap; min-width: 60px; }
  .filter-btn { padding: 7px 14px; border: 1px solid #d1d5db; border-radius: 6px;
                background: #fff; cursor: pointer; font-size: 13px; font-weight: 500;
                transition: all .15s; white-space: nowrap; }
  .filter-btn:hover { background: #f3f4f6; }
  .filter-btn.active { background: #0f3460; color: #fff; border-color: #0f3460; }
  .filter-btn.fam-ws.active  { background: #7c3aed; border-color: #7c3aed; }
  .filter-btn.fam-wc.active  { background: #2563eb; border-color: #2563eb; }
  .filter-btn.fam-lx.active  { background: #059669; border-color: #059669; }
  .filter-btn.fam-unk.active { background: #6b7280; border-color: #6b7280; }
  .sel { padding: 7px 10px; border: 1px solid #d1d5db; border-radius: 6px;
         font-size: 13px; cursor: pointer; background: #fff; max-width: 300px; }
  .filterbar input[type=text] { flex: 1; min-width: 200px; padding: 8px 12px;
                                  border: 1px solid #d1d5db; border-radius: 6px;
                                  font-size: 14px; outline: none; }
  .filterbar input[type=text]:focus { border-color: #0f3460; box-shadow: 0 0 0 3px rgba(15,52,96,.12); }
  .export-btn { padding: 7px 16px; border: 1px solid #0f3460; border-radius: 6px;
                background: #0f3460; color: #fff; cursor: pointer; font-size: 13px;
                font-weight: 500; white-space: nowrap; transition: background .15s; }
  .export-btn:hover { background: #16213e; }

  .table-wrap { background: #fff; border-radius: 10px; overflow: hidden;
                box-shadow: 0 1px 4px rgba(0,0,0,.08); }
  table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
  thead th { background: #1a1a2e; color: #fff; padding: 12px 14px; text-align: left;
             font-weight: 600; font-size: 12px; letter-spacing: .5px;
             text-transform: uppercase; white-space: nowrap; cursor: pointer; user-select: none; }
  thead th:hover { background: #16213e; }
  thead th.sort-asc::after  { content: ' ▲'; }
  thead th.sort-desc::after { content: ' ▼'; }
  tbody tr { border-bottom: 1px solid #f0f0f0; transition: background .1s; }
  tbody tr:last-child { border-bottom: none; }
  td { padding: 10px 14px; vertical-align: top; }
  td.host { font-family: 'Consolas', monospace; font-size: 13px; font-weight: 600; color: #0f3460; }
  td.os   { color: #374151; }
  td.own  { color: #4b5563; font-size: 13px; }
  td.div  { color: #6b7280; font-size: 12px; }
  td.ke   { font-size: 12px; color: #6b7280; white-space: nowrap; }
  td.fam  { font-size: 11px; color: #9ca3af; white-space: nowrap; }
  td.reason { font-size: 12px; color: #6b7280; }
  .row-fail    { background: #fff5f5; } .row-fail:hover    { background: #fee2e2; }
  .row-warning { background: #fffbeb; } .row-warning:hover { background: #fef3c7; }
  .row-ok      { background: #f0fdf4; } .row-ok:hover      { background: #dcfce7; }
  .row-unknown { background: #f9fafb; } .row-unknown:hover { background: #f3f4f6; }
  .badge { display: inline-block; padding: 3px 10px; border-radius: 12px;
           font-size: 11px; font-weight: 700; letter-spacing: .4px; white-space: nowrap; }
  .badge.ok      { background: #dcfce7; color: #15803d; }
  .badge.warning { background: #fef3c7; color: #b45309; }
  .badge.fail    { background: #fee2e2; color: #b91c1c; }
  .badge.unknown { background: #f3f4f6; color: #6b7280; }

  .pagination { display: flex; align-items: center; justify-content: space-between;
                padding: 14px 20px; border-top: 1px solid #f0f0f0;
                flex-wrap: wrap; gap: 10px; }
  .pag-info { font-size: 13px; color: #6b7280; }
  .pag-controls { display: flex; gap: 4px; align-items: center; flex-wrap: wrap; }
  .pag-btn { min-width: 34px; height: 34px; padding: 0 10px; border: 1px solid #d1d5db;
             border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px;
             display: flex; align-items: center; justify-content: center; transition: all .15s; }
  .pag-btn:hover:not(:disabled) { background: #f3f4f6; }
  .pag-btn.active { background: #0f3460; color: #fff; border-color: #0f3460; font-weight: 700; }
  .pag-btn:disabled { opacity: .4; cursor: default; }
  .pag-ellipsis { padding: 0 6px; color: #9ca3af; font-size: 14px; }

  .loading { padding: 60px; text-align: center; color: #9ca3af; font-size: 14px; }
  .empty   { padding: 40px; text-align: center; color: #9ca3af; font-size: 14px; }
  .footer  { text-align: center; margin-top: 20px; font-size: 12px; color: #9ca3af; }
</style>
</head>
<body>
<div class="page">

  <div class="header">
    <h1>Отчёт соответствия ОС корпоративному регламенту</h1>
    <div class="meta" id="meta">Загрузка данных…</div>
  </div>

  <div class="cards">
    <div class="card total" onclick="setStatus('')">
      <div class="num" id="cnt-total">…</div><div class="lbl">Всего</div></div>
    <div class="card ok"   onclick="setStatus('OK')">
      <div class="num" id="cnt-ok">…</div><div class="lbl">Соответствует</div></div>
    <div class="card warn" onclick="setStatus('WARNING')">
      <div class="num" id="cnt-warn">…</div><div class="lbl">Условно допустимо</div></div>
    <div class="card fail" onclick="setStatus('NON_COMPLIANT')">
      <div class="num" id="cnt-fail">…</div><div class="lbl">Не соответствует</div></div>
    <div class="card unk"  onclick="setStatus('UNKNOWN')">
      <div class="num" id="cnt-unk">…</div><div class="lbl">Нет данных об ОС</div></div>
  </div>

  <div class="filterbar">
    <div class="filter-row">
      <span class="filter-label">Статус</span>
      <button class="filter-btn active" data-status="" onclick="setStatus('')">Все</button>
      <button class="filter-btn" data-status="NON_COMPLIANT" onclick="setStatus('NON_COMPLIANT')">Не соответствует</button>
      <button class="filter-btn" data-status="WARNING" onclick="setStatus('WARNING')">Условно</button>
      <button class="filter-btn" data-status="OK" onclick="setStatus('OK')">OK</button>
      <button class="filter-btn" data-status="UNKNOWN" onclick="setStatus('UNKNOWN')">Нет данных</button>
    </div>
    <div class="filter-row">
      <span class="filter-label">ОС</span>
      <button class="filter-btn active" data-fam="" onclick="setFamily('')">Все</button>
      <button class="filter-btn fam-ws" data-fam="windows_server" onclick="setFamily('windows_server')">Windows Server</button>
      <button class="filter-btn fam-wc" data-fam="windows_client" onclick="setFamily('windows_client')">Windows Client</button>
      <button class="filter-btn fam-lx" data-fam="linux" onclick="setFamily('linux')">Linux</button>
      <button class="filter-btn fam-unk" data-fam="unknown" onclick="setFamily('unknown')">Неизвестно</button>
    </div>
    <div class="filter-row">
      <span class="filter-label">Дивизион</span>
      <select class="sel" id="div-sel" onchange="setDivision(this.value)">
        <option value="">Все дивизионы</option>
      </select>
      <select class="sel" onchange="changeSize(this.value)" style="margin-left:auto">
        <option value="50">50 / стр.</option>
        <option value="100" selected>100 / стр.</option>
        <option value="200">200 / стр.</option>
        <option value="500">500 / стр.</option>
      </select>
    </div>
    <div class="filter-row">
      <span class="filter-label">Поиск</span>
      <input type="text" id="search" placeholder="Поиск по хосту, ОС, владельцу…"
             oninput="debounceSearch(this.value)">
      <button class="export-btn" onclick="exportCSV()">&#11015; Скачать CSV</button>
    </div>
  </div>

  <div class="table-wrap">
    <table>
      <thead id="thead"></thead>
      <tbody id="tbody"><tr><td class="loading" colspan="8">Загрузка данных из CMDB…</td></tr></tbody>
    </table>
    <div class="pagination">
      <div class="pag-info" id="pag-info"></div>
      <div class="pag-controls" id="pag-controls"></div>
    </div>
  </div>

  <div class="footer">Регламент допустимых ОС от 13.05.2026 &nbsp;·&nbsp; CMDB OS Compliance</div>
</div>

<script>
const COLS = [
  {f:'shorthost', label:'Хост',     cls:'host'},
  {f:'os_name',   label:'ОС',       cls:'os'},
  {f:'owner',     label:'Владелец', cls:'own'},
  {f:'division',  label:'Дивизион', cls:'div'},
  {f:'ke_type',   label:'Тип КЕ',  cls:'ke'},
  {f:'family',    label:'Семейство',cls:'fam'},
  {f:'status',    label:'Статус',   cls:''},
  {f:'reason',    label:'Причина',  cls:'reason'},
];
const ROW_CLASS = {
  OK: 'row-ok', WARNING: 'row-warning',
  NON_COMPLIANT: 'row-fail', UNKNOWN: 'row-unknown'
};
const BADGE = {
  OK:            '<span class="badge ok">OK</span>',
  WARNING:       '<span class="badge warning">WARNING</span>',
  NON_COMPLIANT: '<span class="badge fail">NON_COMPLIANT</span>',
  UNKNOWN:       '<span class="badge unknown">UNKNOWN</span>',
};
const FAM = {
  windows_server: 'Win Server', windows_client: 'Win Client',
  linux: 'Linux', unknown: '—'
};

let state = { page:1, size:100, status:'', family:'', division:'', q:'', sort:'', dir:'asc' };
let _searchTimer = null;

function esc(s) {
  return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

async function fetchStats() {
  const d = await (await fetch('/api/stats')).json();
  document.getElementById('cnt-total').textContent = d.total;
  document.getElementById('cnt-ok').textContent    = d.OK;
  document.getElementById('cnt-warn').textContent  = d.WARNING;
  document.getElementById('cnt-fail').textContent  = d.NON_COMPLIANT;
  document.getElementById('cnt-unk').textContent   = d.UNKNOWN;
  document.getElementById('meta').textContent =
    'Всего КЕ: ' + d.total + '  |  Не соответствует: ' + d.NON_COMPLIANT + '  |  OK: ' + d.OK;
}

async function fetchDivisions() {
  const d = await (await fetch('/api/divisions')).json();
  const sel = document.getElementById('div-sel');
  d.divisions.forEach(v => {
    const o = document.createElement('option');
    o.value = v; o.textContent = v; sel.appendChild(o);
  });
}

async function fetchData() {
  const p = new URLSearchParams({ page: state.page, size: state.size });
  if (state.status)   p.set('status',   state.status);
  if (state.family)   p.set('family',   state.family);
  if (state.division) p.set('division', state.division);
  if (state.q)        p.set('q',        state.q);
  if (state.sort)     { p.set('sort', state.sort); p.set('dir', state.dir); }

  document.getElementById('tbody').innerHTML =
    '<tr><td class="loading" colspan="8">Загрузка…</td></tr>';
  const d = await (await fetch('/api/data?' + p)).json();
  renderHeaders();
  renderRows(d.data);
  renderPagination(d.total, d.page, d.pages);
}

function renderHeaders() {
  document.getElementById('thead').innerHTML = '<tr>' +
    COLS.map(c => {
      const cls = state.sort === c.f
        ? (state.dir === 'asc' ? ' class="sort-asc"' : ' class="sort-desc"')
        : '';
      return '<th' + cls + ' onclick="toggleSort(\'' + c.f + '\')">' + c.label + '</th>';
    }).join('') + '</tr>';
}

function renderRows(rows) {
  const tbody = document.getElementById('tbody');
  if (!rows.length) {
    tbody.innerHTML = '<tr><td class="empty" colspan="8">Ничего не найдено</td></tr>';
    return;
  }
  tbody.innerHTML = rows.map(r =>
    '<tr class="' + (ROW_CLASS[r.status] || '') + '">' +
    '<td class="host">'   + esc(r.shorthost)           + '</td>' +
    '<td class="os">'     + esc(r.os_name)             + '</td>' +
    '<td class="own">'    + esc(r.owner)               + '</td>' +
    '<td class="div">'    + esc(r.division || '—')     + '</td>' +
    '<td class="ke">'     + esc(r.ke_type)             + '</td>' +
    '<td class="fam">'    + esc(FAM[r.family] || r.family) + '</td>' +
    '<td>'                + (BADGE[r.status] || esc(r.status)) + '</td>' +
    '<td class="reason">' + esc(r.reason)              + '</td>' +
    '</tr>'
  ).join('');
}

function renderPagination(total, page, pages) {
  const start = total ? (page - 1) * state.size + 1 : 0;
  const end   = Math.min(page * state.size, total);
  document.getElementById('pag-info').textContent =
    'Показано ' + start + '–' + end + ' из ' + total;

  let html = '';
  html += '<button class="pag-btn" onclick="goTo(1)" ' + (page===1?'disabled':'') + '>&laquo;</button>';
  html += '<button class="pag-btn" onclick="goTo(' + (page-1) + ')" ' + (page===1?'disabled':'') + '>&lsaquo;</button>';
  for (let p = 1; p <= pages; p++) {
    if (p === 1 || p === pages || Math.abs(p - page) <= 2)
      html += '<button class="pag-btn' + (p===page?' active':'') + '" onclick="goTo(' + p + ')">' + p + '</button>';
    else if (Math.abs(p - page) === 3)
      html += '<span class="pag-ellipsis">…</span>';
  }
  html += '<button class="pag-btn" onclick="goTo(' + (page+1) + ')" ' + (page===pages?'disabled':'') + '>&rsaquo;</button>';
  html += '<button class="pag-btn" onclick="goTo(' + pages + ')" ' + (page===pages?'disabled':'') + '>&raquo;</button>';
  document.getElementById('pag-controls').innerHTML = html;
}

function goTo(p) {
  state.page = p;
  fetchData();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function changeSize(v) { state.size = +v; state.page = 1; fetchData(); }

function setStatus(v) {
  state.status = v; state.page = 1;
  document.querySelectorAll('[data-status]').forEach(b =>
    b.classList.toggle('active', b.dataset.status === v));
  fetchData();
}

function setFamily(v) {
  state.family = v; state.page = 1;
  document.querySelectorAll('[data-fam]').forEach(b =>
    b.classList.toggle('active', b.dataset.fam === v));
  fetchData();
}

function setDivision(v) { state.division = v; state.page = 1; fetchData(); }

function debounceSearch(v) {
  clearTimeout(_searchTimer);
  _searchTimer = setTimeout(() => { state.q = v; state.page = 1; fetchData(); }, 300);
}

function toggleSort(field) {
  if (state.sort === field) {
    if (state.dir === 'asc') { state.dir = 'desc'; }
    else { state.sort = ''; state.dir = 'asc'; }
  } else {
    state.sort = field; state.dir = 'asc';
  }
  state.page = 1;
  fetchData();
}

function exportCSV() {
  const p = new URLSearchParams();
  if (state.status)   p.set('status',   state.status);
  if (state.family)   p.set('family',   state.family);
  if (state.division) p.set('division', state.division);
  if (state.q)        p.set('q',        state.q);
  if (state.sort)     { p.set('sort', state.sort); p.set('dir', state.dir); }
  window.location = '/api/export?' + p;
}

// Boot
fetchStats();
fetchDivisions();
fetchData();
</script>
</body>
</html>"""


if __name__ == "__main__":
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    try:
        load_data()
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}", file=sys.stderr)
        sys.exit(1)

    port = 5000
    url  = f"http://localhost:{port}"
    print(f"\nОткрываю браузер → {url}")
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=port, debug=False)
