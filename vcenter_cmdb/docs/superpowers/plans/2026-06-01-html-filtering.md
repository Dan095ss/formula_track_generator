# Enhanced HTML Filtering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add division resolution via CMDB branches CI + rich interactive HTML report filters (OS family, division, owner, column sort, CSV export, WHERE query).

**Architecture:** All changes in one file (`cmdb_os_compliance.py`). New pure functions for division resolution are added to the middle of the file. `HostRecord` gains `division`, `ReportRow` gains `division` and `family` (with defaults — backward compat). `_HTML_TEMPLATE` is expanded with new JS state, filter widgets, and sort/export/WHERE logic.

**Tech Stack:** Python 3.12, stdlib only, vanilla JS (no CDN), pytest

---

## File Map

| File | Role |
|---|---|
| `vcenter_cmdb/cmdb_os_compliance.py` | Main file — all logic and template |
| `tests/test_cmdb_os_compliance.py` | Tests — extend, do NOT rewrite existing |

Baseline: **68 tests passing** — every task must leave them green.

---

## Task 1: `branch_number_from_host`

**Files:**
- Modify: `tests/test_cmdb_os_compliance.py` (add tests at end)
- Modify: `vcenter_cmdb/cmdb_os_compliance.py` (add after `_RHEL_VER_RE`)

- [ ] **Step 1.1: Write failing tests**

Add to the END of `tests/test_cmdb_os_compliance.py`:

```python
# ============================================================
# 6. Division resolution helpers
# ============================================================
from vcenter_cmdb.cmdb_os_compliance import (
    branch_number_from_host,
    build_branch_maps,
    ref_uuids_of,
    resolve_division,
)


@pytest.mark.parametrize("shorthost, expected", [
    ("vl1212-kassa1",    "1212"),
    ("u1651-sklad3",     "1651"),
    ("YUG-7760-Admin",   "7760"),
    ("VS7368-kassa1",    "7368"),
    ("u2469-mngr1",      "2469"),
    ("irk020-mngr43",    "20"),     # leading zeros stripped
    ("yrs141-bender-1",  "141"),
    ("yug-6264-nout",    "6264"),
    ("nodigits-host",    None),
    ("",                 None),
])
def test_branch_number_from_host(shorthost, expected):
    assert branch_number_from_host(shorthost) == expected
```

- [ ] **Step 1.2: Run to confirm RED**

```
cd C:\Users\Sevryuk.DA\Documents\CLAUDE\vcenter_cmdb
python -m pytest tests/test_cmdb_os_compliance.py::test_branch_number_from_host -v
```
Expected: `ImportError` or `FAILED`

- [ ] **Step 1.3: Implement `branch_number_from_host`**

Add after `_RHEL_VER_RE = ...` line in `cmdb_os_compliance.py`:

```python
_BRANCH_NUM_RE = re.compile(r'(?i)^[a-z]+-?(\d+)')


def branch_number_from_host(shorthost: str) -> str | None:
    """Extract numeric branch code from shorthost, stripping leading zeros.

    Examples: 'vl1212-kassa' -> '1212', 'irk020-srv' -> '20'.
    Returns None if no leading-letters+digits pattern found.
    """
    m = _BRANCH_NUM_RE.match(shorthost)
    if not m:
        return None
    return str(int(m.group(1)))
```

- [ ] **Step 1.4: Run to confirm GREEN**

```
python -m pytest tests/test_cmdb_os_compliance.py::test_branch_number_from_host -v
```
Expected: 10 PASSED

- [ ] **Step 1.5: Run full suite to confirm no regressions**

```
python -m pytest tests/test_cmdb_os_compliance.py -q
```
Expected: 78 passed

- [ ] **Step 1.6: Commit**

```bash
git add vcenter_cmdb/cmdb_os_compliance.py tests/test_cmdb_os_compliance.py
git commit -m "feat: add branch_number_from_host for division fallback lookup"
```

---

## Task 2: `ref_uuids_of` + `build_branch_maps`

**Files:**
- Modify: `tests/test_cmdb_os_compliance.py`
- Modify: `vcenter_cmdb/cmdb_os_compliance.py`

- [ ] **Step 2.1: Write failing tests**

Add after `test_branch_number_from_host` in the test file:

```python
def _make_ci_with_ref(plain_attrs: dict[str, str], ref_uuid: str) -> dict:
    """Build CI where one attr has a ref pointing to ref_uuid."""
    attrs = [
        {
            "uuid": f"attr-{k}", "attr_type_uuid": f"type-{k}",
            "bvalue": v,
            "type": {"uuid": f"type-{k}", "name": k, "type": "string"},
        }
        for k, v in plain_attrs.items()
    ]
    attrs.append({
        "uuid": "attr-ref-branch", "attr_type_uuid": "type-ref-branch",
        "bvalue": "branch-link",
        "type": {"uuid": "type-ref-branch", "name": "branch", "type": "ref"},
        "ref": {"uuid": ref_uuid, "ref_type_uuid": "rt-1", "is_visible": True},
    })
    return {"uuid": "host-111", "name": "test-host", "attrs": attrs}


def test_ref_uuids_of_finds_ref():
    ci = _make_ci_with_ref({"shorthost": "srv01"}, "branch-uuid-aaa")
    assert "branch-uuid-aaa" in ref_uuids_of(ci)


def test_ref_uuids_of_no_refs():
    ci = _make_ci({"shorthost": "srv01"})
    assert ref_uuids_of(ci) == set()


def test_ref_uuids_of_null_ref():
    ci = {
        "uuid": "x", "name": "y",
        "attrs": [{"uuid": "a1", "attr_type_uuid": "t1", "bvalue": "v",
                   "type": {"name": "foo", "type": "string"}, "ref": None}],
    }
    assert ref_uuids_of(ci) == set()


def _make_branch_ci(uuid: str, number: str, ter_lvl_2: str) -> dict:
    return {
        "uuid": uuid,
        "name": f"branch-{number}",
        "attrs": [
            {"uuid": f"a-num-{uuid}", "attr_type_uuid": "t-num", "bvalue": number,
             "type": {"uuid": "t-num", "name": "number", "type": "string"}},
            {"uuid": f"a-div-{uuid}", "attr_type_uuid": "t-div", "bvalue": ter_lvl_2,
             "type": {"uuid": "t-div", "name": "ter_lvl_2", "type": "string"}},
        ],
    }


def test_build_branch_maps_by_uuid():
    branches = [_make_branch_ci("uuid-aaa", "1212", "04. дів. Урал")]
    by_uuid, _ = build_branch_maps(branches)
    assert by_uuid["uuid-aaa"] == "04. дів. Урал"


def test_build_branch_maps_by_number():
    branches = [_make_branch_ci("uuid-bbb", "020", "05. дів. Юг")]
    _, by_number = build_branch_maps(branches)
    assert by_number["20"] == "05. дів. Юг"   # leading zeros stripped


def test_build_branch_maps_skips_no_division():
    branches = [_make_branch_ci("uuid-ccc", "999", "")]  # empty ter_lvl_2
    by_uuid, by_number = build_branch_maps(branches)
    assert "uuid-ccc" not in by_uuid
    assert "999" not in by_number
```

