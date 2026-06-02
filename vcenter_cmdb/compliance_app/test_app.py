"""Tests for compliance_app/app.py helpers."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
import app as app_module
from cmdb_os_compliance import ReportRow, Status


def _row(shorthost="srv01", os_name="ubuntu 22.04", owner="IT / Ivanov.AA",
         ke_type="HOST", status=Status.OK, reason="OK", division="04. дів. Урал",
         family="linux") -> ReportRow:
    return ReportRow(shorthost=shorthost, os_name=os_name, owner=owner,
                     ke_type=ke_type, status=status, reason=reason,
                     division=division, family=family)


@pytest.fixture(autouse=True)
def mock_rows(monkeypatch):
    rows = [
        _row("srv01", status=Status.OK,            family="linux",          division="04. дів. Урал"),
        _row("vm01",  status=Status.NON_COMPLIANT, family="windows_client", division="05. дів. Юг"),
        _row("db01",  status=Status.WARNING,       family="windows_server", division="04. дів. Урал"),
        _row("pc01",  status=Status.NON_COMPLIANT, family="windows_client", division=""),
    ]
    monkeypatch.setattr(app_module, "_rows", rows)
    monkeypatch.setattr(app_module, "_summary", {"total": 4, "OK": 1, "WARNING": 1, "NON_COMPLIANT": 2, "UNKNOWN": 0})
    monkeypatch.setattr(app_module, "_divisions", ["04. дів. Урал", "05. дів. Юг"])


# ---- _filter_rows ----

def test_filter_by_status():
    result = app_module._filter_rows({"status": "NON_COMPLIANT"})
    assert len(result) == 2
    assert all(r.status == Status.NON_COMPLIANT for r in result)


def test_filter_by_family():
    result = app_module._filter_rows({"family": "linux"})
    assert len(result) == 1
    assert result[0].shorthost == "srv01"


def test_filter_by_division():
    result = app_module._filter_rows({"division": "04. дів. Урал"})
    assert len(result) == 2


def test_filter_by_text_search():
    result = app_module._filter_rows({"q": "srv"})
    assert len(result) == 1
    assert result[0].shorthost == "srv01"


def test_filter_no_params_returns_all():
    result = app_module._filter_rows({})
    assert len(result) == 4


# ---- _sort_rows ----

def test_sort_asc():
    rows = app_module._rows
    result = app_module._sort_rows(rows, "shorthost", "asc")
    assert result[0].shorthost == "db01"
    assert result[-1].shorthost == "vm01"


def test_sort_desc():
    rows = app_module._rows
    result = app_module._sort_rows(rows, "shorthost", "desc")
    assert result[0].shorthost == "vm01"


def test_sort_none_returns_unchanged():
    rows = app_module._rows
    assert app_module._sort_rows(rows, "", "asc") is rows


# ---- API routes ----

@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


def test_stats_route(client):
    r = client.get("/api/stats")
    assert r.status_code == 200
    data = r.get_json()
    assert data["total"] == 4
    assert data["OK"] == 1
    assert data["NON_COMPLIANT"] == 2


def test_divisions_route(client):
    r = client.get("/api/divisions")
    assert r.status_code == 200
    data = r.get_json()
    assert "04. дів. Урал" in data["divisions"]


def test_data_route_default(client):
    r = client.get("/api/data")
    assert r.status_code == 200
    data = r.get_json()
    assert data["total"] == 4
    assert data["page"] == 1
    assert len(data["data"]) == 4


def test_data_route_filter(client):
    r = client.get("/api/data?status=NON_COMPLIANT")
    data = r.get_json()
    assert data["total"] == 2
    assert all(row["status"] == "NON_COMPLIANT" for row in data["data"])


def test_data_route_pagination(client):
    r = client.get("/api/data?size=2&page=2")
    data = r.get_json()
    assert data["page"] == 2
    assert data["pages"] == 2
    assert len(data["data"]) == 2


def test_export_route(client):
    r = client.get("/api/export?status=OK")
    assert r.status_code == 200
    assert "text/csv" in r.content_type
    text = r.data.decode("utf-8-sig")
    assert "shorthost" in text
    assert "srv01" in text


def test_index_route(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"CMDB" in r.data


# ============================================================
# Snapshot persistence
# ============================================================
import json as _json
from pathlib import Path


@pytest.fixture
def snap_dir(tmp_path, monkeypatch):
    """Point SNAPSHOTS_DIR at a temp dir for isolation."""
    monkeypatch.setattr(app_module, "SNAPSHOTS_DIR", tmp_path)
    return tmp_path


def test_save_snapshot_creates_file(snap_dir):
    snap_id = app_module.save_snapshot(app_module._rows, source="cmdb")
    files = list(snap_dir.glob("*.json"))
    assert len(files) == 1
    data = _json.loads(files[0].read_text(encoding="utf-8"))
    assert data["id"] == snap_id
    assert data["source"] == "cmdb"
    assert data["summary"]["total"] == 4
    assert "srv01" in data["hosts"]


def test_list_snapshots_returns_sorted(snap_dir):
    app_module.save_snapshot(app_module._rows, source="cmdb")
    import time; time.sleep(0.02)
    app_module.save_snapshot(app_module._rows, source="csv")
    snaps = app_module.list_snapshots()
    assert len(snaps) == 2
    assert snaps[0]["timestamp"] > snaps[1]["timestamp"]   # newest first
    assert "hosts" not in snaps[0]                          # no hosts in list


def test_load_snapshot_has_hosts(snap_dir):
    snap_id = app_module.save_snapshot(app_module._rows, source="cmdb")
    data = app_module.load_snapshot(snap_id)
    assert "hosts" in data
    assert data["hosts"]["srv01"]["status"] == "OK"


# ============================================================
# CSV import + compare
# ============================================================

CSV_CONTENT = (
    "shorthost,os_name,owner,division,ke_type,family,status,reason\r\n"
    "srv01,ubuntu 22.04,IT / A,04. дів. Урал,HOST,linux,OK,OK: Ubuntu\r\n"
    "vm01,windows 10|22h2,IT / B,05. дів. Юг,VM,windows_client,NON_COMPLIANT,NON_COMPLIANT: Win10\r\n"
)


def test_import_csv_snapshot(snap_dir):
    snap_id = app_module.import_csv_snapshot(
        CSV_CONTENT.encode("utf-8-sig"), "os_compliance_report_20260527.csv"
    )
    data = app_module.load_snapshot(snap_id)
    assert data["source"] == "csv"
    assert "srv01" in data["hosts"]
    assert data["hosts"]["vm01"]["status"] == "NON_COMPLIANT"
    assert data["summary"]["total"] == 2


def test_import_csv_extracts_date_from_filename(snap_dir):
    snap_id = app_module.import_csv_snapshot(
        CSV_CONTENT.encode("utf-8"), "os_compliance_report_20260527.csv"
    )
    data = app_module.load_snapshot(snap_id)
    assert "2026-05-27" in data["timestamp"]


def test_compare_snapshots_detects_worsened():
    snap_a = {
        "id": "a", "timestamp": "2026-05-27T00:00:00",
        "hosts": {"srv01": {"status": "OK", "os_name": "u22", "owner": "", "division": "", "reason": ""}},
    }
    snap_b = {
        "id": "b", "timestamp": "2026-06-01T00:00:00",
        "hosts": {"srv01": {"status": "NON_COMPLIANT", "os_name": "u22", "owner": "", "division": "", "reason": "bad"}},
    }
    diff = app_module.compare_snapshots(snap_a, snap_b)
    assert len(diff["changed"]) == 1
    assert diff["changed"][0]["direction"] == "worsened"
    assert diff["changed"][0]["status_from"] == "OK"
    assert diff["changed"][0]["status_to"] == "NON_COMPLIANT"


def test_compare_snapshots_detects_improved():
    snap_a = {"id":"a","timestamp":"","hosts":{"h1":{"status":"NON_COMPLIANT","os_name":"","owner":"","division":"","reason":""}}}
    snap_b = {"id":"b","timestamp":"","hosts":{"h1":{"status":"OK","os_name":"","owner":"","division":"","reason":""}}}
    diff = app_module.compare_snapshots(snap_a, snap_b)
    assert diff["changed"][0]["direction"] == "improved"


def test_compare_snapshots_detects_new_and_removed():
    snap_a = {"id":"a","timestamp":"","hosts":{"old":{"status":"OK","os_name":"","owner":"","division":"","reason":""}}}
    snap_b = {"id":"b","timestamp":"","hosts":{"new_host":{"status":"OK","os_name":"","owner":"","division":"","reason":""}}}
    diff = app_module.compare_snapshots(snap_a, snap_b)
    assert any(h["shorthost"] == "new_host" for h in diff["new"])
    assert any(h["shorthost"] == "old"      for h in diff["removed"])


# ============================================================
# New API routes — snapshots, trend, compare, import
# ============================================================
import io


def test_snapshots_route_empty(client, snap_dir):
    r = client.get("/api/snapshots")
    assert r.status_code == 200
    assert r.get_json() == []


def test_snapshots_route_after_save(client, snap_dir):
    app_module.save_snapshot(app_module._rows, source="cmdb")
    r = client.get("/api/snapshots")
    data = r.get_json()
    assert len(data) == 1
    assert data[0]["source"] == "cmdb"
    assert "hosts" not in data[0]


def test_trend_route(client, snap_dir):
    app_module.save_snapshot(app_module._rows, source="cmdb")
    r = client.get("/api/trend")
    data = r.get_json()
    assert "snapshots" in data
    assert len(data["snapshots"]) == 1


def test_compare_route(client, snap_dir):
    id_a = app_module.save_snapshot(app_module._rows, source="cmdb")
    import time; time.sleep(0.02)
    from cmdb_os_compliance import ReportRow, Status
    rows_b = list(app_module._rows)
    rows_b[0] = ReportRow(rows_b[0].shorthost, rows_b[0].os_name, rows_b[0].owner,
                           rows_b[0].ke_type, Status.NON_COMPLIANT, "bad",
                           rows_b[0].division, rows_b[0].family)
    id_b = app_module.save_snapshot(rows_b, source="cmdb")
    r = client.get(f"/api/compare?a={id_a}&b={id_b}")
    assert r.status_code == 200
    data = r.get_json()
    assert "diff" in data
    assert len(data["diff"]["changed"]) == 1


def test_import_route(client, snap_dir):
    csv_data = (
        "shorthost,os_name,owner,division,ke_type,family,status,reason\r\n"
        "host1,ubuntu 22.04,IT,04. div,HOST,linux,OK,ok\r\n"
    ).encode("utf-8")
    r = client.post("/api/snapshots/import",
                    data={"file": (io.BytesIO(csv_data), "report_20260527.csv")},
                    content_type="multipart/form-data")
    assert r.status_code == 200
    data = r.get_json()
    assert "id" in data
    assert data["summary"]["total"] == 1


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
