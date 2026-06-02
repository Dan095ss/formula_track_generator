# In-App CMDB Rescan with Live Progress — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let any user trigger a fresh CMDB scan from the web UI and show a global, live progress banner (filling bar + phase label) to every connected client, auto-refreshing data when the scan finishes.

**Architecture:** A module-level singleton `_scan_state` dict (guarded by `_scan_lock`) holds scan progress. A `ScanProgress` reporter writes weighted phase progress into it. `load_data()` is refactored to take a `ScanProgress` and wire optional progress callbacks into the slow CMDB-client methods. Two endpoints (`POST /api/scan/start`, `GET /api/scan/status`) drive a 1-second browser poll that renders the banner and reloads data on `data_version` change. Server startup stays blocking; the CLI tool is untouched.

**Tech Stack:** Python 3.12, Flask, threading, `requests`; vanilla JS/CSS in the `_HTML` string; pytest + Flask `test_client` for tests.

**Spec:** `docs/superpowers/specs/2026-06-02-in-app-rescan-design.md`

---

## File Structure

- `compliance_app/cmdb_os_compliance.py` — add optional progress callbacks to
  `iter_cis`, `iter_refs`, `build_host_branch_map` (CLI behavior unchanged).
- `compliance_app/app.py` — `_scan_state`/`_scan_lock`/`_SCAN_PHASES`,
  `ScanProgress`, `load_data(progress)` refactor, `_run_scan`, two endpoints,
  `_HTML` scan button + banner + polling JS, startup passes a `ScanProgress`.
- `compliance_app/test_app.py` — tests for callbacks, `ScanProgress`,
  `_run_scan`, endpoints, and an index-HTML smoke check.

All commands run from `C:/Users/Sevryuk.DA/Documents/CLAUDE/vcenter_cmdb/compliance_app`.

---

## Task 1: Optional progress callbacks in the CMDB client

**Files:**
- Modify: `compliance_app/cmdb_os_compliance.py` (`iter_cis`, `iter_refs`, `build_host_branch_map`)
- Test: `compliance_app/test_app.py`

- [ ] **Step 1: Write the failing test**

Add to `test_app.py`:

```python
# ============================================================
# CMDB client progress callbacks
# ============================================================
from cmdb_os_compliance import CmdbClient, Config


class _FakeResp:
    def __init__(self, payload, status=200):
        self._payload, self.status_code, self.text = payload, status, ""
    def json(self):
        return self._payload


class _FakeSession:
    def __init__(self, pages):
        self._pages = pages
        self.headers = {}
        self.verify = False
    def get(self, url, params=None, timeout=None):
        return _FakeResp(self._pages[params["page"] - 1])


def _client():
    c = CmdbClient(Config(cmdb_url="http://x", token="t"))
    return c


def test_iter_cis_invokes_on_page_each_page():
    c = _client()
    c._session = _FakeSession([
        {"total_pages": 2, "total_items": 3, "page_data": [{"a": 1}]},
        {"total_pages": 2, "total_items": 3, "page_data": [{"b": 2}]},
    ])
    seen = []
    items = list(c.iter_cis("uuid", on_page=lambda p, t: seen.append((p, t))))
    assert len(items) == 2
    assert seen == [(1, 2), (2, 2)]


def test_iter_cis_without_callback_still_works():
    c = _client()
    c._session = _FakeSession([{"total_pages": 1, "total_items": 1, "page_data": [{"a": 1}]}])
    assert list(c.iter_cis("uuid")) == [{"a": 1}]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest test_app.py::test_iter_cis_invokes_on_page_each_page -v`
Expected: FAIL — `iter_cis() got an unexpected keyword argument 'on_page'`

- [ ] **Step 3: Add the callback parameters**

In `cmdb_os_compliance.py`, change `iter_cis` signature and add the callback call after each page:

```python
    def iter_cis(self, ci_type_uuid: str, on_page=None) -> Iterator[dict]:
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
            if on_page:
                on_page(page, total_pages)
            log.debug("Fetched page %d/%d", page, total_pages)
            if page >= total_pages:
                break
            page += 1
```

Change `iter_refs` the same way (add `on_page=None`, call `on_page(page, total_pages)` after `yield from`):

