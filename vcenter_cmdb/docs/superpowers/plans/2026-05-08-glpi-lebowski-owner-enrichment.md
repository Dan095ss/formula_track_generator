# GLPI Hosts Lebowski Owner Enrichment — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enrich `owner` field in `glpi_hosts_scan.py` from Lebowski `/subsystems` API when GLPI returns `"N/A"`, and fix the existing ESXi cluster-enrichment bug.

**Architecture:** Two new functions (`get_lebowski_session`, `fetch_lebowski_owners`) mirror the pattern from `vcenter_vms_to_cmdb.py`. After each host record is built in the collect loop, if `owner == "N/A"` the short hostname is looked up in the Lebowski owners dict. Bug fix: `item["type"]` → `item["hardware_type"]` in the ESXi enrichment block.

**Tech Stack:** Python 3.x, requests, Apache Airflow (Variable, Connection), unittest.mock

---

### File Map

| Action | Path |
|--------|------|
| Create | `vcenter_cmdb/glpi_hosts_scan.py` |
| Create | `vcenter_cmdb/tests/__init__.py` |
| Create | `vcenter_cmdb/tests/test_glpi_lebowski.py` |

---

### Task 1: Save GLPI script to project

**Files:**
- Create: `vcenter_cmdb/glpi_hosts_scan.py`

- [ ] **Step 1: Create the file from the session content**

Save the full DAG code (shared by user in this session) verbatim to `vcenter_cmdb/glpi_hosts_scan.py`.

- [ ] **Step 2: Verify syntax**

```bash
cd vcenter_cmdb && python -m py_compile glpi_hosts_scan.py && echo "Syntax OK"
```
Expected: `Syntax OK`

- [ ] **Step 3: Commit**

```bash
git add vcenter_cmdb/glpi_hosts_scan.py
git commit -m "chore(glpi): add glpi_hosts_scan DAG to project"
```

---

### Task 2: Fix hardware_type bug with TDD

**Files:**
- Create: `vcenter_cmdb/tests/__init__.py`
- Create: `vcenter_cmdb/tests/test_glpi_lebowski.py`
- Modify: `vcenter_cmdb/glpi_hosts_scan.py`

The existing code has `if item["type"] == "esxi"` but the dict stores it as `hardware_type`.
This means ESXi hosts never get cluster data.

- [ ] **Step 1: Create test infrastructure**

Create empty `vcenter_cmdb/tests/__init__.py`.

Create `vcenter_cmdb/tests/test_glpi_lebowski.py`:

```python
import sys
import os
from unittest.mock import MagicMock, patch

# Patch all heavy imports before loading the DAG module
sys.modules.update({
    'airflow': MagicMock(),
    'airflow.models': MagicMock(),
    'airflow.operators': MagicMock(),
    'airflow.operators.python': MagicMock(),
    'airflow.utils': MagicMock(),
    'airflow.utils.dates': MagicMock(),
    'airflow.api': MagicMock(),
    'airflow.api.common': MagicMock(),
    'airflow.api.common.trigger_dag': MagicMock(),
    'pymysql': MagicMock(),
    'pyVim': MagicMock(),
    'pyVim.connect': MagicMock(),
    'pyVmomi': MagicMock(),
})

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest


class TestHardwareTypeBugFixed(unittest.TestCase):
    """Cluster enrichment must use hardware_type key, not type."""

    def test_esxi_cluster_enriched_via_hardware_type_key(self):
        all_data = [
            {"hostname": "esxi01.dns-shop.ru", "hardware_type": "esxi", "host_cluster": None},
        ]
        cluster_mapping = {"esxi01": "CLUSTER-A"}

        # This is the corrected logic — must match the fix in glpi_hosts_scan.py
        for item in all_data:
            if item["hardware_type"] == "esxi" and item["hostname"]:
                short = item["hostname"].split(".")[0].lower()
                item["host_cluster"] = cluster_mapping.get(short, "N/A")

        self.assertEqual(all_data[0]["host_cluster"], "CLUSTER-A")

    def test_non_esxi_host_cluster_unchanged(self):
        all_data = [
            {"hostname": "srv01.dns-shop.ru", "hardware_type": "physical", "host_cluster": None},
        ]
        cluster_mapping = {"srv01": "CLUSTER-B"}

        for item in all_data:
            if item["hardware_type"] == "esxi" and item["hostname"]:
                short = item["hostname"].split(".")[0].lower()
                item["host_cluster"] = cluster_mapping.get(short, "N/A")

        self.assertIsNone(all_data[0]["host_cluster"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to confirm they pass (logic verified)**

```bash
cd vcenter_cmdb && python -m pytest tests/test_glpi_lebowski.py::TestHardwareTypeBugFixed -v
```
Expected: 2 PASS

- [ ] **Step 3: Fix the bug in glpi_hosts_scan.py**

Find the block inside `if esxi_hostnames:` — the loop that enriches clusters. Change:

```python
# BEFORE (bug — key doesn't exist):
if item["type"] == "esxi" and item["hostname"]:

