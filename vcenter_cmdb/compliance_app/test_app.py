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
