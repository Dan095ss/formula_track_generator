# AD Users Dump — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Two self-contained scripts that extract all AD accounts (user, service, admin, disabled) with a defined CMDB attribute set to CSV — one for local testing, one as an Airflow DAG.

**Architecture:** Both files are self-contained (no shared module — matches project pattern). Pure helper functions are duplicated. Local script reads config from env vars. Airflow DAG reads from `airflow.models.Variable`. Both use `ldap3.extend.standard.paged_search` for large AD (500 entries/page).

**Tech Stack:** Python 3.x, ldap3, csv (stdlib), struct (stdlib), uuid (stdlib), Airflow 2.x (DAG only)

---

## Files

| File | Role |
|------|------|
| `vcenter_cmdb/ad_users_local.py` | Standalone script: env-var config, ldap3 search, CSV output |
| `vcenter_cmdb/ad_users_to_cmdb.py` | Airflow DAG: same logic, config from Airflow Variables |
| `vcenter_cmdb/tests/test_ad_helpers.py` | Unit tests for all pure helper functions |

---

## CMDB Field → AD Attribute Mapping

| CMDB field | AD attribute | Notes |
|-----------|-------------|-------|
| `sAMAccountName` | `sAMAccountName` | login |
| `UPN` | `userPrincipalName` | |
| `SID` | `objectSid` | binary → `S-1-5-...` |
| `UID` | `uid` | |
| `GUID` | `objectGUID` | binary → UUID string |
| `account_type` | `userAccountControl` | always "user" (objectCategory=person) |
| `source` | — | constant `"AD"` |
| `status` | `userAccountControl` | bit 0x2 → enabled/disabled |
| `created_at` | `whenCreated` | datetime → `%Y-%m-%d %H:%M:%S` |
| `last_password_change` | `pwdLastSet` | Windows FILETIME → datetime string |
| `DisplayName` | `displayName` | |
| `department` | `department` | |
| `position` | `title` | job title field in AD |
| `title` | `title` | same as position for now |
| `organization` | `company` | |
| `manager` | `manager` | DN → CN only |
| `location` | `extensionAttribute12` | geographic |
| `EA5` | `extensionAttribute5` | leadership level |
| `EA8` | `extensionAttribute8` | computer name |
| `EA10` | `extensionAttribute10` | UZ attributes |
| `description` | `description` | |

---

## Task 1: Helper functions + unit tests

**Files:**
- Create: `vcenter_cmdb/tests/test_ad_helpers.py`
- Create: `vcenter_cmdb/ad_users_local.py` (helpers section only)

### Step 1.1 — Write failing tests for `parse_sid`

File: `vcenter_cmdb/tests/test_ad_helpers.py`

```python
import sys
import os
import unittest

sys.modules.update({
    'ldap3': __import__('unittest.mock', fromlist=['MagicMock']).MagicMock(),
})
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestParseSid(unittest.TestCase):
    def test_everyone_sid(self):
        # S-1-1-0 (Everyone): revision=1, subcount=1, ia=1, sub=0
        sid_bytes = b'\x01\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00'
        from ad_users_local import parse_sid
        self.assertEqual(parse_sid(sid_bytes), 'S-1-1-0')

    def test_empty_returns_empty(self):
        from ad_users_local import parse_sid
        self.assertEqual(parse_sid(None), '')
        self.assertEqual(parse_sid(b''), '')

    def test_string_passthrough(self):
        from ad_users_local import parse_sid
        self.assertEqual(parse_sid('S-1-5-21-100'), 'S-1-5-21-100')
```

