"""Tests for cmdb_os_compliance.py — TDD RED phase."""
import csv
import io
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vcenter_cmdb.cmdb_os_compliance import (
    CmdbAuthError,
    CmdbError,
    ClassificationResult,
    Config,
    HostRecord,
    ReportRow,
    Status,
    build_inventory,
    build_report,
    classify_os,
    extract_attrs,
    load_config,
    os_name_of,
    owner_of,
    shorthost_of,
    summarize,
    write_csv,
    write_html,
)



# ============================================================
# 1. Config / load_config
# ============================================================

def test_load_config_from_env(monkeypatch):
    monkeypatch.setenv("CMDB_URL", "https://cmdb.example.com")
    monkeypatch.setenv("CMDB_TOKEN", "mytoken123")
    cfg = load_config([])
    assert cfg.cmdb_url == "https://cmdb.example.com"
    assert cfg.token == "mytoken123"
    assert cfg.page_size == 500
    assert cfg.verify_ssl is False


def test_load_config_cli_overrides_env(monkeypatch):
    monkeypatch.setenv("CMDB_URL", "https://cmdb.example.com")
    monkeypatch.setenv("CMDB_TOKEN", "envtoken")
    cfg = load_config(["--token", "clitoken", "--page-size", "100"])
    assert cfg.token == "clitoken"
    assert cfg.page_size == 100


def test_load_config_missing_url_raises(monkeypatch):
    monkeypatch.delenv("CMDB_URL", raising=False)
    monkeypatch.setenv("CMDB_TOKEN", "tok")
    with pytest.raises(SystemExit):
        load_config([])


def test_load_config_missing_token_raises(monkeypatch):
    monkeypatch.setenv("CMDB_URL", "https://cmdb.example.com")
    monkeypatch.delenv("CMDB_TOKEN", raising=False)
    with pytest.raises(SystemExit):
        load_config([])


# ============================================================
# 2. OS Classifier
# ============================================================

@pytest.mark.parametrize("os_name, expected_status, expected_family", [
    # --- Windows Client OK ---
    ("майкрософт windows 11 pro|25h2",             Status.OK,            "windows_client"),
    ("майкрософт windows 11 pro|24h2",             Status.OK,            "windows_client"),
    ("майкрософт windows 11 pro|23h2",             Status.OK,            "windows_client"),
    ("Microsoft Windows 11 Pro|23H2",              Status.OK,            "windows_client"),
    # --- Windows Client WARNING ---
    ("майкрософт windows 11 pro|22h2",             Status.WARNING,       "windows_client"),
    ("майкрософт windows 11 pro|",                 Status.WARNING,       "windows_client"),
    ("windows 11 enterprise|21h2",                 Status.WARNING,       "windows_client"),
    # --- Windows Client NON_COMPLIANT ---
    ("майкрософт windows 10 pro|22h2",             Status.NON_COMPLIANT, "windows_client"),
    ("windows 10 enterprise ltsc|21h2",            Status.NON_COMPLIANT, "windows_client"),
    ("windows 7 professional|sp1",                 Status.NON_COMPLIANT, "windows_client"),
    ("windows 8.1|",                               Status.NON_COMPLIANT, "windows_client"),
    # --- Windows Server OK ---
    ("майкрософт windows server 2022 standard|",   Status.OK,            "windows_server"),
    ("microsoft windows server 2022 datacenter|",  Status.OK,            "windows_server"),
    ("microsoft windows server 2025 datacenter|",  Status.OK,            "windows_server"),
    ("майкрософт windows server 2022|",            Status.OK,            "windows_server"),
    # --- Windows Server WARNING ---
    ("microsoft windows server 2019 standard|",    Status.WARNING,       "windows_server"),
    ("майкрософт windows server 2019|",            Status.WARNING,       "windows_server"),
    # --- Windows Server NON_COMPLIANT ---
    ("microsoft windows server 2016 standard|",    Status.NON_COMPLIANT, "windows_server"),
    ("microsoft windows server 2012 r2|",          Status.NON_COMPLIANT, "windows_server"),
    ("microsoft windows server 2008 r2|",          Status.NON_COMPLIANT, "windows_server"),
    # --- Ubuntu OK ---
    ("ubuntu 22.04 lts|22.04.3 lts (jammy)",       Status.OK,            "linux"),
    ("ubuntu 24.04 lts|24.04 lts (noble)",         Status.OK,            "linux"),
    ("ubuntu 22.04.5 lts|...",                     Status.OK,            "linux"),
    # --- Ubuntu NON_COMPLIANT ---
    ("ubuntu 20.04 lts|20.04 lts (focal)",         Status.NON_COMPLIANT, "linux"),
    ("ubuntu 16.04.7 lts|16.04.7 lts (xenial)",    Status.NON_COMPLIANT, "linux"),
    ("ubuntu 23.10|23.10 (mantic)",                Status.NON_COMPLIANT, "linux"),
    ("ubuntu 21.10|mantic",                        Status.NON_COMPLIANT, "linux"),
    # --- Debian ---
    ("debian gnu/linux 12|bookworm",               Status.OK,            "linux"),
    ("debian gnu/linux 13|trixie",                 Status.OK,            "linux"),
    ("debian gnu/linux 11|bullseye",               Status.NON_COMPLIANT, "linux"),
    ("debian 10|buster",                           Status.NON_COMPLIANT, "linux"),
    # --- AlmaLinux ---
    ("almalinux 9|9.4",                            Status.OK,            "linux"),
    ("alma linux 10|10.0",                         Status.OK,            "linux"),
    ("almalinux 8|8.9",                            Status.NON_COMPLIANT, "linux"),
    # --- RHEL ---
    ("red hat enterprise linux 9|9.3",             Status.OK,            "linux"),
    ("rhel 9.4|",                                  Status.OK,            "linux"),
    ("red hat enterprise linux 7|7.9",             Status.NON_COMPLIANT, "linux"),
    ("rhel 8|8.9",                                 Status.NON_COMPLIANT, "linux"),
    # --- CentOS ---
    ("centos linux 7|7.9.2009 (core)",             Status.NON_COMPLIANT, "linux"),
    ("centos stream 9|",                           Status.NON_COMPLIANT, "linux"),
    # --- Edge cases ---
    (None,                                          Status.UNKNOWN,       "unknown"),
    ("",                                            Status.UNKNOWN,       "unknown"),
    ("freebsd 13|13.2-release",                    Status.NON_COMPLIANT, "unknown"),
    ("solaris 11|",                                Status.NON_COMPLIANT, "unknown"),
])
def test_classify_os(os_name, expected_status, expected_family):
    result = classify_os(os_name)
    assert result.status == expected_status, (
        f"os_name={os_name!r}: got status={result.status!r}, expected={expected_status!r}. "
        f"reason={result.reason!r}"
    )
    assert result.family == expected_family, (
        f"os_name={os_name!r}: got family={result.family!r}, expected={expected_family!r}"
    )