```python
    def iter_refs(self, ref_type_uuid: str, on_page=None) -> Iterator[dict]:
        page = 1
        total_pages = None
        while True:
            resp = self._session.get(
                f"{self._base}/ref/full/",
                params={"type": ref_type_uuid, "page": page, "size": self._cfg.page_size},
                timeout=self._cfg.timeout,
            )
            if resp.status_code != 200:
                raise CmdbHTTPError(resp.status_code, resp.text)
            body = resp.json()
            if total_pages is None:
                total_pages = body.get("total_pages", 1)
                log.info("Ref type %s: %d refs, %d pages",
                         ref_type_uuid, body.get("total_items", "?"), total_pages)
            yield from body.get("page_data", [])
            if on_page:
                on_page(page, total_pages)
            if page >= total_pages:
                break
            page += 1
```

Add `on_progress=None` to `build_host_branch_map` and report per ref-type scanned. Change the method signature line and the `for rt in ref_types:` loop to enumerate and report:

```python
    def build_host_branch_map(
        self, branches_by_uuid: dict[str, str], on_progress=None
    ) -> dict[str, str]:
```

Then replace `for rt in ref_types:` with:

```python
        total_rt = len(ref_types)
        for i, rt in enumerate(ref_types, 1):
```

and immediately before that loop's closing (after the existing trailing comment `# keep scanning — multiple ref types might connect hosts to branches`) add:

```python
            if on_progress:
                on_progress(i, total_rt)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest test_app.py -k "iter_cis" -v`
Expected: PASS (both tests)

- [ ] **Step 5: Run the full suite to confirm no regressions**

Run: `python -m pytest test_app.py -v`
Expected: all existing tests still PASS

- [ ] **Step 6: Commit**

```bash
git add vcenter_cmdb/compliance_app/cmdb_os_compliance.py vcenter_cmdb/compliance_app/test_app.py
git commit -m "feat: optional progress callbacks in CMDB client (CLAUDE-9jm)"
```

---

## Task 2: `ScanProgress` reporter + scan state

**Files:**
- Modify: `compliance_app/app.py` (add `_scan_lock`, `_scan_state`, `_SCAN_PHASES`, `ScanProgress` after the in-memory store block, ~line 37)
- Test: `compliance_app/test_app.py`

- [ ] **Step 1: Write the failing test**

Add to `test_app.py`:

```python
# ============================================================
# ScanProgress
# ============================================================
import copy


@pytest.fixture
def reset_scan_state():
    saved = copy.deepcopy(app_module._scan_state)
    yield
    app_module._scan_state.clear()
    app_module._scan_state.update(saved)


def test_scan_progress_phase_sets_base_percent(reset_scan_state):
    p = app_module.ScanProgress()
    p.phase(3)  # weights 1-2 are 2 + 8 = 10
    assert app_module._scan_state["percent"] == 10
    assert app_module._scan_state["phase_index"] == 3
    assert app_module._scan_state["phase_total"] == 7
    assert app_module._scan_state["phase"]  # non-empty label


def test_scan_progress_tick_advances_within_phase(reset_scan_state):
    p = app_module.ScanProgress()
    p.phase(3)            # base 10, phase weight 35
    p.tick(1, 2)          # halfway: 10 + 35*0.5 = 27.5 -> 27
    assert app_module._scan_state["percent"] == 27
    assert "1/2" in app_module._scan_state["detail"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest test_app.py::test_scan_progress_phase_sets_base_percent -v`
Expected: FAIL — `module 'app' has no attribute 'ScanProgress'`

- [ ] **Step 3: Implement scan state and `ScanProgress`**

In `app.py`, right after the in-memory store block (after the `_divisions: list[str] = []` line, ~line 37), add:

```python
import threading

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
    ("Загрузка HOST", 20),
    ("Загрузка VM", 20),
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
            _scan_state["detail"] = f"страница {current}/{total}" if total else ""
```

