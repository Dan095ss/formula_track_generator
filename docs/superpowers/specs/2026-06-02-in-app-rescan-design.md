# In-App CMDB Rescan with Live Progress — Design

**Date:** 2026-06-02
**Epic:** CLAUDE-9jm
**Scope:** Feature 1 of 3 (rescan trigger + live progress). Features 2 (resource
status indicator) and 3 (on-demand nmap probe) are separate specs.

## Problem

`compliance_app/app.py` loads all CMDB data once at server startup via the
blocking `load_data()` call, then serves a read-only snapshot from in-memory
globals. To refresh the data the operator must restart the whole server. The app
is used by multiple people on the LAN, so a restart is disruptive and there is no
feedback while the (multi-minute) scan runs.

## Goal

Let any user trigger a fresh CMDB scan from the web UI. While a scan runs, every
connected client sees a global progress banner under the header (filling bar +
current-phase label). When the scan finishes, all clients automatically refresh
their data. Only one scan runs at a time.

## Non-Goals

- No authentication / per-user permissions (the app currently has none).
- No change to the CLI tool `cmdb_os_compliance.py:main()` behavior.
- No change to startup behavior: the server still does a blocking initial
  `load_data()` before opening the port (data is ready immediately on boot).
- No persistence of scan state across server restarts (in-memory only).

## Decisions (from brainstorming)

- **Progress UI:** a filling bar + text label of the current stage.
- **Multi-user:** scan state is global/server-side; the banner appears for *all*
  clients, not just the one who triggered it. Resolves concurrency: scan is a
  singleton, a second start is rejected.
- **Transport:** polling (Approach A). No SSE/WebSocket, no new dependencies.
- **Startup:** unchanged — blocking initial load. The rescan button is for
  refresh only.

## Architecture

### Server-side scan state (`app.py`)

A module-level singleton guarded by a lock:

```python
_scan_lock = threading.Lock()
_scan_state = {
    "running":     False,
    "phase":       "",      # human label, e.g. "Загрузка филиалов"
    "phase_index": 0,       # 1..7
    "phase_total": 7,
    "percent":     0,       # 0-100, weighted across phases
    "detail":      "",      # optional within-phase note, e.g. "страница 3/12"
    "started_at":  None,    # ISO timestamp
    "finished_at": None,    # ISO timestamp
    "error":       None,    # error message string if the scan failed
    "data_version": 0,      # increments on each successful completion
}
```

`data_version` is the signal clients use to know the served data changed and a
table refresh is needed.

### Progress reporter (`ScanProgress`)

A small class in `app.py` that owns the weighted phase plan and writes into
`_scan_state`. Weights (sum = 100):

| # | Phase                              | Weight |
|---|------------------------------------|--------|
| 1 | Авторизация                        | 2%     |
| 2 | Загрузка филиалов                  | 8%     |
| 3 | Карта host→branch (ref-скан)       | 35%    |
| 4 | Загрузка ACCOUNT                   | 10%    |
| 5 | Загрузка HOST                      | 20%    |
| 6 | Загрузка VM                        | 20%    |
| 7 | Сборка отчёта                      | 5%     |

API:

- `progress.phase(index, label)` — enter a phase; sets `phase`, `phase_index`,
  and base `percent` (sum of completed phase weights).
- `progress.tick(current, total)` — within a long phase, advance `percent`
  fractionally across the current phase's weight and set `detail` text.

`ScanProgress` is constructed per scan. For the synchronous startup load it is
also used (harmless — nobody is polling yet) so that `data_version` becomes 1
after boot.

### Instrumenting the long phases

To keep the bar moving inside multi-page phases, add an **optional** progress
callback parameter (default `None`) to:

- `CmdbClient.iter_cis(ci_type_uuid, on_page=None)` — calls
  `on_page(page, total_pages)` after each page.
- `CmdbClient.iter_refs(ref_type_uuid, on_page=None)` — same.
- `CmdbClient.build_host_branch_map(branches_by_uuid, on_progress=None)` —
  reports ref-type scan progress.

Because the parameters are optional with `None` default, `cmdb_os_compliance.py:main()`
and existing callers are unaffected.