- [ ] **Step 2.2: Run to confirm RED**

```
python -m pytest tests/test_cmdb_os_compliance.py -k "ref_uuids_of or build_branch_maps" -v
```
Expected: ImportError / FAILED

- [ ] **Step 2.3: Implement `ref_uuids_of` and `build_branch_maps`**

Add to `cmdb_os_compliance.py` in the **CItem Parsers** section, after `owner_of()`:

```python
def ref_uuids_of(ci: dict) -> set[str]:
    """Return set of ref UUIDs from all attrs of this CI (ignores attrs without ref)."""
    result: set[str] = set()
    for attr in ci.get("attrs") or []:
        ref = attr.get("ref")
        if ref and ref.get("uuid"):
            result.add(ref["uuid"])
    return result
```

Add to `cmdb_os_compliance.py` in the **Host Inventory** section, before `build_inventory()`:

```python
def build_branch_maps(
    branch_cis: Iterable[dict],
) -> tuple[dict[str, str], dict[str, str]]:
    """Build two lookup dicts from branches CI list.

    Returns:
        by_uuid:   {branch_ci_uuid -> ter_lvl_2}
        by_number: {branch_number_str (no leading zeros) -> ter_lvl_2}
    """
    by_uuid: dict[str, str] = {}
    by_number: dict[str, str] = {}
    for ci in branch_cis:
        uuid = ci.get("uuid")
        if not uuid:
            continue
        attrs = extract_attrs(ci)
        division = attrs.get("ter_lvl_2", "").strip()
        if not division:
            continue
        by_uuid[uuid] = division
        number_raw = attrs.get("number", "").strip()
        if number_raw:
            try:
                by_number[str(int(number_raw))] = division
            except ValueError:
                pass
    return by_uuid, by_number
```

- [ ] **Step 2.4: Run to confirm GREEN**

```
python -m pytest tests/test_cmdb_os_compliance.py -k "ref_uuids_of or build_branch_maps" -v
```
Expected: 7 PASSED

- [ ] **Step 2.5: Full suite**

```
python -m pytest tests/test_cmdb_os_compliance.py -q
```
Expected: 85 passed

- [ ] **Step 2.6: Commit**

```bash
git add vcenter_cmdb/cmdb_os_compliance.py tests/test_cmdb_os_compliance.py
git commit -m "feat: add ref_uuids_of and build_branch_maps for branch CI lookup"
```

---

## Task 3: `resolve_division`

**Files:**
- Modify: `tests/test_cmdb_os_compliance.py`
- Modify: `vcenter_cmdb/cmdb_os_compliance.py`

- [ ] **Step 3.1: Write failing tests**

Add after Task 2 tests:

```python
def test_resolve_division_via_ref():
    ci = _make_ci_with_ref({"shorthost": "srv01"}, "branch-uuid-aaa")
    by_uuid = {"branch-uuid-aaa": "04. дів. Урал"}
    assert resolve_division(ci, by_uuid, {}) == "04. дів. Урал"


def test_resolve_division_fallback_hostname():
    ci = _make_ci({"shorthost": "vl1212-kassa1"})
    by_number = {"1212": "08. дів. Центральный"}
    assert resolve_division(ci, {}, by_number) == "08. дів. Центральный"


def test_resolve_division_ref_takes_priority():
    # ref matches AND hostname also has a number — ref wins
    ci = _make_ci_with_ref({"shorthost": "vl1212-kassa1"}, "branch-uuid-aaa")
    by_uuid = {"branch-uuid-aaa": "04. дів. Урал"}
    by_number = {"1212": "99. Other"}
    assert resolve_division(ci, by_uuid, by_number) == "04. дів. Урал"


def test_resolve_division_no_match():
    ci = _make_ci({"shorthost": "nodigits-host"})
    assert resolve_division(ci, {}, {}) is None


def test_resolve_division_unknown_number():
    ci = _make_ci({"shorthost": "vl9999-srv"})
    by_number = {"1212": "04. дів. Урал"}
    assert resolve_division(ci, {}, by_number) is None
```

- [ ] **Step 3.2: Run to confirm RED**

```
python -m pytest tests/test_cmdb_os_compliance.py -k "resolve_division" -v
```
Expected: ImportError / FAILED

- [ ] **Step 3.3: Implement `resolve_division`**

Add in `cmdb_os_compliance.py`, in the **Host Inventory** section, right before `build_branch_maps()`:

```python
def resolve_division(
    ci: dict,
    branches_by_uuid: dict[str, str],
    branches_by_number: dict[str, str],
) -> str | None:
    """Determine ter_lvl_2 (division) for a CI.

    Primary:  scan CI attrs for any ref.uuid present in branches_by_uuid.
    Fallback: extract numeric code from shorthost, look up in branches_by_number.
    Returns None if division cannot be determined.
    """
    for ref_uuid in ref_uuids_of(ci):
        division = branches_by_uuid.get(ref_uuid)
        if division:
            return division
    sh = shorthost_of(ci) or ""
    code = branch_number_from_host(sh)
    if code:
        return branches_by_number.get(code)
    return None
```

- [ ] **Step 3.4: Run to confirm GREEN**

```
python -m pytest tests/test_cmdb_os_compliance.py -k "resolve_division" -v
```
Expected: 5 PASSED

- [ ] **Step 3.5: Full suite**

```
python -m pytest tests/test_cmdb_os_compliance.py -q
```
Expected: 90 passed

- [ ] **Step 3.6: Commit**

```bash
git add vcenter_cmdb/cmdb_os_compliance.py tests/test_cmdb_os_compliance.py
git commit -m "feat: add resolve_division with ref-primary and hostname-fallback"
```

---

## Task 4: Extend data model — `HostRecord`, `ReportRow`, `build_inventory`, `build_report`, `write_csv`

**Files:**
- Modify: `vcenter_cmdb/cmdb_os_compliance.py`
- Modify: `tests/test_cmdb_os_compliance.py`

All new fields have **defaults** so the 68 existing tests keep passing unchanged.

- [ ] **Step 4.1: Write new failing tests**

Add after Task 3 tests:

