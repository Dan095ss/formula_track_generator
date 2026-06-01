# Design: Flask CMDB OS Compliance Web App

**Date:** 2026-06-01  
**Status:** Approved

---

## Goal

Replace the static HTML report with a local Flask web app. Data loads from CMDB at startup, all filtering/pagination happens server-side via API calls from the browser.

---

## File Structure

```
vcenter_cmdb/
└── compliance_app/
    ├── cmdb_os_compliance.py   ← copied from vcenter_cmdb/ root (same file)
    ├── app.py                  ← NEW: Flask server (single file)
    └── requirements.txt        ← flask, requests, urllib3
```

`app.py` imports directly: `from cmdb_os_compliance import ...` — no sys.path tricks.

---

## Data Flow

```
python compliance_app/app.py
  → load_config([])              uses hardcoded URL/token defaults
  → CmdbClient.check_auth()
  → build_branch_maps(branches)
  → build_inventory(hosts, vms, bu, bn, bname)
  → build_report(inventory)     → _rows: list[ReportRow]  stored in memory
  → summarize(_rows)             → _summary: dict
  → extract unique divisions     → _divisions: list[str]
  → webbrowser.open("http://localhost:5000")
  → app.run(port=5000)
```

---

## API Routes

| Method | Path | Params | Response |
|---|---|---|---|
| GET | `/` | — | HTML page (inline string) |
| GET | `/api/stats` | — | `{total, OK, WARNING, NON_COMPLIANT, UNKNOWN}` |
| GET | `/api/divisions` | — | `{divisions: [...]}` |
| GET | `/api/data` | see below | `{data:[...], total, page, pages}` |
| GET | `/api/export` | same as /api/data | CSV attachment |

### `/api/data` + `/api/export` query params

| Param | Default | Description |
|---|---|---|
| `page` | 1 | Page number |
| `size` | 100 | Rows per page (max 500) |
| `status` | `` | Filter: OK / WARNING / NON_COMPLIANT / UNKNOWN |
| `family` | `` | Filter: windows_server / windows_client / linux / unknown |
| `division` | `` | Filter: exact match |
| `q` | `` | Text search: shorthost + os_name + owner + reason |
| `sort` | `` | Field name to sort by |
| `dir` | `asc` | asc / desc |

---

## Server-Side Filter Logic

```python
def _filter_rows(args) -> list[ReportRow]:
    rows = _rows
    if status := args.get("status"):  rows = [r for r in rows if r.status.value == status]
    if family := args.get("family"):   rows = [r for r in rows if r.family == family]
    if division := args.get("division"): rows = [r for r in rows if r.division == division]
    if q := args.get("q", "").lower():
        rows = [r for r in rows if q in (r.shorthost+r.os_name+r.owner+r.division+r.reason).lower()]
    return rows

def _sort_rows(rows, sort, dir_) -> list[ReportRow]:
    if not sort:
        return rows  # default: already sorted NON_COMPLIANT first from build_report
    return sorted(rows, key=lambda r: (getattr(r, sort, "") or "").lower(), reverse=(dir_=="desc"))
```

---

## Frontend (inline HTML in app.py)

Single-page app. No external CDN dependencies.

### Boot sequence
1. `fetch('/api/stats')` → populate 5 summary cards
2. `fetch('/api/divisions')` → populate division `<select>`
3. `fetchData()` → populate table (page 1)

### Filter controls (same as current HTML)
- Status toggle buttons (Все / Не соответствует / Условно / OK / Нет данных)
- OS Family buttons (Все / Windows Server / Windows Client / Linux / Неизвестно)
- Division `<select>` (populated from API)
- Text search `<input>`
- Page size `<select>` (50 / 100 / 200 / 500)
- "Скачать CSV" button → `window.location = '/api/export?' + params`

### Table
- Columns: Хост / ОС / Владелец / Дивизион / Тип КЕ / Семейство / Статус / Причина
- Sortable headers (click → ASC → DESC → reset)
- Row colors by status (same CSS as before)
- Pagination controls

### State
All filter state held in JS variables. Any change calls `fetchData(page=1)`. Pagination calls `fetchData(page=N)`.

---

## Startup UX

```
$ python compliance_app/app.py
Loading data from CMDB (this takes ~1-2 min)...
  branches: 8229 CIs loaded
  HOST: 32184 CIs loaded  
  VM:   4091 CIs loaded
Loaded 36275 KEs in 94s  |  NON_COMPLIANT: 15566  OK: 19946
Opening browser → http://localhost:5000
 * Running on http://127.0.0.1:5000
```

---

## Error Handling

- Auth error → print message + exit
- CMDB unreachable → print message + exit  
- `/api/data` errors → JSON `{error: "..."}` with HTTP 500

---

## Out of Scope

- Authentication on the Flask app itself (local only)
- Database / persistence
- WHERE query parser (text search covers it)
- Deployment (gunicorn, docker, etc.)