# ============================================================
# 3. CItem parsers
# ============================================================

def _make_ci(attrs: dict[str, str]) -> dict:
    """Build a minimal CItem dict from {attr_name: bvalue}."""
    return {
        "uuid": "aaa-111",
        "name": "test-host",
        "attrs": [
            {
                "uuid": f"attr-{k}",
                "attr_type_uuid": f"type-{k}",
                "bvalue": v,
                "type": {"uuid": f"type-{k}", "name": k, "type": "string"},
            }
            for k, v in attrs.items()
        ],
    }


def test_extract_attrs_basic():
    ci = _make_ci({"os_name": "ubuntu 22.04 lts|...", "shorthost": "srv01"})
    attrs = extract_attrs(ci)
    assert attrs["os_name"] == "ubuntu 22.04 lts|..."
    assert attrs["shorthost"] == "srv01"


def test_extract_attrs_skips_empty_bvalue():
    ci = _make_ci({"os_name": "", "shorthost": "srv01"})
    attrs = extract_attrs(ci)
    assert "os_name" not in attrs
    assert attrs["shorthost"] == "srv01"


def test_extract_attrs_no_attrs_field():
    ci = {"uuid": "x", "name": "y", "attrs": None}
    assert extract_attrs(ci) == {}


def test_shorthost_of_present():
    ci = _make_ci({"shorthost": "SRV01"})
    assert shorthost_of(ci) == "srv01"


def test_shorthost_of_missing():
    ci = _make_ci({"os_name": "ubuntu 22.04"})
    assert shorthost_of(ci) is None


def test_os_name_of_present():
    ci = _make_ci({"os_name": "ubuntu 22.04 lts|jammy", "shorthost": "s1"})
    assert os_name_of(ci) == "ubuntu 22.04 lts|jammy"


def test_os_name_of_missing():
    ci = _make_ci({"shorthost": "s1"})
    assert os_name_of(ci) is None


def test_owner_of_both_fields():
    ci = _make_ci({"owner": "IT-группа Сириус", "owner_person": "Ivanov.AA", "shorthost": "s1"})
    assert owner_of(ci) == "IT-группа Сириус / Ivanov.AA"


def test_owner_of_only_owner():
    ci = _make_ci({"owner": "IT-группа Сириус", "shorthost": "s1"})
    assert owner_of(ci) == "IT-группа Сириус"


def test_owner_of_missing():
    ci = _make_ci({"shorthost": "s1"})
    assert owner_of(ci) is None


# ============================================================
# 4. Inventory aggregation
# ============================================================

def _ci(shorthost: str, os_name: str | None, owner: str | None = None) -> dict:
    attrs = {"shorthost": shorthost}
    if os_name:
        attrs["os_name"] = os_name
    if owner:
        attrs["owner"] = owner
    return _make_ci(attrs)


def test_build_inventory_host_only():
    hosts = [_ci("srv01", "ubuntu 22.04 lts|...", "IT-группа A")]
    inv = build_inventory(hosts, [])
    assert "srv01" in inv
    assert inv["srv01"].sources == {"HOST"}
    assert inv["srv01"].os_name == "ubuntu 22.04 lts|..."
    assert inv["srv01"].owner == "IT-группа A"


