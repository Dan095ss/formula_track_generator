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
try:
    AD_PAGE_SIZE = int(os.environ.get("AD_PAGE_SIZE", "500"))
except ValueError:
    AD_PAGE_SIZE = 500

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
_AD_NEVER = 9223372036854775807  # 0x7FFFFFFFFFFFFFFF — AD sentinel for "never"


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
    if val <= 0 or val == _AD_NEVER:
        return ""
    try:
        dt = _WINDOWS_EPOCH + timedelta(microseconds=val // 10)
    except OverflowError:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def extract_manager_cn(dn: Optional[str]) -> str:
    if not dn:
        return ""
    m = re.match(r"CN=([^,]+)", dn, re.IGNORECASE)
    return m.group(1) if m else ""


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


# === ОСНОВНАЯ ФУНКЦИЯ ===

def fetch_ad_users(output_path: str = AD_OUTPUT_PATH) -> int:
    from ldap3 import Server, Connection, ALL, AUTO_BIND_NO_TLS, AUTO_BIND_TLS_BEFORE_BIND

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
    try:
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
    finally:
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