Note: `app.py` already imports `threading` at the top (line 11); the extra `import threading` here is harmless but you may omit it and instead place the state block below the existing imports — either is fine as long as `threading` is in scope.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest test_app.py -k "scan_progress" -v`
Expected: PASS (both tests)

- [ ] **Step 5: Commit**

```bash
git add vcenter_cmdb/compliance_app/app.py vcenter_cmdb/compliance_app/test_app.py
git commit -m "feat: ScanProgress reporter and scan state (CLAUDE-9jm)"
```

---

## Task 3: Refactor `load_data()` to report progress

**Files:**
- Modify: `compliance_app/app.py` (`load_data`, ~lines 205-249, and the `__main__` block ~line 818)

This task has no new unit test (it requires a live CMDB). It is covered indirectly by Task 4's `_run_scan` tests (which stub `load_data`) and verified manually. Keep the change mechanical.

- [ ] **Step 1: Replace `load_data` body**

Replace the entire `load_data` function with:

```python
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

    inventory = build_inventory(host_cis, vm_cis, bu, bn, bname, hbm, adm)
    log.info("%d unique KEs", len(inventory))

    progress.phase(7)                       # Сборка отчёта
    _rows      = build_report(inventory)
    _summary   = summarize(_rows)
    _divisions = sorted({r.division for r in _rows if r.division})
    log.info("Done — %d KEs | NON_COMPLIANT: %d | OK: %d",
             len(_rows), _summary["NON_COMPLIANT"], _summary["OK"])
    save_snapshot(_rows, source="cmdb")
```

- [ ] **Step 2: Update the startup call**

In the `__main__` block, change `load_data()` to `load_data(ScanProgress())`:

```python
    try:
        load_data(ScanProgress())
```

- [ ] **Step 3: Verify import sanity (no live call)**

Run: `python -c "import app; print(type(app.load_data))"`
Expected: prints `<class 'function'>` with no import error.

- [ ] **Step 4: Run the full suite**

Run: `python -m pytest test_app.py -v`
Expected: all tests PASS (load_data is not exercised live).

- [ ] **Step 5: Commit**

```bash
git add vcenter_cmdb/compliance_app/app.py
git commit -m "refactor: load_data reports scan progress per phase (CLAUDE-9jm)"
```

---

## Task 4: `_run_scan` + scan endpoints

**Files:**
- Modify: `compliance_app/app.py` (add `_run_scan` near `load_data`; add two routes in the Routes section)
- Test: `compliance_app/test_app.py`

- [ ] **Step 1: Write the failing tests**

Add to `test_app.py`:

```python
# ============================================================
# Scan runner + endpoints
# ============================================================

def test_run_scan_success_increments_version(reset_scan_state, monkeypatch):
    monkeypatch.setattr(app_module, "load_data", lambda progress=None: None)
    app_module._scan_state["data_version"] = 5
    app_module._scan_state["running"] = True
    app_module._run_scan()
    assert app_module._scan_state["running"] is False
    assert app_module._scan_state["data_version"] == 6
    assert app_module._scan_state["error"] is None


def test_run_scan_failure_sets_error(reset_scan_state, monkeypatch):
    def boom(progress=None):
        raise RuntimeError("CMDB down")
    monkeypatch.setattr(app_module, "load_data", boom)
    app_module._scan_state["data_version"] = 5
    app_module._scan_state["running"] = True
    app_module._run_scan()
    assert app_module._scan_state["running"] is False
    assert app_module._scan_state["error"] == "CMDB down"
    assert app_module._scan_state["data_version"] == 5


def test_scan_start_returns_202(client, reset_scan_state, monkeypatch):
    monkeypatch.setattr(app_module, "_run_scan", lambda: None)
    app_module._scan_state["running"] = False
    r = client.post("/api/scan/start")
    assert r.status_code == 202
    assert r.get_json()["started"] is True
    assert app_module._scan_state["running"] is True


def test_scan_start_conflict_returns_409(client, reset_scan_state):
    app_module._scan_state["running"] = True
    r = client.post("/api/scan/start")
    assert r.status_code == 409
    assert "error" in r.get_json()