```python
# ============================================================
# 7. Data model — division + family fields
# ============================================================

def test_host_record_has_division():
    rec = HostRecord(shorthost="srv01", os_name="ubuntu 22.04", owner="IT", division="04. дів. Урал", sources={"HOST"})
    assert rec.division == "04. дів. Урал"


def test_host_record_division_defaults_none():
    rec = HostRecord(shorthost="srv01", os_name=None, owner=None, sources={"HOST"})
    assert rec.division is None


def test_report_row_has_division_and_family():
    r = ReportRow("srv01", "ubuntu 22.04", "IT", "HOST", Status.OK, "ok", division="04. дів. Урал", family="linux")
    assert r.division == "04. дів. Урал"
    assert r.family == "linux"


def test_report_row_defaults():
    r = ReportRow("srv01", "ubuntu", "IT", "HOST", Status.OK, "ok")
    assert r.division == ""
    assert r.family == ""


def test_build_inventory_sets_division():
    branch_ci = _make_branch_ci("branch-uuid-1", "1212", "04. дів. Урал")
    by_uuid, by_number = build_branch_maps([branch_ci])
    host_ci = _make_ci_with_ref({"shorthost": "srv01", "os_name": "ubuntu 22.04"}, "branch-uuid-1")
    inv = build_inventory([host_ci], [], by_uuid, by_number)
    assert inv["srv01"].division == "04. дів. Урал"


def test_build_inventory_division_fallback():
    branch_ci = _make_branch_ci("branch-uuid-2", "1212", "08. дів. Центральный")
    by_uuid, by_number = build_branch_maps([branch_ci])
    host_ci = _make_ci({"shorthost": "vl1212-kassa", "os_name": "ubuntu 22.04"})
    inv = build_inventory([host_ci], [], by_uuid, by_number)
    assert inv["vl1212-kassa"].division == "08. дів. Центральный"


def test_build_report_sets_family_and_division():
    rec = HostRecord(shorthost="srv01", os_name="ubuntu 22.04 lts|...", owner="IT",
                     division="04. дів. Урал", sources={"HOST"})
    rows = build_report({"srv01": rec})
    assert rows[0].family == "linux"
    assert rows[0].division == "04. дів. Урал"


def test_write_csv_includes_division_family(tmp_path):
    rows = [
        ReportRow("srv01", "ubuntu 22.04", "IT", "HOST", Status.OK, "ok",
                  division="04. дів. Урал", family="linux"),
    ]
    out = tmp_path / "r.csv"
    write_csv(rows, out)
    content = out.read_text(encoding="utf-8-sig")
    assert "division" in content
    assert "04. дів. Урал" in content
    assert "family" in content
    assert "linux" in content
```

- [ ] **Step 4.2: Run to confirm RED**

```
python -m pytest tests/test_cmdb_os_compliance.py -k "division or family" -v
```
Expected: multiple FAILED

- [ ] **Step 4.3: Update `HostRecord` — add `division` with default**

In `cmdb_os_compliance.py`, replace the `HostRecord` dataclass:

```python
@dataclass
class HostRecord:
    shorthost: str
    os_name: str | None
    owner: str | None
    division: str | None
    sources: set[str]

    def __init__(
        self,
        shorthost: str,
        os_name: str | None,
        owner: str | None,
        sources: set[str],
        division: str | None = None,
    ) -> None:
        self.shorthost = shorthost
        self.os_name = os_name
        self.owner = owner
        self.division = division
        self.sources = sources

    @property
    def ke_type(self) -> str:
        if self.sources == {"HOST"}:
            return "HOST"
        if self.sources == {"VM"}:
            return "VM"
        return "HOST+VM"
```

> Note: We use `__init__` instead of `@dataclass` default so `division` can have a default while `sources` (a mutable set) comes before it. The `@dataclass` decorator is kept but we override `__init__`.

Actually simpler: just reorder so `division` comes last with default:

```python
@dataclass
class HostRecord:
    shorthost: str
    os_name: str | None
    owner: str | None
    sources: set[str]
    division: str | None = None

    @property
    def ke_type(self) -> str:
        if self.sources == {"HOST"}:
            return "HOST"
        if self.sources == {"VM"}:
            return "VM"
        return "HOST+VM"
```

- [ ] **Step 4.4: Update `ReportRow` — add `division` and `family` with defaults**

Replace the `ReportRow` dataclass:

```python
@dataclass
class ReportRow:
    shorthost: str
    os_name: str
    owner: str
    ke_type: str
    status: Status
    reason: str
    division: str = ""
    family: str = ""
```

- [ ] **Step 4.5: Update `build_inventory` — accept and use branch maps**

Replace the `build_inventory` signature and HOST-insertion block:

```python
def build_inventory(
    host_cis: Iterable[dict],
    vm_cis: Iterable[dict],
    branches_by_uuid: dict[str, str] | None = None,
    branches_by_number: dict[str, str] | None = None,
) -> dict[str, HostRecord]:
    """Build {shorthost: HostRecord}. HOST os_name and owner take priority over VM."""
    bu = branches_by_uuid or {}
    bn = branches_by_number or {}
    inv: dict[str, HostRecord] = {}

    skip_host = 0
    for ci in host_cis:
        sh = shorthost_of(ci)
        if not sh:
            skip_host += 1
            continue
        osn = os_name_of(ci)
        own = owner_of(ci)
        div = resolve_division(ci, bu, bn)
        if sh in inv:
            log.warning("Duplicate HOST shorthost %r — keeping first values", sh)
            inv[sh].sources.add("HOST")
            if inv[sh].os_name is None and osn:
                inv[sh].os_name = osn
            if inv[sh].owner is None and own:
                inv[sh].owner = own
            if inv[sh].division is None and div:
                inv[sh].division = div
        else:
            inv[sh] = HostRecord(shorthost=sh, os_name=osn, owner=own, sources={"HOST"}, division=div)

    if skip_host:
        log.debug("Skipped %d HOST CIs without shorthost", skip_host)

    skip_vm = 0
    for ci in vm_cis:
        sh = shorthost_of(ci)
        if not sh:
            skip_vm += 1
            continue
        osn = os_name_of(ci)
        own = owner_of(ci)
        div = resolve_division(ci, bu, bn)
        if sh in inv:
            inv[sh].sources.add("VM")
            # HOST values win — do NOT overwrite
        else:
            inv[sh] = HostRecord(shorthost=sh, os_name=osn, owner=own, sources={"VM"}, division=div)

    if skip_vm:
        log.debug("Skipped %d VM CIs without shorthost", skip_vm)

    return inv
```

- [ ] **Step 4.6: Update `build_report` — pass `family` and `division`**

Replace `build_report`:

```python
def build_report(inventory: dict[str, HostRecord]) -> list[ReportRow]:
    rows: list[ReportRow] = []
    for rec in inventory.values():
        result = classify_os(rec.os_name)
        rows.append(ReportRow(
            shorthost=rec.shorthost,
            os_name=rec.os_name or "",
            owner=rec.owner or "",
            ke_type=rec.ke_type,
            status=result.status,
            reason=result.reason,
            division=rec.division or "",
            family=result.family,
        ))
    rows.sort(key=lambda r: (_STATUS_PRIORITY[r.status], r.shorthost))
    return rows
```

- [ ] **Step 4.7: Update `write_csv` — add new columns**

Replace `write_csv`:

```python
def write_csv(rows: list[ReportRow], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["shorthost", "os_name", "owner", "division", "ke_type", "family", "status", "reason"])
        for r in rows:
            writer.writerow([r.shorthost, r.os_name, r.owner, r.division, r.ke_type, r.family, r.status, r.reason])
```

- [ ] **Step 4.8: Run all new tests GREEN**

