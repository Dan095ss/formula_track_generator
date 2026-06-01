# Design: Historical Snapshots + Comparison + Trend Chart

**Date:** 2026-06-01  
**Status:** Approved

---

## Goal

Add historical snapshot storage, CSV import, diff comparison, and trend chart to the Flask CMDB OS Compliance app.

---

## Snapshot Format

`compliance_app/snapshots/YYYYMMDD_HHMMSS.json`

```json
{
  "id": "20260601_134700",
  "timestamp": "2026-06-01T13:47:00",
  "source": "cmdb",
  "summary": {"total": 36275, "OK": 19946, "WARNING": 763, "NON_COMPLIANT": 15566, "UNKNOWN": 0},
  "hosts": {
    "srv01": {
      "status": "OK", "os_name": "ubuntu 22.04 lts|...", "owner": "IT / Ivanov",
      "division": "04. дів. Урал", "family": "linux", "reason": "OK: Ubuntu 22.04 LTS"
    }
  }
}
```

`source`: `"cmdb"` for auto-saved, `"csv"` for imported.

---

## New Python Functions (app.py)

### `save_snapshot(rows, source="cmdb") -> str`
- Creates `compliance_app/snapshots/` if needed
- Serializes rows to JSON format above
- Returns snapshot id (e.g. `"20260601_134700"`)
- Called automatically at end of `load_data()`

### `list_snapshots() -> list[dict]`
- Reads all `snapshots/*.json`, returns `[{id, timestamp, source, summary}]` sorted newest-first
- Does NOT load `hosts` dict (too large)

### `load_snapshot(snap_id: str) -> dict`
- Reads `snapshots/{snap_id}.json`, returns full dict including `hosts`

### `import_csv_snapshot(csv_bytes: bytes, filename: str) -> str`
- Parses CSV (columns: shorthost, os_name, owner, division, ke_type, family, status, reason)
- Extracts date from filename if matches `*_YYYYMMDD*` pattern, else uses now
- Saves as snapshot with `source="csv"`
- Returns snapshot id

### `compare_snapshots(snap_a: dict, snap_b: dict) -> dict`
- snap_b is assumed newer
- Returns:
  ```json
  {
    "new":     [{"shorthost": ..., "status": ..., ...}],
    "removed": [{"shorthost": ..., "status_from": ..., ...}],
    "changed": [{"shorthost": ..., "status_from": "OK", "status_to": "NON_COMPLIANT", ...}]
  }
  ```
- `changed` only includes hosts where status actually changed
- Direction: `"improved"` if priority(to) > priority(from), else `"worsened"`
  - Priority: NON_COMPLIANT=0, WARNING=1, UNKNOWN=2, OK=3

---

## New API Routes

| Method | Route | Description |
|---|---|---|
| GET | `/api/snapshots` | List snapshots (no hosts data) |
| GET | `/api/trend` | All snapshots summary for chart |
| GET | `/api/compare?a=ID&b=ID` | Diff two snapshots |
| POST | `/api/snapshots/import` | Upload CSV file, create snapshot |

### `/api/snapshots` response
```json
[{"id": "20260601_134700", "timestamp": "2026-06-01T13:47", "source": "cmdb",
  "summary": {"total": 36275, "OK": 19946, ...}}, ...]
```

### `/api/trend` response
```json
{"snapshots": [{"id": "...", "timestamp": "...", "summary": {...}}, ...]}
```
(same as /api/snapshots — clients use this for chart)

### `/api/compare?a=ID&b=ID` response
```json
{
  "snap_a": {"id": "...", "timestamp": "...", "summary": {...}},
  "snap_b": {"id": "...", "timestamp": "...", "summary": {...}},
  "diff": {
    "new":     [...],
    "removed": [...],
    "changed": [{"shorthost": "srv01", "status_from": "OK", "status_to": "NON_COMPLIANT",
                 "direction": "worsened", "os_name": "...", "owner": "...", "division": "...",
                 "reason_to": "..."}]
  }
}
```

### `POST /api/snapshots/import` 
- multipart/form-data, field `file`
- Response: `{"id": "...", "timestamp": "...", "summary": {...}}`

---

## Frontend: New Tabs

### Tab bar (top, always visible)
```
[Таблица] [История] [Тренд] [Сравнение]
```

### История tab
- Table: дата | источник (CMDB/CSV) | всего | OK | WARNING | NON_COMPLIANT
- "Импорт CSV" button → file picker → POST /api/snapshots/import
- Each row: "Сравнить" button → pre-selects this snapshot in Сравнение tab

### Тренд tab
- SVG line chart: x=date, y=count, 3 lines (OK=green, WARNING=orange, NON_COMPLIANT=red)
- Shows last N snapshots (all if ≤20, else last 20)
- No external CDN — pure SVG + JS

### Сравнение tab
- Two `<select>` dropdowns: "Снимок A (старый)" and "Снимок B (новый)"
- Button "Сравнить"
- Results: summary cards (изменилось / ухудшилось / улучшилось / новых / удалённых)
- Filter buttons: Все | Ухудшились | Улучшились | Новые | Удалённые
- Table: хост / ОС / владелец / дивизион / было / стало

---

## `load_data()` update

After building `_rows`, call `save_snapshot(_rows, source="cmdb")`.
Also populate `_snapshots_cache = list_snapshots()` global for fast /api/snapshots response.

---

## Out of Scope

- Editing/deleting snapshots
- Automatic scheduled snapshots
- Alerts on status changes
