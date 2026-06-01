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