```
python -m pytest tests/test_cmdb_os_compliance.py -k "division or family" -v
```
Expected: all PASSED

- [ ] **Step 4.9: Full suite — must stay green**

```
python -m pytest tests/test_cmdb_os_compliance.py -q
```
Expected: 103 passed (68 original + 35 new)

- [ ] **Step 4.10: Commit**

```bash
git add vcenter_cmdb/cmdb_os_compliance.py tests/test_cmdb_os_compliance.py
git commit -m "feat: extend HostRecord/ReportRow with division+family, wire build_inventory"
```

---

## Task 5: Update `main()` — fetch branches before inventory

**Files:**
- Modify: `vcenter_cmdb/cmdb_os_compliance.py`

No new tests needed (main is integration-level; existing mock tests cover it via build_inventory).

- [ ] **Step 5.1: Update `main()`**

In `main()`, replace the try-block body:

```python
    try:
        client.check_auth()
        host_uuid   = client.get_ci_type_uuid("HOST")
        vm_uuid     = client.get_ci_type_uuid("VM")
        branch_uuid = client.get_ci_type_uuid("branches")
        log.info("Pre-loading branches for division lookup…")
        branches_by_uuid, branches_by_number = build_branch_maps(
            client.iter_cis(branch_uuid)
        )
        log.info("Loaded %d branch UUIDs, %d branch numbers",
                 len(branches_by_uuid), len(branches_by_number))
        inventory = build_inventory(
            client.iter_cis(host_uuid),
            client.iter_cis(vm_uuid),
            branches_by_uuid,
            branches_by_number,
        )
        rows = build_report(inventory)
        summary = summarize(rows)
        print_console_table(rows, summary)
        write_csv(rows, config.output_path)
        write_html(rows, summary, config.html_path)
        log.info("CSV:  %s", config.output_path)
        log.info("HTML: %s", config.html_path)
```

- [ ] **Step 5.2: Full suite still green**

```
python -m pytest tests/test_cmdb_os_compliance.py -q
```
Expected: same count, all PASSED

- [ ] **Step 5.3: Commit**

```bash
git add vcenter_cmdb/cmdb_os_compliance.py
git commit -m "feat: fetch branches CI in main() and pass division maps to build_inventory"
```

---

## Task 6: HTML — new filters (OS Family, Division, Owner) + Division column

**Files:**
- Modify: `vcenter_cmdb/cmdb_os_compliance.py` (the `_HTML_TEMPLATE` string and `write_html()`)
- Modify: `tests/test_cmdb_os_compliance.py`

- [ ] **Step 6.1: Write failing HTML tests**

Add after existing test file tests:

```python
# ============================================================
# 8. HTML extended
# ============================================================

def _html_rows():
    return [
        ReportRow("srv01", "ubuntu 22.04 lts|...", "IT-отдел A / Ivanov.AA", "HOST",
                  Status.OK, "OK: Ubuntu 22.04 LTS", division="04. дів. Урал", family="linux"),
        ReportRow("vm01", "windows server 2019|", "IT-отдел B", "VM",
                  Status.WARNING, "WARNING: WS 2019", division="05. дів. Юг", family="windows_server"),
        ReportRow("vm02", "windows 10 pro|22h2", "", "VM",
                  Status.NON_COMPLIANT, "NON_COMPLIANT: Win10", division="", family="windows_client"),
    ]


def test_write_html_includes_division_and_family(tmp_path):
    rows = _html_rows()
    summary = {"total": 3, "OK": 1, "WARNING": 1, "NON_COMPLIANT": 1, "UNKNOWN": 0}
    out = tmp_path / "r.html"
    write_html(rows, summary, out)
    content = out.read_text(encoding="utf-8")
    assert '"division"' in content          # field in JS data
    assert '"family"' in content            # field in JS data
    assert "04. дів. Урал" in content
    assert "windows_server" in content
    assert "linux" in content


def test_write_html_has_os_family_buttons(tmp_path):
    rows = _html_rows()
    summary = {"total": 3, "OK": 1, "WARNING": 1, "NON_COMPLIANT": 1, "UNKNOWN": 0}
    out = tmp_path / "r.html"
    write_html(rows, summary, out)
    content = out.read_text(encoding="utf-8")
    assert "windows_server" in content
    assert "windows_client" in content
    assert "linux" in content
    assert "filterByFamily" in content      # JS function exists


def test_write_html_has_export_and_where(tmp_path):
    rows = _html_rows()
    summary = {"total": 3, "OK": 1, "WARNING": 1, "NON_COMPLIANT": 1, "UNKNOWN": 0}
    out = tmp_path / "r.html"
    write_html(rows, summary, out)
    content = out.read_text(encoding="utf-8")
    assert "exportCSV" in content           # export function
    assert "compileWhere" in content        # WHERE parser
    assert "Скачать CSV" in content         # button label
```

- [ ] **Step 6.2: Run to confirm RED**

```
python -m pytest tests/test_cmdb_os_compliance.py -k "html_includes_division or html_has_os_family or html_has_export" -v
```
Expected: FAILED (fields missing from current template)

- [ ] **Step 6.3: Update `write_html()` to include new fields in JSON data**

In `write_html()`, update the data list comprehension:

```python
def write_html(rows: list[ReportRow], summary: dict[str, int], path: Path) -> None:
    import json as _json
    data = [
        {
            "shorthost": r.shorthost,
            "os_name":   r.os_name,
            "owner":     r.owner,
            "division":  r.division,
            "ke_type":   r.ke_type,
            "family":    r.family,
            "status":    r.status,
            "reason":    r.reason,
        }
        for r in rows
    ]
    content = _HTML_TEMPLATE.format(
        report_date=date.today().strftime("%d.%m.%Y"),
        generated_at=datetime.now().strftime("%d.%m.%Y %H:%M"),
        total=summary["total"],
        ok=summary["OK"],
        warning=summary["WARNING"],
        fail=summary["NON_COMPLIANT"],
        unknown=summary["UNKNOWN"],
        data_json=_json.dumps(data, ensure_ascii=False),
    )
    path.write_text(content, encoding="utf-8")
```

- [ ] **Step 6.4: Replace `_HTML_TEMPLATE`**

This is a full template replacement. The new template adds:
- `division` column between `owner` and `ke_type`
- OS Family toggle buttons
- Division and Owner `<select>` dropdowns populated from data
- Updated JS state variables and `applyFilters()`
- Placeholder hooks for sort/export/WHERE (implemented in Tasks 7-8)

Replace the entire `_HTML_TEMPLATE = """\...""""` string with the following. **Key JS additions are marked with `// NEW`.**