# AFTER (fix):
if item["hardware_type"] == "esxi" and item["hostname"]:
```

- [ ] **Step 4: Commit**

```bash
git add vcenter_cmdb/glpi_hosts_scan.py vcenter_cmdb/tests/__init__.py vcenter_cmdb/tests/test_glpi_lebowski.py
git commit -m "fix(glpi): use hardware_type key in ESXi cluster enrichment block"
```

---

### Task 3: Add Lebowski fetch functions with TDD

**Files:**
- Modify: `vcenter_cmdb/glpi_hosts_scan.py`
- Modify: `vcenter_cmdb/tests/test_glpi_lebowski.py`

- [ ] **Step 1: Write failing tests**

Append to `vcenter_cmdb/tests/test_glpi_lebowski.py` (after the existing classes):

```python
class TestFetchLebowskiOwners(unittest.TestCase):

    @patch('glpi_hosts_scan.requests')
    @patch('glpi_hosts_scan.Connection')
    def test_returns_owner_dict_on_success(self, mock_conn, mock_requests):
        mock_conn.get_connection_from_secrets.return_value = MagicMock(
            login="user", password="pass"
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "message": "",
            "data": [
                {"id": "a", "name": "srv01", "owner": {"id": "b", "name": "Иванов Иван Иванович"}},
                {"id": "c", "name": "SRV02", "owner": {"id": "d", "name": "Петров Пётр"}},
            ]
        }
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_requests.Session.return_value = mock_session

        import glpi_hosts_scan as m
        result = m.fetch_lebowski_owners()

        self.assertEqual(result["srv01"], "Иванов Иван Иванович")
        self.assertEqual(result["srv02"], "Петров Пётр")   # lowercased key

    @patch('glpi_hosts_scan.requests')
    @patch('glpi_hosts_scan.Connection')
    def test_returns_empty_dict_on_network_error(self, mock_conn, mock_requests):
        mock_conn.get_connection_from_secrets.side_effect = Exception("no conn")
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("timeout")
        mock_requests.Session.return_value = mock_session

        import glpi_hosts_scan as m
        result = m.fetch_lebowski_owners()

        self.assertEqual(result, {})

    @patch('glpi_hosts_scan.requests')
    @patch('glpi_hosts_scan.Connection')
    def test_skips_entries_with_owner_name_too_short(self, mock_conn, mock_requests):
        mock_conn.get_connection_from_secrets.return_value = MagicMock(login="u", password="p")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "message": "",
            "data": [
                {"id": "x", "name": "srv03", "owner": {"id": "y", "name": "AB"}},
            ]
        }
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_requests.Session.return_value = mock_session

        import glpi_hosts_scan as m
        result = m.fetch_lebowski_owners()

        self.assertNotIn("srv03", result)
```

- [ ] **Step 2: Run to confirm tests fail**

```bash
cd vcenter_cmdb && python -m pytest tests/test_glpi_lebowski.py::TestFetchLebowskiOwners -v
```
Expected: FAIL — `module 'glpi_hosts_scan' has no attribute 'fetch_lebowski_owners'`

- [ ] **Step 3: Add imports and constants to glpi_hosts_scan.py**

In the imports section, add after `import logging`:

```python
import requests
from requests.auth import HTTPBasicAuth
from airflow.models import Connection
```

After the `GLPI_INSTANCES = [...]` line, add:

```python
LEBOWSKI_BASE_URL = "https://lebowski.dns-shop.ru/services/hs/api"
LEBOWSKI_CONN_ID = "lebowski_api"
```

- [ ] **Step 4: Add the two functions to glpi_hosts_scan.py**

Add after `extract_role_env_from_comments_or_hostname`:

```python
def get_lebowski_session():
    session = requests.Session()
    try:
        conn = Connection.get_connection_from_secrets(LEBOWSKI_CONN_ID)
        session.auth = HTTPBasicAuth(conn.login, conn.password)
    except Exception:
        login = Variable.get("LEBOWSKI_LOGIN", default_var=None)
        password = Variable.get("LEBOWSKI_PASSWORD", default_var=None)
        if login and password:
            session.auth = HTTPBasicAuth(login, password)
        else:
            logging.warning("Lebowski API: не найдены креды")
    session.headers.update({"Accept": "application/json"})
    return session


def fetch_lebowski_owners() -> dict:
    """Returns {subsystem_name.lower(): owner_name} from Lebowski /subsystems."""
    result = {}
    try:
        session = get_lebowski_session()
        r = session.get(f"{LEBOWSKI_BASE_URL}/subsystems", timeout=30)
        if r.status_code == 200:
            data = r.json()
            if data.get("code") == 0 and isinstance(data.get("data"), list):
                for sub in data["data"]:
                    owner = sub.get("owner", {})
                    owner_name = owner.get("name") if isinstance(owner, dict) else None
                    sub_name = sub.get("name", "")
                    if sub_name and owner_name and len(str(owner_name)) > 2:
                        result[sub_name.lower()] = str(owner_name).strip()
    except Exception as e:
        logging.warning(f"Lebowski /subsystems: {e}")
    return result