- [ ] Run to verify FAIL: `python -m pytest vcenter_cmdb/tests/test_ad_helpers.py::TestParseSid -v`
  Expected: `ImportError` or `ModuleNotFoundError` (ad_users_local doesn't exist yet)

### Step 1.2 — Write failing tests for `parse_guid`

Append to `vcenter_cmdb/tests/test_ad_helpers.py`:

```python
import uuid as _uuid


class TestParseGuid(unittest.TestCase):
    def test_known_guid(self):
        u = _uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
        from ad_users_local import parse_guid
        self.assertEqual(parse_guid(u.bytes_le), '6ba7b810-9dad-11d1-80b4-00c04fd430c8')

    def test_empty_returns_empty(self):
        from ad_users_local import parse_guid
        self.assertEqual(parse_guid(None), '')
        self.assertEqual(parse_guid(b''), '')
```

### Step 1.3 — Write failing tests for `parse_windows_ts`

Append to `vcenter_cmdb/tests/test_ad_helpers.py`:

```python
class TestParseWindowsTs(unittest.TestCase):
    def test_zero_returns_empty(self):
        from ad_users_local import parse_windows_ts
        self.assertEqual(parse_windows_ts(0), '')
        self.assertEqual(parse_windows_ts(None), '')

    def test_known_filetime(self):
        # FILETIME 132539328000000000 = 2021-01-01 00:00:00
        # Verify: (datetime(2021,1,1) - datetime(1601,1,1)) = 153402 days
        # 153402 * 86400 * 10_000_000 = 132539328000000000
        from ad_users_local import parse_windows_ts
        self.assertEqual(parse_windows_ts(132539328000000000), '2021-01-01 00:00:00')
```

### Step 1.4 — Write failing tests for `extract_manager_cn` and `parse_uac`

Append to `vcenter_cmdb/tests/test_ad_helpers.py`:

```python
class TestExtractManagerCn(unittest.TestCase):
    def test_standard_dn(self):
        from ad_users_local import extract_manager_cn
        dn = 'CN=John Smith,OU=Users,DC=company,DC=local'
        self.assertEqual(extract_manager_cn(dn), 'John Smith')

    def test_empty(self):
        from ad_users_local import extract_manager_cn
        self.assertEqual(extract_manager_cn(''), '')
        self.assertEqual(extract_manager_cn(None), '')


class TestParseUac(unittest.TestCase):
    def test_enabled(self):
        from ad_users_local import parse_uac
        status, account_type = parse_uac(512)   # 0x200 = NORMAL_ACCOUNT
        self.assertEqual(status, 'enabled')
        self.assertEqual(account_type, 'user')

    def test_disabled(self):
        from ad_users_local import parse_uac
        status, _ = parse_uac(514)  # 512 | 2 = NORMAL_ACCOUNT | ACCOUNTDISABLE
        self.assertEqual(status, 'disabled')

    def test_none_defaults_to_enabled(self):
        from ad_users_local import parse_uac
        status, _ = parse_uac(None)
        self.assertEqual(status, 'enabled')
```

### Step 1.5 — Write failing test for `map_entry_to_row`

Append to `vcenter_cmdb/tests/test_ad_helpers.py`:

```python
import uuid as _uuid2

class TestMapEntryToRow(unittest.TestCase):
    def _make_entry(self):
        guid = _uuid2.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
        sid = b'\x01\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00'
        attrs = {
            'sAMAccountName': 'ivanov.ia',
            'userPrincipalName': 'ivanov.ia@company.local',
            'uid': 'E12345',
            'userAccountControl': 512,
            'whenCreated': '2021-01-15 10:00:00',
            'pwdLastSet': 132539328000000000,
            'displayName': 'Ivanov Ivan',
            'department': 'IT',
            'title': 'Engineer',
            'company': 'DNS',
            'manager': 'CN=Petrov P,OU=Managers,DC=company,DC=local',
            'extensionAttribute12': 'Moscow',
            'extensionAttribute5': 'MS',
            'extensionAttribute8': 'PC-IVANOV',
            'extensionAttribute10': 'TYPE=employee',
            'description': 'Regular user',
        }
        raw_attrs = {
            'objectSid': [sid],
            'objectGUID': [guid.bytes_le],
        }
        return attrs, raw_attrs

    def test_row_keys(self):
        from ad_users_local import map_entry_to_row, CSV_COLUMNS
        attrs, raw_attrs = self._make_entry()
        row = map_entry_to_row(attrs, raw_attrs)
        for col in CSV_COLUMNS:
            self.assertIn(col, row, f"Missing column: {col}")

    def test_row_values(self):
        from ad_users_local import map_entry_to_row
        attrs, raw_attrs = self._make_entry()
        row = map_entry_to_row(attrs, raw_attrs)
        self.assertEqual(row['sAMAccountName'], 'ivanov.ia')
        self.assertEqual(row['source'], 'AD')
        self.assertEqual(row['status'], 'enabled')
        self.assertEqual(row['SID'], 'S-1-1-0')
        self.assertEqual(row['GUID'], '6ba7b810-9dad-11d1-80b4-00c04fd430c8')
        self.assertEqual(row['manager'], 'Petrov P')
        self.assertEqual(row['location'], 'Moscow')
        self.assertEqual(row['EA5'], 'MS')
```

- [ ] Run full test file to verify all FAIL: `python -m pytest vcenter_cmdb/tests/test_ad_helpers.py -v`
  Expected: all tests FAIL with ImportError

### Step 1.6 — Implement helper functions in `ad_users_local.py`

Create `vcenter_cmdb/ad_users_local.py` with helpers only (no main block yet):

```python
import csv
import logging
import os
import re
import struct
import uuid
from datetime import datetime, timedelta
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# === КОНФИГУРАЦИЯ ===
AD_HOST = os.environ.get("AD_HOST", "")
AD_BIND_DN = os.environ.get("AD_BIND_DN", "")
AD_PASSWORD = os.environ.get("AD_PASSWORD", "")
AD_BASE_DN = os.environ.get("AD_BASE_DN", "")
AD_USE_SSL = os.environ.get("AD_USE_SSL", "false").lower() == "true"
AD_OUTPUT_PATH = os.environ.get("AD_OUTPUT_PATH", "/tmp/ad_users_dump.csv")
AD_PAGE_SIZE = int(os.environ.get("AD_PAGE_SIZE", "500"))

AD_FILTER = "(&(objectClass=user)(objectCategory=person))"

AD_LDAP_ATTRIBUTES = [
    "sAMAccountName", "userPrincipalName", "objectSid", "uid", "objectGUID",
    "userAccountControl", "whenCreated", "pwdLastSet",
    "displayName", "department", "title", "company", "manager",
    "extensionAttribute5", "extensionAttribute8",
    "extensionAttribute10", "extensionAttribute12",
    "description",
]

CSV_COLUMNS = [
    "sAMAccountName", "UPN", "SID", "UID", "GUID",
    "account_type", "source", "status",
    "created_at", "last_password_change",
    "DisplayName", "department", "position", "title",
    "organization", "manager", "location",
    "EA5", "EA8", "EA10", "description",
]

_WINDOWS_EPOCH = datetime(1601, 1, 1)
_UAC_DISABLED = 0x2


# === ХЕЛПЕРЫ ===

def parse_sid(raw) -> str:
    if not raw:
        return ""
    if isinstance(raw, str):
        return raw
    b = bytes(raw)
    if len(b) < 8:
        return ""
    revision = b[0]
    sub_count = b[1]
    ia = int.from_bytes(b[2:8], "big")
    parts = [str(revision), str(ia)]
    for i in range(sub_count):
        offset = 8 + i * 4
        if offset + 4 > len(b):
            break
        sub = struct.unpack_from("<I", b, offset)[0]
        parts.append(str(sub))
    return "S-" + "-".join(parts)


def parse_guid(raw) -> str:
    if not raw:
        return ""
    if isinstance(raw, str):
        return raw
    try:
        return str(uuid.UUID(bytes_le=bytes(raw)))
    except Exception:
        return ""


def parse_windows_ts(raw) -> str:
    if not raw:
        return ""
    try:
        val = int(raw)
    except (TypeError, ValueError):
        return ""
    if val <= 0:
        return ""
    dt = _WINDOWS_EPOCH + timedelta(microseconds=val // 10)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def extract_manager_cn(dn: Optional[str]) -> str:
    if not dn:
        return ""
    m = re.match(r"CN=([^,]+)", dn, re.IGNORECASE)
    return m.group(1) if m else dn


def parse_uac(uac) -> tuple:
    try:
        val = int(uac or 0)
    except (TypeError, ValueError):
        val = 0
    status = "disabled" if val & _UAC_DISABLED else "enabled"
    return status, "user"


def _str(val) -> str:
    if val is None:
        return ""
    if isinstance(val, list):
        return str(val[0]) if val else ""
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    return str(val)


def _first_raw(val) -> bytes:
    if not val:
        return b""
    if isinstance(val, (bytes, bytearray)):
        return bytes(val)
    if isinstance(val, list):
        return bytes(val[0]) if val else b""
    return b""


def map_entry_to_row(attrs: dict, raw_attrs: dict) -> dict:
    uac = attrs.get("userAccountControl") or 0
    status, account_type = parse_uac(uac)
    return {
        "sAMAccountName": _str(attrs.get("sAMAccountName")),
        "UPN":            _str(attrs.get("userPrincipalName")),
        "SID":            parse_sid(_first_raw(raw_attrs.get("objectSid"))),
        "UID":            _str(attrs.get("uid")),
        "GUID":           parse_guid(_first_raw(raw_attrs.get("objectGUID"))),
        "account_type":   account_type,
        "source":         "AD",
        "status":         status,
        "created_at":     _str(attrs.get("whenCreated")),
        "last_password_change": parse_windows_ts(attrs.get("pwdLastSet")),
        "DisplayName":    _str(attrs.get("displayName")),
        "department":     _str(attrs.get("department")),
        "position":       _str(attrs.get("title")),
        "title":          _str(attrs.get("title")),
        "organization":   _str(attrs.get("company")),
        "manager":        extract_manager_cn(_str(attrs.get("manager"))),
        "location":       _str(attrs.get("extensionAttribute12")),
        "EA5":            _str(attrs.get("extensionAttribute5")),
        "EA8":            _str(attrs.get("extensionAttribute8")),
        "EA10":           _str(attrs.get("extensionAttribute10")),
        "description":    _str(attrs.get("description")),
    }
```

- [ ] Run tests to verify PASS: `python -m pytest vcenter_cmdb/tests/test_ad_helpers.py -v`
  Expected: all tests PASS

- [ ] Commit:
```bash
git add vcenter_cmdb/ad_users_local.py vcenter_cmdb/tests/test_ad_helpers.py
git commit -m "feat(ad): add AD helper functions with unit tests"
```

---

## Task 2: Local standalone script (`ad_users_local.py`)

**Files:**
- Modify: `vcenter_cmdb/ad_users_local.py` — add `fetch_ad_users()` and `__main__` block

### Step 2.1 — Append LDAP fetch + main to `ad_users_local.py`

Add after the helpers section:

```python
# === ОСНОВНАЯ ФУНКЦИЯ ===

def fetch_ad_users(output_path: str = AD_OUTPUT_PATH) -> int:
    from ldap3 import Server, Connection, SUBTREE, AUTO_BIND_NO_TLS, AUTO_BIND_TLS_BEFORE_BIND, ALL

    if not AD_HOST or not AD_BIND_DN or not AD_BASE_DN:
        raise ValueError("AD_HOST, AD_BIND_DN, AD_BASE_DN must be set via environment variables")

    logger.info(f"Connecting to {AD_HOST} (SSL={AD_USE_SSL})")
    server = Server(AD_HOST, get_info=ALL, use_ssl=AD_USE_SSL)
    auto_bind = AUTO_BIND_TLS_BEFORE_BIND if AD_USE_SSL else AUTO_BIND_NO_TLS
    conn = Connection(
        server,
        user=AD_BIND_DN,
        password=AD_PASSWORD,
        auto_bind=auto_bind,
    )

    logger.info(f"Searching base={AD_BASE_DN}, filter={AD_FILTER}, page_size={AD_PAGE_SIZE}")
    entries = conn.extend.standard.paged_search(
        search_base=AD_BASE_DN,
        search_filter=AD_FILTER,
        attributes=AD_LDAP_ATTRIBUTES,
        paged_size=AD_PAGE_SIZE,
        generator=False,
    )

    rows = []
    for entry in entries:
        if entry.get("type") != "searchResEntry":
            continue
        row = map_entry_to_row(
            entry.get("attributes", {}),
            entry.get("raw_attributes", {}),
        )
        rows.append(row)

    conn.unbind()
    logger.info(f"Fetched {len(rows)} accounts")

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"Saved to {output_path}")
    return len(rows)


if __name__ == "__main__":
    count = fetch_ad_users()
    print(f"Done: {count} accounts written to {AD_OUTPUT_PATH}")
```

### Step 2.2 — Manual smoke test (requires AD access)

```bash
export AD_HOST="dc01.company.local"
export AD_BIND_DN="CN=svc_ldap,OU=ServiceAccounts,DC=company,DC=local"
export AD_PASSWORD="secret"
export AD_BASE_DN="DC=company,DC=local"
export AD_OUTPUT_PATH="/tmp/ad_users_dump.csv"

python vcenter_cmdb/ad_users_local.py
head -3 /tmp/ad_users_dump.csv
```

Expected: CSV created, first line = header, second line = first user record.

- [ ] Commit:
```bash
git add vcenter_cmdb/ad_users_local.py
git commit -m "feat(ad): add standalone local AD users dump script"
```

---

## Task 3: Airflow DAG (`ad_users_to_cmdb.py`)

**Files:**
- Create: `vcenter_cmdb/ad_users_to_cmdb.py`

### Step 3.1 — Create Airflow DAG file

Create `vcenter_cmdb/ad_users_to_cmdb.py`:

```python
import csv
import logging
import re
import struct
import uuid
from datetime import datetime, timedelta
from typing import Optional

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

logger = logging.getLogger("airflow.task")

# === КОНФИГУРАЦИЯ ===
AD_FILTER = "(&(objectClass=user)(objectCategory=person))"

AD_LDAP_ATTRIBUTES = [
    "sAMAccountName", "userPrincipalName", "objectSid", "uid", "objectGUID",
    "userAccountControl", "whenCreated", "pwdLastSet",
    "displayName", "department", "title", "company", "manager",
    "extensionAttribute5", "extensionAttribute8",
    "extensionAttribute10", "extensionAttribute12",
    "description",
]

CSV_COLUMNS = [
    "sAMAccountName", "UPN", "SID", "UID", "GUID",
    "account_type", "source", "status",
    "created_at", "last_password_change",
    "DisplayName", "department", "position", "title",
    "organization", "manager", "location",
    "EA5", "EA8", "EA10", "description",
]

_WINDOWS_EPOCH = datetime(1601, 1, 1)
_UAC_DISABLED = 0x2

default_args = {
    "owner": "Sevryuk.DA@dns-shop.ru",
    "retries": 1,
}


# === ХЕЛПЕРЫ ===

def parse_sid(raw) -> str:
    if not raw:
        return ""
    if isinstance(raw, str):
        return raw
    b = bytes(raw)
    if len(b) < 8:
        return ""
    revision = b[0]
    sub_count = b[1]
    ia = int.from_bytes(b[2:8], "big")
    parts = [str(revision), str(ia)]
    for i in range(sub_count):
        offset = 8 + i * 4
        if offset + 4 > len(b):
            break
        sub = struct.unpack_from("<I", b, offset)[0]
        parts.append(str(sub))
    return "S-" + "-".join(parts)


def parse_guid(raw) -> str:
    if not raw:
        return ""
    if isinstance(raw, str):
        return raw
    try:
        return str(uuid.UUID(bytes_le=bytes(raw)))
    except Exception:
        return ""


def parse_windows_ts(raw) -> str:
    if not raw:
        return ""
    try:
        val = int(raw)
    except (TypeError, ValueError):
        return ""
    if val <= 0:
        return ""
    dt = _WINDOWS_EPOCH + timedelta(microseconds=val // 10)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def extract_manager_cn(dn: Optional[str]) -> str:
    if not dn:
        return ""
    m = re.match(r"CN=([^,]+)", dn, re.IGNORECASE)
    return m.group(1) if m else dn


def parse_uac(uac) -> tuple:
    try:
        val = int(uac or 0)
    except (TypeError, ValueError):
        val = 0
    status = "disabled" if val & _UAC_DISABLED else "enabled"
    return status, "user"


def _str(val) -> str:
    if val is None:
        return ""
    if isinstance(val, list):
        return str(val[0]) if val else ""
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    return str(val)


def _first_raw(val) -> bytes:
    if not val:
        return b""
    if isinstance(val, (bytes, bytearray)):
        return bytes(val)
    if isinstance(val, list):
        return bytes(val[0]) if val else b""
    return b""


def map_entry_to_row(attrs: dict, raw_attrs: dict) -> dict:
    uac = attrs.get("userAccountControl") or 0
    status, account_type = parse_uac(uac)
    return {
        "sAMAccountName": _str(attrs.get("sAMAccountName")),
        "UPN":            _str(attrs.get("userPrincipalName")),
        "SID":            parse_sid(_first_raw(raw_attrs.get("objectSid"))),
        "UID":            _str(attrs.get("uid")),
        "GUID":           parse_guid(_first_raw(raw_attrs.get("objectGUID"))),
        "account_type":   account_type,
        "source":         "AD",
        "status":         status,
        "created_at":     _str(attrs.get("whenCreated")),
        "last_password_change": parse_windows_ts(attrs.get("pwdLastSet")),
        "DisplayName":    _str(attrs.get("displayName")),
        "department":     _str(attrs.get("department")),
        "position":       _str(attrs.get("title")),
        "title":          _str(attrs.get("title")),
        "organization":   _str(attrs.get("company")),
        "manager":        extract_manager_cn(_str(attrs.get("manager"))),
        "location":       _str(attrs.get("extensionAttribute12")),
        "EA5":            _str(attrs.get("extensionAttribute5")),
        "EA8":            _str(attrs.get("extensionAttribute8")),
        "EA10":           _str(attrs.get("extensionAttribute10")),
        "description":    _str(attrs.get("description")),
    }


# === ЗАДАЧА DAG ===

def fetch_ad_users(**context):
    from ldap3 import Server, Connection, ALL, AUTO_BIND_NO_TLS, AUTO_BIND_TLS_BEFORE_BIND

    ad_host = Variable.get("AD_HOST")
    ad_bind_dn = Variable.get("AD_BIND_DN")
    ad_password = Variable.get("AD_PASSWORD")
    ad_base_dn = Variable.get("AD_BASE_DN")
    ad_use_ssl = Variable.get("AD_USE_SSL", default_var="false").lower() == "true"
    ad_output_path = Variable.get("AD_OUTPUT_PATH", default_var="/tmp/ad_users_dump.csv")
    ad_page_size = int(Variable.get("AD_PAGE_SIZE", default_var="500"))

    logger.info(f"Connecting to {ad_host} (SSL={ad_use_ssl})")
    server = Server(ad_host, get_info=ALL, use_ssl=ad_use_ssl)
    auto_bind = AUTO_BIND_TLS_BEFORE_BIND if ad_use_ssl else AUTO_BIND_NO_TLS
    conn = Connection(
        server,
        user=ad_bind_dn,
        password=ad_password,
        auto_bind=auto_bind,
    )

    logger.info(f"Searching base={ad_base_dn}, filter={AD_FILTER}, page_size={ad_page_size}")
    entries = conn.extend.standard.paged_search(
        search_base=ad_base_dn,
        search_filter=AD_FILTER,
        attributes=AD_LDAP_ATTRIBUTES,
        paged_size=ad_page_size,
        generator=False,
    )

    rows = []
    for entry in entries:
        if entry.get("type") != "searchResEntry":
            continue
        row = map_entry_to_row(
            entry.get("attributes", {}),
            entry.get("raw_attributes", {}),
        )
        rows.append(row)

    conn.unbind()
    logger.info(f"Fetched {len(rows)} accounts")

    with open(ad_output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"Saved {len(rows)} accounts to {ad_output_path}")
    return len(rows)


# === DAG ===

with DAG(
    dag_id="ad_users_dump",
    default_args=default_args,
    description="Выгрузка всех учётных записей AD в CSV",
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
    tags=["ad", "cmdb"],
) as dag:

    task_fetch = PythonOperator(
        task_id="fetch_ad_users",
        python_callable=fetch_ad_users,
    )
```

### Step 3.2 — Verify DAG imports cleanly

```bash
python -c "
import sys
from unittest.mock import MagicMock
sys.modules.update({
    'airflow': MagicMock(), 'airflow.models': MagicMock(),
    'airflow.operators': MagicMock(), 'airflow.operators.python': MagicMock(),
    'airflow.utils': MagicMock(), 'airflow.utils.dates': MagicMock(),
    'ldap3': MagicMock(),
})
import vcenter_cmdb.ad_users_to_cmdb
print('DAG import OK')
"
```

Expected: `DAG import OK`

- [ ] Commit:
```bash
git add vcenter_cmdb/ad_users_to_cmdb.py
git commit -m "feat(ad): add Airflow DAG ad_users_dump for AD account export"
```

---

## Task 4: Final verification

- [ ] Run full test suite:
```bash
cd C:/Users/Sevryuk.DA/Documents/CLAUDE
python -m pytest vcenter_cmdb/tests/ -v
```
Expected: all tests PASS

- [ ] Push:
```bash
git push
```