```python
_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Отчёт соответствия ОС регламенту — {report_date}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; color: #1a1a2e; }}
  .page {{ max-width: 1500px; margin: 0 auto; padding: 24px 20px; }}

  .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
             color: #fff; border-radius: 12px; padding: 28px 32px; margin-bottom: 24px; }}
  .header h1 {{ font-size: 22px; font-weight: 700; letter-spacing: .5px; }}
  .header .meta {{ margin-top: 6px; font-size: 13px; opacity: .7; }}

  .cards {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }}
  .card {{ flex: 1; min-width: 140px; background: #fff; border-radius: 10px;
           padding: 18px 20px; box-shadow: 0 1px 4px rgba(0,0,0,.08); cursor: pointer;
           transition: box-shadow .15s; }}
  .card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,.15); }}
  .card .num {{ font-size: 32px; font-weight: 700; line-height: 1; }}
  .card .lbl {{ font-size: 12px; color: #666; margin-top: 4px; text-transform: uppercase; letter-spacing: .6px; }}
  .card.total .num {{ color: #1a1a2e; }}
  .card.ok    .num {{ color: #16a34a; }}
  .card.warn  .num {{ color: #d97706; }}
  .card.fail  .num {{ color: #dc2626; }}
  .card.unk   .num {{ color: #6b7280; }}

  .filterbar {{ background: #fff; border-radius: 10px; padding: 14px 20px;
                margin-bottom: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  .filter-row {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 8px; }}
  .filter-row:last-child {{ margin-bottom: 0; }}
  .filter-label {{ font-size: 11px; font-weight: 600; color: #6b7280;
                   text-transform: uppercase; letter-spacing: .5px; white-space: nowrap; min-width: 60px; }}
  .filterbar input[type=text] {{ flex: 1; min-width: 200px; padding: 8px 12px;
                                  border: 1px solid #d1d5db; border-radius: 6px;
                                  font-size: 14px; outline: none; }}
  .filterbar input[type=text]:focus {{ border-color: #0f3460; box-shadow: 0 0 0 3px rgba(15,52,96,.12); }}
  .filter-btn {{ padding: 7px 14px; border: 1px solid #d1d5db; border-radius: 6px;
                 background: #fff; cursor: pointer; font-size: 13px; font-weight: 500;
                 transition: all .15s; white-space: nowrap; }}
  .filter-btn:hover {{ background: #f3f4f6; }}
  .filter-btn.active {{ background: #0f3460; color: #fff; border-color: #0f3460; }}
  .filter-btn.fam-ws.active  {{ background: #7c3aed; border-color: #7c3aed; }}
  .filter-btn.fam-wc.active  {{ background: #2563eb; border-color: #2563eb; }}
  .filter-btn.fam-lx.active  {{ background: #059669; border-color: #059669; }}
  .filter-btn.fam-unk.active {{ background: #6b7280; border-color: #6b7280; }}
  .sel {{ padding: 7px 10px; border: 1px solid #d1d5db; border-radius: 6px;
          font-size: 13px; cursor: pointer; background: #fff; max-width: 280px; }}
  .page-size-sel {{ padding: 7px 10px; border: 1px solid #d1d5db; border-radius: 6px;
                    font-size: 13px; cursor: pointer; background: #fff; }}
  .where-input {{ font-family: 'Consolas', monospace; font-size: 13px; }}
  .where-error {{ font-size: 12px; color: #dc2626; margin-left: 8px; }}
  .export-btn {{ padding: 7px 16px; border: 1px solid #0f3460; border-radius: 6px;
                 background: #0f3460; color: #fff; cursor: pointer; font-size: 13px;
                 font-weight: 500; white-space: nowrap; transition: background .15s; }}
  .export-btn:hover {{ background: #16213e; }}

  .table-wrap {{ background: #fff; border-radius: 10px; overflow: hidden;
                 box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; }}
  thead th {{ background: #1a1a2e; color: #fff; padding: 12px 14px; text-align: left;
              font-weight: 600; font-size: 12px; letter-spacing: .5px;
              text-transform: uppercase; white-space: nowrap;
              cursor: pointer; user-select: none; }}
  thead th:hover {{ background: #16213e; }}
  thead th .sort-icon {{ margin-left: 4px; opacity: .5; }}
  thead th.sort-asc .sort-icon::after  {{ content: ' ▲'; opacity: 1; }}
  thead th.sort-desc .sort-icon::after {{ content: ' ▼'; opacity: 1; }}
  tbody tr {{ border-bottom: 1px solid #f0f0f0; transition: background .1s; }}
  tbody tr:last-child {{ border-bottom: none; }}
  td {{ padding: 10px 14px; vertical-align: top; }}
  td.host {{ font-family: 'Consolas', monospace; font-size: 13px; font-weight: 600; color: #0f3460; }}
  td.os   {{ color: #374151; }}
  td.own  {{ color: #4b5563; font-size: 13px; }}
  td.div  {{ color: #6b7280; font-size: 12px; }}
  td.ke   {{ font-size: 12px; color: #6b7280; white-space: nowrap; }}
  td.fam  {{ font-size: 11px; color: #9ca3af; white-space: nowrap; }}
  td.reason {{ font-size: 12px; color: #6b7280; }}

  .row-fail    {{ background: #fff5f5; }}
  .row-warning {{ background: #fffbeb; }}
  .row-ok      {{ background: #f0fdf4; }}
  .row-unknown {{ background: #f9fafb; }}
  .row-fail:hover    {{ background: #fee2e2; }}
  .row-warning:hover {{ background: #fef3c7; }}
  .row-ok:hover      {{ background: #dcfce7; }}
  .row-unknown:hover {{ background: #f3f4f6; }}

  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px;
            font-size: 11px; font-weight: 700; letter-spacing: .4px; white-space: nowrap; }}
  .badge.ok      {{ background: #dcfce7; color: #15803d; }}
  .badge.warning {{ background: #fef3c7; color: #b45309; }}
  .badge.fail    {{ background: #fee2e2; color: #b91c1c; }}
  .badge.unknown {{ background: #f3f4f6; color: #6b7280; }}

  .pagination {{ display: flex; align-items: center; justify-content: space-between;
                 padding: 14px 20px; background: #fff; border-top: 1px solid #f0f0f0;
                 flex-wrap: wrap; gap: 10px; }}
  .pag-info {{ font-size: 13px; color: #6b7280; }}
  .pag-controls {{ display: flex; gap: 4px; align-items: center; flex-wrap: wrap; }}
  .pag-btn {{ min-width: 34px; height: 34px; padding: 0 10px; border: 1px solid #d1d5db;
              border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px;
              display: flex; align-items: center; justify-content: center;
              transition: all .15s; white-space: nowrap; }}
  .pag-btn:hover:not(:disabled) {{ background: #f3f4f6; }}
  .pag-btn.active {{ background: #0f3460; color: #fff; border-color: #0f3460; font-weight: 700; }}
  .pag-btn:disabled {{ opacity: .4; cursor: default; }}
  .pag-ellipsis {{ padding: 0 6px; color: #9ca3af; font-size: 14px; }}

  .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #9ca3af; }}
  .empty {{ padding: 40px; text-align: center; color: #9ca3af; font-size: 14px; }}
</style>
</head>
<body>
<div class="page">

  <div class="header">
    <h1>Отчёт соответствия ОС корпоративному регламенту</h1>
    <div class="meta">Сформирован: {generated_at} &nbsp;·&nbsp; Всего КЕ: {total}</div>
  </div>

  <div class="cards">
    <div class="card total" onclick="filterByStatus('ALL')">
      <div class="num">{total}</div><div class="lbl">Всего</div></div>
    <div class="card ok"   onclick="filterByStatus('OK')">
      <div class="num">{ok}</div><div class="lbl">Соответствует</div></div>
    <div class="card warn" onclick="filterByStatus('WARNING')">
      <div class="num">{warning}</div><div class="lbl">Условно допустимо</div></div>
    <div class="card fail" onclick="filterByStatus('NON_COMPLIANT')">
      <div class="num">{fail}</div><div class="lbl">Не соответствует</div></div>
    <div class="card unk"  onclick="filterByStatus('UNKNOWN')">
      <div class="num">{unknown}</div><div class="lbl">Нет данных об ОС</div></div>
  </div>

  <div class="filterbar">
    <div class="filter-row">
      <span class="filter-label">Статус</span>
      <button class="filter-btn active" data-status="ALL"           onclick="setStatus(this)">Все</button>
      <button class="filter-btn"        data-status="NON_COMPLIANT" onclick="setStatus(this)">Не соответствует</button>
      <button class="filter-btn"        data-status="WARNING"       onclick="setStatus(this)">Условно</button>
      <button class="filter-btn"        data-status="OK"            onclick="setStatus(this)">OK</button>
      <button class="filter-btn"        data-status="UNKNOWN"       onclick="setStatus(this)">Нет данных</button>
    </div>
    <div class="filter-row">
      <span class="filter-label">ОС</span>
      <button class="filter-btn active fam-all" data-fam="ALL"            onclick="setFamily(this)">Все</button>
      <button class="filter-btn fam-ws"         data-fam="windows_server" onclick="setFamily(this)">Windows Server</button>
      <button class="filter-btn fam-wc"         data-fam="windows_client" onclick="setFamily(this)">Windows Client</button>
      <button class="filter-btn fam-lx"         data-fam="linux"          onclick="setFamily(this)">Linux</button>
      <button class="filter-btn fam-unk"        data-fam="unknown"        onclick="setFamily(this)">Неизвестно</button>
    </div>
    <div class="filter-row">
      <span class="filter-label">Дивизион</span>
      <select class="sel" id="div-sel" onchange="applyFilters()">
        <option value="">Все дивизионы</option>
      </select>
      <span class="filter-label" style="margin-left:12px">Владелец</span>
      <select class="sel" id="owner-sel" onchange="applyFilters()">
        <option value="">Все владельцы</option>
      </select>
      <select class="page-size-sel" onchange="changePageSize(this.value)" style="margin-left:auto">
        <option value="50">50 / стр.</option>
        <option value="100" selected>100 / стр.</option>
        <option value="200">200 / стр.</option>
        <option value="500">500 / стр.</option>
      </select>
    </div>
    <div class="filter-row">
      <span class="filter-label">Поиск</span>
      <input type="text" id="search" placeholder="Текстовый поиск по хосту, ОС, владельцу…" oninput="applyFilters()">
    </div>
    <div class="filter-row">
      <span class="filter-label">WHERE</span>
      <input type="text" class="where-input" id="where"
             placeholder='status = "NON_COMPLIANT" AND division LIKE "04%"'
             oninput="applyWhere()" style="flex:1;min-width:300px">
      <span class="where-error" id="where-err"></span>
      <button class="export-btn" onclick="exportCSV()">⬇ Скачать CSV</button>
    </div>
  </div>

  <div class="table-wrap">
    <table>
      <thead id="thead"></thead>
      <tbody id="tbody"></tbody>
    </table>
    <div class="pagination">
      <div class="pag-info" id="pag-info"></div>
      <div class="pag-controls" id="pag-controls"></div>
    </div>
  </div>

  <div class="footer">Регламент допустимых ОС от 13.05.2026 &nbsp;·&nbsp; CMDB OS Compliance Checker</div>
</div>

<script>
var DATA = {data_json};

var ROW_CLASS = {{
  'OK': 'row-ok', 'WARNING': 'row-warning',
  'NON_COMPLIANT': 'row-fail', 'UNKNOWN': 'row-unknown'
}};
var BADGE = {{
  'OK':            '<span class="badge ok">OK</span>',
  'WARNING':       '<span class="badge warning">WARNING</span>',
  'NON_COMPLIANT': '<span class="badge fail">NON_COMPLIANT</span>',
  'UNKNOWN':       '<span class="badge unknown">UNKNOWN</span>'
}};
var FAMILY_LABEL = {{
  'windows_server': 'Win Server', 'windows_client': 'Win Client',
  'linux': 'Linux', 'unknown': '—'
}};
var COLS = [
  {{f:'shorthost', label:'Хост',    cls:'host'}},
  {{f:'os_name',   label:'ОС',      cls:'os'}},
  {{f:'owner',     label:'Владелец',cls:'own'}},
  {{f:'division',  label:'Дивизион',cls:'div'}},
  {{f:'ke_type',   label:'Тип КЕ', cls:'ke'}},
  {{f:'family',    label:'Семейство',cls:'fam'}},
  {{f:'status',    label:'Статус',  cls:''}},
  {{f:'reason',    label:'Причина', cls:'reason'}},
];

var filtered = DATA.slice();
var currentPage = 1;
var pageSize = 100;
var activeStatus = 'ALL';
var activeFamily = 'ALL';
var sortField = null;
var sortDir = 0;   // 0=none 1=asc -1=desc
var compiledWhere = null;

// ── Init dropdowns ──────────────────────────────────────────
function initDropdowns() {{
  var divs   = Array.from(new Set(DATA.map(function(r){{return r.division||'';}})))
                    .filter(Boolean).sort();
  var owners = Array.from(new Set(DATA.map(function(r){{return r.owner||'';}})))
                    .filter(Boolean).sort();
  var dsel = document.getElementById('div-sel');
  divs.forEach(function(d) {{
    var o = document.createElement('option'); o.value = d; o.textContent = d; dsel.appendChild(o);
  }});
  var osel = document.getElementById('owner-sel');
  owners.forEach(function(o) {{
    var el = document.createElement('option'); el.value = o; el.textContent = o; osel.appendChild(el);
  }});
}}

// ── Header with sort ────────────────────────────────────────
function renderHeaders() {{
  var html = '<tr>';
  COLS.forEach(function(col) {{
    var cls = '';
    if (sortField === col.f) cls = sortDir === 1 ? ' sort-asc' : ' sort-desc';
    html += '<th class="' + cls + '" onclick="toggleSort(\'' + col.f + '\')">' +
            col.label + '<span class="sort-icon"></span></th>';
  }});
  html += '</tr>';
  document.getElementById('thead').innerHTML = html;
}}

// ── Sort ────────────────────────────────────────────────────
function toggleSort(field) {{
  if (sortField === field) {{
    if (sortDir === 1) {{ sortDir = -1; }}
    else if (sortDir === -1) {{ sortDir = 0; sortField = null; }}
    else {{ sortDir = 1; }}
  }} else {{
    sortField = field; sortDir = 1;
  }}
  applyFilters();
}}

function sortFiltered() {{
  if (!sortField || sortDir === 0) return;
  var f = sortField, d = sortDir;
  filtered.sort(function(a, b) {{
    var av = String(a[f]||'').toLowerCase();
    var bv = String(b[f]||'').toLowerCase();
    return av < bv ? -d : av > bv ? d : 0;
  }});
}}

// ── WHERE parser ────────────────────────────────────────────
var TK = {{IDENT:'I',STR:'S',EQ:'=',NEQ:'!=',LIKE:'L',AND:'&',OR:'|',NOT:'!',LP:'(',RP:')',EOF:'E'}};

function tokenize(s) {{
  var tok = [], i = 0;
  while (i < s.length) {{
    if (/\s/.test(s[i])) {{ i++; continue; }}
    if (s[i]==='(' ) {{ tok.push({{t:TK.LP }});          i++;   continue; }}
    if (s[i]===')' ) {{ tok.push({{t:TK.RP }});          i++;   continue; }}
    if (s[i]==='!'&&s[i+1]==='=') {{ tok.push({{t:TK.NEQ}}); i+=2; continue; }}
    if (s[i]==='=' ) {{ tok.push({{t:TK.EQ }});          i++;   continue; }}
    if (s[i]==='"' ) {{
      var j=i+1; while(j<s.length&&s[j]!=='"')j++;
      tok.push({{t:TK.STR,v:s.slice(i+1,j)}});  i=j+1; continue;
    }}
    var j=i; while(j<s.length&&/[\w.]/.test(s[j]))j++;
    var w=s.slice(i,j).toUpperCase();
    if      (w==='AND')  tok.push({{t:TK.AND}});
    else if (w==='OR')   tok.push({{t:TK.OR}});
    else if (w==='NOT')  tok.push({{t:TK.NOT}});
    else if (w==='LIKE') tok.push({{t:TK.LIKE}});
    else                 tok.push({{t:TK.IDENT,v:s.slice(i,j).toLowerCase()}});
    i=j;
  }}
  tok.push({{t:TK.EOF}}); return tok;
}}

function mkParser(tokens) {{
  var pos=0;
  function peek()    {{ return tokens[pos]; }}
  function consume() {{ return tokens[pos++]; }}
  function parseOr() {{
    var left=parseAnd();
    while(peek().t===TK.OR) {{ consume(); var r=parseAnd(); (function(l,rr){{left=function(x){{return l(x)||rr(x);}};}})(left,r); }}
    return left;
  }}
  function parseAnd() {{
    var left=parseNot();
    while(peek().t===TK.AND) {{ consume(); var r=parseNot(); (function(l,rr){{left=function(x){{return l(x)&&rr(x);}};}})(left,r); }}
    return left;
  }}
  function parseNot() {{
    if(peek().t===TK.NOT) {{ consume(); var inner=parsePrimary(); return function(x){{return !inner(x);}};}}
    return parsePrimary();
  }}
  function parsePrimary() {{
    if(peek().t===TK.LP) {{ consume(); var e=parseOr(); if(peek().t===TK.RP)consume(); return e; }}
    var field=consume().v||'';
    var op=consume().t;
    var val=(consume().v||'').toLowerCase();
    if(op===TK.EQ)   return function(r){{return String(r[field]||'').toLowerCase()===val;}};
    if(op===TK.NEQ)  return function(r){{return String(r[field]||'').toLowerCase()!==val;}};
    if(op===TK.LIKE) {{
      var pat=val.replace(/[.+^${{}}()|[\]\\\\]/g,'\\\\$&').replace(/%/g,'.*').replace(/_/g,'.');
      var re=new RegExp('^'+pat+'$');
      return function(r){{return re.test(String(r[field]||'').toLowerCase());}};
    }}
    return function(){{return true;}};
  }}
  return parseOr;
}}

function compileWhere(query) {{
  if(!query.trim()) return null;
  try {{
    var tok=tokenize(query);
    return mkParser(tok)();
  }} catch(e) {{ return 'error'; }}
}}

function applyWhere() {{
  var q = document.getElementById('where').value;
  var err = document.getElementById('where-err');
  compiledWhere = compileWhere(q);
  err.textContent = (compiledWhere==='error') ? '⚠ Ошибка синтаксиса' : '';
  applyFilters();
}}

// ── Export CSV ───────────────────────────────────────────────
function exportCSV() {{
  var cols = ['shorthost','os_name','owner','division','ke_type','family','status','reason'];
  var lines = [cols.join(',')];
  filtered.forEach(function(r) {{
    lines.push(cols.map(function(c) {{
      var v=String(r[c]||'');
      if(v.indexOf(',')>-1||v.indexOf('"')>-1||v.indexOf('\\n')>-1)
        v='"'+v.replace(/"/g,'""')+'"';
      return v;
    }}).join(','));
  }});
  var blob=new Blob(['\\uFEFF'+lines.join('\\n')],{{type:'text/csv;charset=utf-8;'}});
  var url=URL.createObjectURL(blob);
  var a=document.createElement('a'); a.href=url; a.download='os_compliance_filtered.csv'; a.click();
  URL.revokeObjectURL(url);
}}

// ── Render ───────────────────────────────────────────────────
function render() {{
  var tbody = document.getElementById('tbody');
  var start = (currentPage-1)*pageSize;
  var page  = filtered.slice(start, start+pageSize);
  if(filtered.length===0) {{
    tbody.innerHTML='<tr><td colspan="8" class="empty">Ничего не найдено</td></tr>';
  }} else {{
    tbody.innerHTML=page.map(function(r) {{
      return '<tr class="'+ROW_CLASS[r.status]+'">' +
        '<td class="host">'+esc(r.shorthost)+'</td>' +
        '<td class="os">'+esc(r.os_name)+'</td>' +
        '<td class="own">'+esc(r.owner)+'</td>' +
        '<td class="div">'+esc(r.division||'—')+'</td>' +
        '<td class="ke">'+esc(r.ke_type)+'</td>' +
        '<td class="fam">'+esc(FAMILY_LABEL[r.family]||r.family)+'</td>' +
        '<td>'+BADGE[r.status]+'</td>' +
        '<td class="reason">'+esc(r.reason)+'</td>' +
        '</tr>';
    }}).join('');
  }}
  renderHeaders();
  renderPagination();
}}

function renderPagination() {{
  var total=filtered.length;
  var totalPages=Math.max(1,Math.ceil(total/pageSize));
  var start=total===0?0:(currentPage-1)*pageSize+1;
  var end=Math.min(currentPage*pageSize,total);
  document.getElementById('pag-info').textContent='Показано '+start+'–'+end+' из '+total;
  var html='';
  html+='<button class="pag-btn" onclick="goTo(1)" '+(currentPage===1?'disabled':'')+'>&laquo;</button>';
  html+='<button class="pag-btn" onclick="goTo('+(currentPage-1)+')" '+(currentPage===1?'disabled':'')+'>&lsaquo;</button>';
  var pages=pagesToShow(currentPage,totalPages);
  var prev=null;
  pages.forEach(function(p) {{
    if(prev!==null&&p-prev>1) html+='<span class="pag-ellipsis">…</span>';
    html+='<button class="pag-btn'+(p===currentPage?' active':'')+'" onclick="goTo('+p+')">'+p+'</button>';
    prev=p;
  }});
  html+='<button class="pag-btn" onclick="goTo('+(currentPage+1)+')" '+(currentPage===totalPages?'disabled':'')+'>&rsaquo;</button>';
  html+='<button class="pag-btn" onclick="goTo('+totalPages+')" '+(currentPage===totalPages?'disabled':'')+'>&raquo;</button>';
  document.getElementById('pag-controls').innerHTML=html;
}}

function pagesToShow(cur,total) {{
  var pages=[],delta=2;
  for(var p=1;p<=total;p++) {{
    if(p===1||p===total||(p>=cur-delta&&p<=cur+delta)) pages.push(p);
  }}
  return pages;
}}

function goTo(p) {{
  var totalPages=Math.max(1,Math.ceil(filtered.length/pageSize));
  currentPage=Math.max(1,Math.min(p,totalPages));
  render();
  window.scrollTo({{top:0,behavior:'smooth'}});
}}

function esc(s) {{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

// ── Filter logic ─────────────────────────────────────────────
function applyFilters() {{
  var q   = (document.getElementById('search').value||'').toLowerCase();
  var div = document.getElementById('div-sel').value;
  var own = document.getElementById('owner-sel').value;
  var wh  = (compiledWhere && compiledWhere!=='error') ? compiledWhere : null;
  filtered = DATA.filter(function(r) {{
    if(activeStatus!=='ALL' && r.status!==activeStatus) return false;
    if(activeFamily!=='ALL' && r.family!==activeFamily) return false;
    if(div && r.division!==div) return false;
    if(own && r.owner!==own)    return false;
    if(q  && !(r.shorthost+r.os_name+r.owner+r.division+r.reason).toLowerCase().includes(q)) return false;
    if(wh && !wh(r))            return false;
    return true;
  }});
  sortFiltered();
  currentPage=1;
  render();
}}

function setStatus(btn) {{
  document.querySelectorAll('.filter-btn[data-status]').forEach(function(b){{b.classList.remove('active');}});
  btn.classList.add('active');
  activeStatus=btn.dataset.status;
  applyFilters();
}}

function filterByStatus(status) {{
  activeStatus=status;
  document.querySelectorAll('.filter-btn[data-status]').forEach(function(b){{
    b.classList.toggle('active',b.dataset.status===status);
  }});
  applyFilters();
}}

function setFamily(btn) {{
  document.querySelectorAll('.filter-btn[data-fam]').forEach(function(b){{b.classList.remove('active');}});
  btn.classList.add('active');
  activeFamily=btn.dataset.fam;
  applyFilters();
}}

function filterByFamily(fam) {{
  activeFamily=fam;
  document.querySelectorAll('.filter-btn[data-fam]').forEach(function(b){{
    b.classList.toggle('active',b.dataset.fam===fam);
  }});
  applyFilters();
}}

function changePageSize(val) {{
  pageSize=parseInt(val); currentPage=1; render();
}}

// ── Boot ─────────────────────────────────────────────────────
initDropdowns();
renderHeaders();
applyFilters();
</script>
</body>
</html>
"""
```

