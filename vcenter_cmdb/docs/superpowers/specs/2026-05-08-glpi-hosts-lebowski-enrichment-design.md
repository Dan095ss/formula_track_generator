# Design: Lebowski Owner Enrichment for GLPI Hosts DAG

**Date:** 2026-05-08  
**File:** `glpi_hosts_scan.py`  
**Status:** Approved

## Problem

The GLPI hosts scan DAG collects physical servers and ESXi hosts but has no Lebowski integration. When GLPI doesn't know the owner (`owner == "N/A"`), the field stays empty with no fallback.

The `vcenter_vms_to_cmdb.py` DAG already solves this for VMs — it falls back to Lebowski subsystem owner. The same pattern should apply to physical hosts.

## Solution

When a GLPI host has `owner == "N/A"`, look up its short hostname in Lebowski's `/subsystems` endpoint and fill the owner with the subsystem's `owner.name` (FIO).

## Changes to `glpi_hosts_scan.py`

### 1. New imports and constants

```python
import requests
from requests.auth import HTTPBasicAuth

LEBOWSKI_BASE_URL = "https://lebowski.dns-shop.ru/services/hs/api"
LEBOWSKI_CONN_ID = "lebowski_api"
```

### 2. New functions (same pattern as vcenter DAG)

**`get_lebowski_session()`**  
Returns a `requests.Session` with Basic Auth from Airflow Connection `lebowski_api`,
falling back to Variables `LEBOWSKI_LOGIN` / `LEBOWSKI_PASSWORD`.

**`fetch_lebowski_owners() -> dict`**  
Calls `GET /subsystems`, returns `{subsystem_name.lower(): owner_name}`.
On any failure, logs a warning and returns `{}` (graceful degradation).

### 3. Enrichment in `collect_glpi_data()`

Before the main loop:
```python
lebowski_owners = fetch_lebowski_owners()
```

After building each `clean_item`, if owner is missing:
```python
if clean_item["owner"] == "N/A" and shorthost:
    leb_owner = lebowski_owners.get(shorthost.lower())
    if leb_owner:
        clean_item["owner"] = leb_owner
        clean_item["lebowski_filled"] = "owner"
```

New field `"lebowski_filled"` added to the output dict: `"owner"` when Lebowski provided the value, `""` otherwise. Mirrors the vcenter DAG convention.

### 4. Bug fix

Line `if item["type"] == "esxi"` → `if item["hardware_type"] == "esxi"`.  
The field is stored as `hardware_type`, so clusters were never being enriched for ESXi hosts.

## Matching Strategy

- Match key: `shorthost` (first label before `.`, already extracted earlier in the loop)
- Lebowski keys: `subsystem.name.lower()` — assumed to be short hostnames matching GLPI records
- Priority: GLPI owner is primary; Lebowski is fallback only when `owner == "N/A"`

## What Is NOT Changing

- No shared utils module (two files, duplication acceptable for now)
- No new fields beyond `lebowski_filled`
- No change to owner priority logic — Lebowski remains last resort before N/A
- Group field not added (not available in current Lebowski API spec)

## Success Criteria

- Hosts with `owner == "N/A"` in GLPI get owner filled from Lebowski when a matching subsystem exists
- `lebowski_filled == "owner"` is set for those records
- ESXi cluster enrichment works (bug fix)
- Lebowski fetch failure does not break the DAG (graceful degradation)