def test_scan_status_route(client, reset_scan_state):
    r = client.get("/api/scan/status")
    assert r.status_code == 200
    data = r.get_json()
    assert "running" in data and "percent" in data and "data_version" in data
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest test_app.py -k "run_scan or scan_start or scan_status" -v`
Expected: FAIL — `_run_scan` missing / 404 on `/api/scan/start`.

- [ ] **Step 3: Implement `_run_scan`**

In `app.py`, immediately after the `load_data` function, add:

```python
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
```

- [ ] **Step 4: Add the endpoints**

In the Routes section (e.g. after the `api_stats` route), add:

```python
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest test_app.py -k "run_scan or scan_start or scan_status" -v`
Expected: PASS (all five)

- [ ] **Step 6: Run the full suite**

Run: `python -m pytest test_app.py -v`
Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add vcenter_cmdb/compliance_app/app.py vcenter_cmdb/compliance_app/test_app.py
git commit -m "feat: scan runner and /api/scan endpoints (CLAUDE-9jm)"
```

---

## Task 5: Frontend — scan button, global banner, polling

**Files:**
- Modify: `compliance_app/app.py` (`_HTML` string: CSS, header markup, JS)
- Test: `compliance_app/test_app.py` (index smoke check)

- [ ] **Step 1: Write the failing smoke test**

Add to `test_app.py`:

```python
def test_index_contains_scan_ui(client):
    r = client.get("/")
    body = r.data.decode("utf-8")
    assert "scan-btn" in body
    assert "startScan" in body
    assert "pollScanStatus" in body
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest test_app.py::test_index_contains_scan_ui -v`
Expected: FAIL — strings not present.

- [ ] **Step 3: Add CSS**

In the `_HTML` `<style>` block, before the closing `</style>`, add:

```css
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
```

- [ ] **Step 4: Add the button + banner markup**

Immediately after the header `</div>` (the block with `<h1>CMDB OS Compliance</h1>`), before `<div class="tabs">`, insert:

```html
  <div class="scanbar">
    <button class="scan-btn" id="scan-btn" onclick="startScan()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
      Сканировать
    </button>
  </div>
  <div class="scan-banner" id="scan-banner">
    <div class="scan-banner-row">
      <span class="scan-phase" id="scan-phase"></span>
      <span class="scan-pct" id="scan-pct"></span>
    </div>
    <div class="scan-track"><div class="scan-fill" id="scan-fill"></div></div>
  </div>
```

- [ ] **Step 5: Make `fetchDivisions` idempotent**

Replace the existing `fetchDivisions` function in the JS with one that clears before rebuilding (so a refresh does not duplicate options):

```javascript
async function fetchDivisions(){
  const d=await(await fetch('/api/divisions')).json();
  const sel=document.getElementById('div-sel');
  const cur=sel.value;
  sel.innerHTML='<option value="">Все дивизионы</option>';
  d.divisions.forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;sel.appendChild(o);});
  if(cur)sel.value=cur;
}
```

- [ ] **Step 6: Add scan JS and start polling**

Immediately before the final init line `fetchStats();fetchDivisions();fetchData();`, insert:

```javascript
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
```

- [ ] **Step 7: Run the smoke test + full suite**

Run: `python -m pytest test_app.py -v`
Expected: all PASS, including `test_index_contains_scan_ui`.

- [ ] **Step 8: Commit**

```bash
git add vcenter_cmdb/compliance_app/app.py vcenter_cmdb/compliance_app/test_app.py
git commit -m "feat: scan button, live progress banner, status polling (CLAUDE-9jm)"
```

---

## Task 6: Manual verification

Automated tests cover the backend; the banner/polling need a live run.

- [ ] **Step 1: Start the app**

Run: `python app.py`
Expected: blocking initial load completes, server starts, browser opens.

- [ ] **Step 2: Trigger a rescan**

Click **Сканировать**, confirm the dialog. Observe:
- banner appears under the header for the whole page,
- bar fills and the phase label changes through the 7 phases,
- on completion the banner disappears and the cards/table refresh,
- a second click while running is a no-op (button disabled), and opening the page in a second tab during a scan shows the same banner.

- [ ] **Step 3: Note the result**

Confirm in the response whether each observable behavior held. If a phase stalls or the bar misreports, capture the `/api/scan/status` JSON for debugging.

---

## Notes for the implementer

- Strings in the `_HTML` block are written with `\uXXXX` escapes for Cyrillic to match the existing file's style — keep that convention.
- Do not change `cmdb_os_compliance.py:main()` or any existing call site; the new
  callback parameters are optional with `None` defaults.
- Run every `pytest` command from the `compliance_app` directory.