- [ ] **Step 6.5: Run new HTML tests GREEN**

```
python -m pytest tests/test_cmdb_os_compliance.py -k "html_includes_division or html_has_os_family or html_has_export" -v
```
Expected: 3 PASSED

- [ ] **Step 6.6: Full suite**

```
python -m pytest tests/test_cmdb_os_compliance.py -q
```
Expected: all passed (no regressions)

- [ ] **Step 6.7: Commit**

```bash
git add vcenter_cmdb/cmdb_os_compliance.py tests/test_cmdb_os_compliance.py
git commit -m "feat: rewrite HTML template with division column, OS family/division/owner filters, sort, export, WHERE"
```

---

## Task 7: Update console table — add division column

**Files:**
- Modify: `vcenter_cmdb/cmdb_os_compliance.py`

Minor cosmetic fix so the terminal output isn't broken by the new field.

- [ ] **Step 7.1: Update `print_console_table`**

Replace `print_console_table`:

```python
def print_console_table(rows: list[ReportRow], summary: dict[str, int]) -> None:
    COL = [30, 45, 28, 22, 10, 14]
    header = ["shorthost", "os_name", "owner", "division", "ke_type", "status"]
    sep = "-" * (sum(COL) + len(COL) * 2 + 1)
    print(sep)
    print("  ".join(h.ljust(w) for h, w in zip(header, COL)))
    print(sep)
    for r in rows:
        cells = [
            r.shorthost[:COL[0]], r.os_name[:COL[1]], r.owner[:COL[2]],
            (r.division or "")[:COL[3]], r.ke_type[:COL[4]], r.status,
        ]
        print("  ".join(str(c).ljust(w) for c, w in zip(cells, COL)))
    print(sep)
    print(f"\nИтого: {summary['total']}  |  OK: {summary['OK']}  "
          f"WARNING: {summary['WARNING']}  NON_COMPLIANT: {summary['NON_COMPLIANT']}  "
          f"UNKNOWN: {summary['UNKNOWN']}")
```