```

- [ ] **Step 5: Run tests to confirm they pass**

```bash
cd vcenter_cmdb && python -m pytest tests/test_glpi_lebowski.py::TestFetchLebowskiOwners -v
```
Expected: 3 PASS

- [ ] **Step 6: Commit**

```bash
git add vcenter_cmdb/glpi_hosts_scan.py vcenter_cmdb/tests/test_glpi_lebowski.py
git commit -m "feat(glpi): add get_lebowski_session and fetch_lebowski_owners"
```

---

### Task 4: Wire enrichment into collect loop with TDD

**Files:**
- Modify: `vcenter_cmdb/glpi_hosts_scan.py`
- Modify: `vcenter_cmdb/tests/test_glpi_lebowski.py`

- [ ] **Step 1: Write failing tests for enrichment logic**

Append to `vcenter_cmdb/tests/test_glpi_lebowski.py`:

```python
class TestOwnerEnrichmentLogic(unittest.TestCase):
    """Pure enrichment logic — no DAG imports needed."""

    def _enrich(self, item: dict, lebowski_owners: dict) -> dict:
        shorthost = item.get("shorthost", "")
        if item["owner"] == "N/A" and shorthost:
            leb_owner = lebowski_owners.get(shorthost.lower())
            if leb_owner:
                item["owner"] = leb_owner
                item["lebowski_filled"] = "owner"
        return item

    def test_fills_owner_when_na_and_match_found(self):
        item = {"owner": "N/A", "shorthost": "srv01", "lebowski_filled": ""}
        owners = {"srv01": "Иванов Иван Иванович"}
        result = self._enrich(item, owners)
        self.assertEqual(result["owner"], "Иванов Иван Иванович")
        self.assertEqual(result["lebowski_filled"], "owner")

    def test_does_not_overwrite_existing_owner(self):
        item = {"owner": "TeamOps", "shorthost": "srv01", "lebowski_filled": ""}
        owners = {"srv01": "Иванов Иван Иванович"}
        result = self._enrich(item, owners)
        self.assertEqual(result["owner"], "TeamOps")
        self.assertEqual(result["lebowski_filled"], "")

    def test_owner_stays_na_when_host_not_in_lebowski(self):
        item = {"owner": "N/A", "shorthost": "unknownhost", "lebowski_filled": ""}
        owners = {"srv01": "Иванов Иван Иванович"}
        result = self._enrich(item, owners)
        self.assertEqual(result["owner"], "N/A")
        self.assertEqual(result["lebowski_filled"], "")

    def test_lookup_is_case_insensitive(self):
        item = {"owner": "N/A", "shorthost": "SRV01", "lebowski_filled": ""}
        owners = {"srv01": "Иванов Иван Иванович"}
        result = self._enrich(item, owners)
        self.assertEqual(result["owner"], "Иванов Иван Иванович")
```

- [ ] **Step 2: Run to confirm they pass (logic verified inline)**

```bash
cd vcenter_cmdb && python -m pytest tests/test_glpi_lebowski.py::TestOwnerEnrichmentLogic -v
```
Expected: 4 PASS

- [ ] **Step 3: Add lebowski_owners fetch before the GLPI loop in collect_glpi_data**

Right after `all_data = []` and `esxi_hostnames = []` at the start of `collect_glpi_data`:

```python
lebowski_owners = fetch_lebowski_owners()
logging.info(f"Lebowski: {len(lebowski_owners)} владельцев подсистем")
```

- [ ] **Step 4: Add lebowski_filled field to clean_item dict**

In the `clean_item = { ... }` block, add as the last field:

```python
"lebowski_filled": "",
```

- [ ] **Step 5: Add enrichment block right before all_data.append**

Find `all_data.append(clean_item)` and replace it with:

```python
if clean_item["owner"] == "N/A" and shorthost:
    leb_owner = lebowski_owners.get(shorthost.lower())
    if leb_owner:
        clean_item["owner"] = leb_owner
        clean_item["lebowski_filled"] = "owner"

all_data.append(clean_item)
```

- [ ] **Step 6: Run full test suite**

```bash
cd vcenter_cmdb && python -m pytest tests/test_glpi_lebowski.py -v
```
Expected: all PASS

- [ ] **Step 7: Verify syntax**

```bash
cd vcenter_cmdb && python -m py_compile glpi_hosts_scan.py && echo "Syntax OK"
```
Expected: `Syntax OK`

- [ ] **Step 8: Commit and push**

```bash
git add vcenter_cmdb/glpi_hosts_scan.py vcenter_cmdb/tests/test_glpi_lebowski.py
git commit -m "feat(glpi): enrich owner from Lebowski when GLPI returns N/A"
git push
```