`load_data()` is refactored to accept a `progress: ScanProgress` argument and
wire the callbacks into the HOST/VM/host_branch_map phases. Its existing `print()`
status lines are replaced by `progress.phase(...)` calls.

### Background runner

```python
def _run_scan() -> None:
    progress = ScanProgress()
    try:
        load_data(progress)            # mutates _rows/_summary/_divisions + saves snapshot
        with _scan_lock:
            _scan_state["data_version"] += 1
            _scan_state["error"] = None
    except Exception as e:
        with _scan_lock:
            _scan_state["error"] = str(e)
        log.exception("Scan failed")
    finally:
        with _scan_lock:
            _scan_state["running"]     = False
            _scan_state["finished_at"] = datetime.now().isoformat(timespec="seconds")
```

### Endpoints

- `POST /api/scan/start`
  - Under `_scan_lock`: if `_scan_state["running"]` → return **409**
    `{"error": "Сканирование уже выполняется"}`.
  - Else set `running=True`, reset `phase/percent/error/finished_at`, set
    `started_at`, spawn `threading.Thread(target=_run_scan, daemon=True)`,
    return **202** `{"started": True}`.
- `GET /api/scan/status` → JSON snapshot of `_scan_state` (copy under lock).

### Frontend (the `_HTML` string in `app.py`)

- **Scan button** `🔄 Сканировать` placed under the header. Click shows a
  lightweight `confirm()` ("Запустить полное сканирование CMDB?") because the
  scan is heavy and shared, then `POST /api/scan/start`. A 409 response is
  ignored (someone else already started; the banner will show it anyway).
- **Global banner** under the header, hidden by default. While `running`:
  visible on every tab, showing the phase label, a CSS-width progress bar driven
  by `percent`, and the percentage. On `error`: red banner with the message and
  a "Повторить" button.
- **Polling loop:** `setInterval(pollScanStatus, 1000)`, started on page load and
  always running (lightweight on a LAN).
  - `running` → render/refresh banner, disable scan button.
  - Track `lastDataVersion`. When `status.data_version > lastDataVersion` and not
    running → hide banner, update `lastDataVersion`, re-run
    `fetchStats(); fetchDivisions(); fetchData();` to pull the new data. (Divisions
    refresh must avoid duplicating existing `<option>`s — clear and rebuild.)
  - `error` → show red banner, re-enable button.

## Error Handling

| Situation                        | Behavior                                              |
|----------------------------------|-------------------------------------------------------|
| Scan fails (auth/network)        | `error` set; red banner + Повторить; old data stays.  |
| Start while a scan is running    | 409; no-op; banner already reflects the running scan. |
| Client opens mid-scan            | First poll shows the running banner immediately.      |
| Server restart during scan       | State is in-memory; restart does a fresh blocking load.|

## Testing

Mirror `test_app.py` (pytest + `monkeypatch` + Flask `test_client`):

- `_run_scan` transitions: stub `load_data` to a no-op; assert `running` goes
  True→False, `data_version` increments, `error` stays `None`.
- `_run_scan` failure: stub `load_data` to raise; assert `error` is set,
  `running` False, `data_version` unchanged.
- `POST /api/scan/start` returns 202 and flips `running`; a second immediate call
  returns 409.
- `GET /api/scan/status` returns the current state shape.
- `ScanProgress` math: after `phase(3, ...)` base percent == sum of weights 1–2;
  `tick(1, 2)` advances halfway into phase 3's weight.

Frontend (banner, polling, bar fill) is verified manually in the browser — no JS
test harness exists in this project.

## Files Touched

- `compliance_app/app.py` — scan state, `ScanProgress`, `_run_scan`, two
  endpoints, `load_data(progress)` refactor, `_HTML` button/banner/polling JS,
  startup call passes a `ScanProgress`.
- `compliance_app/cmdb_os_compliance.py` — optional `on_page`/`on_progress`
  callbacks on `iter_cis`, `iter_refs`, `build_host_branch_map`.
- `compliance_app/test_app.py` — new tests for scan endpoints and `ScanProgress`.