- [ ] **Step 7.2: Full suite still green**

```
python -m pytest tests/test_cmdb_os_compliance.py -q
```

- [ ] **Step 7.3: Commit**

```bash
git add vcenter_cmdb/cmdb_os_compliance.py
git commit -m "feat: add division column to console table output"
```

---

## Final Verification

- [ ] **Run full test suite**

```
python -m pytest tests/test_cmdb_os_compliance.py -v
```
Expected: all tests PASSED, no failures, no errors.

- [ ] **Smoke-test HTML generation**

```python
python -c "
from pathlib import Path
from vcenter_cmdb.cmdb_os_compliance import ReportRow, Status, write_html, summarize
rows = [
    ReportRow('srv01','ubuntu 22.04','IT-A','HOST',Status.OK,'OK',division='04. дів. Урал',family='linux'),
    ReportRow('vm01','windows server 2019|','IT-B','VM',Status.WARNING,'WARN',division='05. дів. Юг',family='windows_server'),
    ReportRow('vm02','windows 10|','','VM',Status.NON_COMPLIANT,'BAD',division='',family='windows_client'),
]
s = summarize(rows)
out = Path('smoke_test.html')
write_html(rows, s, out)
print('OK -', out, out.stat().st_size, 'bytes')
"
```
Expected: `OK - smoke_test.html <N> bytes` where N > 50000

- [ ] **Push**

```bash
git push
```
