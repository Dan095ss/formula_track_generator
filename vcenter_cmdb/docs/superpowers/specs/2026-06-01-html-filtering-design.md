# Design: Enhanced HTML Filtering for cmdb_os_compliance.py

**Date:** 2026-06-01  
**Status:** Approved  
**Scope:** `vcenter_cmdb/cmdb_os_compliance.py` — single file, no new files

---

## Problem

The current HTML report has only basic search + status filter. Missing:
- Division (дивизион) context — who owns what
- OS Family grouping
- Column sorting
- Export of filtered subset
- Advanced ad-hoc queries

---

## Solution

Enhance `cmdb_os_compliance.py` to:
1. Pre-load `branches` CIs and resolve division (`ter_lvl_2`) per host
2. Add `division` and `family` to `ReportRow`
3. Rewrite the HTML template with rich interactive filters

---

## Division Resolution Logic

### Primary — via CI relationship (ref)

Every HOST/VM CI may have an `Attr` whose `attr.ref.uuid` points to a `branches` CI.  
We build `branches_by_uuid: {branch_ci_uuid → ter_lvl_2}` upfront.  
When processing a CI, scan all its `attrs` for any `attr.ref` whose `uuid` is in `branches_by_uuid`.

### Fallback — hostname number lookup

If no ref found, extract the numeric branch code from `shorthost` with:
```
re.search(r'(?i)^[a-z]+-?(\d+)', shorthost)
```
Examples: `vl1212-kassa` → `1212`, `u1651-sklad3` → `1651`, `YUG-7760-Admin` → `7760`

Look up result in `branches_by_number: {number_str → ter_lvl_2}`.

### No match → `division = ""`

---

## Data Model Changes

### `HostRecord`
```python
@dataclass
class HostRecord:
    shorthost: str
    os_name: str | None
    owner: str | None
    division: str | None      # NEW: ter_lvl_2 from branches
    sources: set[str]
```

### `ReportRow`
```python
@dataclass
class ReportRow:
    shorthost: str
    os_name: str
    owner: str
    division: str             # NEW
    ke_type: str
    family: str               # NEW: windows_server|windows_client|linux|unknown
    status: Status
    reason: str
```

### `extract_attrs()` — no change needed
The `ref` field is already present on `Attr` objects in the API response.  
Add `ref_uuid_of(ci)` helper that returns set of ref UUIDs from all attrs.

---

## New Python Functions

| Function | Purpose |
|---|---|
| `ref_uuids_of(ci)` | Returns `set[str]` of all `attr.ref.uuid` values for a CI |
| `branch_number_from_host(shorthost)` | Regex extraction of numeric code |
| `resolve_division(ci, branches_by_uuid, branches_by_number)` | Primary + fallback logic |
| `build_branch_maps(branch_cis)` | Builds both lookup dicts from branches CI list |

## Modified Functions

| Function | Change |
|---|---|
| `build_inventory()` | Accepts `branches_by_uuid`, `branches_by_number`; sets `HostRecord.division` |
| `build_report()` | Passes `family` from `ClassificationResult`; passes `division` from `HostRecord` |
| `main()` | Fetches branches CIs before building inventory |
| `write_html()` | Uses new template (see below) |

---

## HTML Template — New Features

### Filters panel
| Filter | Type | Field |
|---|---|---|
| Status | Toggle buttons (existing) | `status` |
| OS Family | Toggle buttons | `family` |
| Division | `<select>` dropdown | `division` |
| Owner | `<select>` dropdown | `owner` |
| Text search | `<input>` (existing) | all fields |
| WHERE query | `<input>` advanced | any field |

### Column sorting
Click any `<th>` → cycle: unsorted → ASC → DESC.  
Active sort shown with ▲/▼ indicator.

### Export filtered CSV
Button "Скачать CSV" → generates CSV from `filtered[]` array in JS → triggers download via Blob URL.  
Respects all active filters.

### WHERE query syntax (built-in JS, no libraries)
```
field = "value"
field != "value"
field LIKE "prefix%"
expr AND expr
expr OR expr
NOT expr
```
Fields: `shorthost`, `os_name`, `owner`, `division`, `ke_type`, `status`, `reason`, `family`  
Error shown inline if parse fails. Falls back to no-op (show all).

### New `division` column
Shown between `owner` and `ke_type`. Empty string shown as `—`.

---

## Performance Notes

- `branches` CIs: ~8229 records (seen in screenshot) — one paginated fetch at startup
- No per-CI graph calls — O(1) lookup via pre-built dicts
- `ref_uuids_of()` scans existing `attrs` array — no extra API call

---

## Backward Compatibility

- All existing CLI args unchanged
- CSV gains two new columns: `division`, `family` (appended, existing columns unchanged)
- HTML is fully self-contained (no CDN, no external JS)

---

## Out of Scope

- AD lookup for division (future)
- Flask migration (future — classification and reporting logic already decoupled)
- Server-side cmdbQL filtering at fetch time