def test_build_inventory_vm_only():
    vms = [_ci("vm01", "windows server 2022|", "IT-группа B")]
    inv = build_inventory([], vms)
    assert "vm01" in inv
    assert inv["vm01"].sources == {"VM"}
    assert inv["vm01"].owner == "IT-группа B"


def test_build_inventory_host_priority():
    hosts = [_ci("srv01", "ubuntu 22.04 lts|host", "HOST-owner")]
    vms   = [_ci("srv01", "ubuntu 20.04 lts|vm", "VM-owner")]
    inv = build_inventory(hosts, vms)
    assert inv["srv01"].os_name == "ubuntu 22.04 lts|host"
    assert inv["srv01"].owner == "HOST-owner"
    assert inv["srv01"].sources == {"HOST", "VM"}
    assert inv["srv01"].ke_type == "HOST+VM"


def test_build_inventory_case_insensitive_merge():
    hosts = [_ci("SRV01", "ubuntu 22.04 lts|...")]
    vms   = [_ci("srv01", "windows 10|...")]
    inv = build_inventory(hosts, vms)
    assert len(inv) == 1
    assert list(inv.keys())[0] == "srv01"


def test_build_inventory_skips_no_shorthost():
    hosts = [_ci("", "ubuntu 22.04 lts|...")]
    inv = build_inventory(hosts, [])
    assert len(inv) == 0


# ============================================================
# 5. Reporting
# ============================================================

def _make_inventory(entries: list[tuple]) -> dict[str, HostRecord]:
    result = {}
    for entry in entries:
        sh, osn, src = entry[0], entry[1], entry[2]
        own = entry[3] if len(entry) > 3 else None
        result[sh] = HostRecord(shorthost=sh, os_name=osn, owner=own, sources=src)
    return result


def test_summarize_counts():
    rows = [
        ReportRow("h1", "...", "", "HOST", Status.OK,            "ok"),
        ReportRow("h2", "...", "", "VM",   Status.NON_COMPLIANT, "bad"),
        ReportRow("h3", "...", "", "HOST", Status.WARNING,       "warn"),
        ReportRow("h4", "...", "", "VM",   Status.NON_COMPLIANT, "bad2"),
    ]
    s = summarize(rows)
    assert s["total"] == 4
    assert s["OK"] == 1
    assert s["WARNING"] == 1
    assert s["NON_COMPLIANT"] == 2


def test_build_report_sort_order():
    inv = _make_inventory([
        ("z-host", "ubuntu 22.04 lts|...", {"HOST"}),
        ("a-host", "windows 10 pro|22h2",  {"VM"}),
        ("m-host", "windows server 2019|", {"HOST"}),
    ])
    rows = build_report(inv)
    nc_idx   = next(i for i, r in enumerate(rows) if r.status == Status.NON_COMPLIANT)
    warn_idx = next(i for i, r in enumerate(rows) if r.status == Status.WARNING)
    ok_idx   = next(i for i, r in enumerate(rows) if r.status == Status.OK)
    assert nc_idx < warn_idx < ok_idx


def test_build_report_includes_owner():
    inv = _make_inventory([
        ("srv01", "ubuntu 22.04 lts|...", {"HOST"}, "IT-группа Сириус"),
    ])
    rows = build_report(inv)
    assert rows[0].owner == "IT-группа Сириус"


def test_write_csv_roundtrip(tmp_path):
    rows = [
        ReportRow("srv01", "ubuntu 22.04 lts|джамми", "IT-группа A", "HOST", Status.OK, "ok"),
        ReportRow("vm01",  "майкрософт windows 10|22h2", "", "VM", Status.NON_COMPLIANT, "bad"),
    ]
    out = tmp_path / "report.csv"
    write_csv(rows, out)
    content = out.read_text(encoding="utf-8-sig")
    assert "srv01" in content
    assert "джамми" in content
    assert "майкрософт" in content
    assert "IT-группа A" in content


def test_write_html_creates_file(tmp_path):
    rows = [
        ReportRow("srv01", "ubuntu 22.04 lts|...", "IT-группа A / Ivanov.AA", "HOST", Status.OK, "OK: Ubuntu 22.04 LTS"),
        ReportRow("vm01",  "майкрософт windows 10|22h2", "IT-группа B", "VM", Status.NON_COMPLIANT, "NON_COMPLIANT: Windows 10"),
    ]
    summary = {"total": 2, "OK": 1, "WARNING": 0, "NON_COMPLIANT": 1, "UNKNOWN": 0}
    out = tmp_path / "report.html"
    write_html(rows, summary, out)
    content = out.read_text(encoding="utf-8")
    assert "srv01" in content
    assert "IT-группа A" in content
    assert "Ivanov.AA" in content
    assert "NON_COMPLIANT" in content
    assert "<table" in content


# ============================================================
# 6. Division resolution helpers
# ============================================================

from vcenter_cmdb.cmdb_os_compliance import (
    branch_number_from_host,
    build_branch_maps,
    ref_uuids_of,
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
