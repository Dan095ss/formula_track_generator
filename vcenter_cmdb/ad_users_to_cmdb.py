import logging
import re
import struct
import uuid
from datetime import datetime, timedelta
from typing import Optional

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
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
_AD_NEVER = 9223372036854775807

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
    if isinstance(raw, datetime):
        return raw.strftime("%Y-%m-%d %H:%M:%S")
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
        s = str(val[0]) if val else ""
    elif isinstance(val, datetime):
        s = val.strftime("%Y-%m-%d %H:%M:%S")
    else:
        s = str(val)
    return s.replace("'", "")


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
        "EA8":            _str(attrs.get("extensionAttribute8")).lower(),
        "EA10":           _str(attrs.get("extensionAttribute10")),
        "description":    _str(attrs.get("description")),
    }


# === ЗАДАЧА DAG ===

def fetch_ad_users(**context):
    from ldap3 import Server, Connection, ALL, AUTO_BIND_NO_TLS

    ti = context["ti"]

    ad_server = Variable.get("AD_SERVER")
    ad_user = Variable.get("AD_USER")
    ad_password = Variable.get("AD_PASSWORD")
    ad_base_dn = Variable.get("AD_BASE_DN")
    try:
        ad_page_size = int(Variable.get("AD_PAGE_SIZE", default_var="500"))
    except ValueError:
        ad_page_size = 500

    logger.info(f"Подключение к {ad_server}, user={ad_user}")
    server = Server(ad_server, get_info=ALL)
    conn = Connection(
        server,
        user=ad_user,
        password=ad_password,
        auto_bind=AUTO_BIND_NO_TLS,
    )

    logger.info(f"Поиск: base={ad_base_dn}, filter={AD_FILTER}, page_size={ad_page_size}")
    try:
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
            login = row.get("sAMAccountName") or "?"
            if len(rows) == 1:
                logger.info(
                    f"[1] Первая УЗ (тест): login={login} | status={row.get('status')} | "
                    f"DisplayName={row.get('DisplayName')} | department={row.get('department')} | "
                    f"position={row.get('position')} | manager={row.get('manager')} | "
                    f"EA5={row.get('EA5')} | EA10={row.get('EA10')}"
                )
            else:
                logger.info(f"[{len(rows)}] УЗ обработана: {login}")
    finally:
        conn.unbind()
        logger.info("Соединение с AD закрыто")

    logger.info(f"Собрано {len(rows)} учётных записей")
    ti.xcom_push(key="ACCOUNT", value=rows)
    logger.info(f"Данные переданы в XCom: {len(rows)} записей -> cmdb_universal_uploader_v2")


# === DAG ===

with DAG(
    dag_id="ad_users_dump",
    default_args=default_args,
    description="Выгрузка всех учётных записей AD в CMDB",
    schedule_interval="0 6 * * *",
    start_date=days_ago(1),
    catchup=False,
    tags=["ad", "cmdb", "account"],
) as dag:

    collect_task = PythonOperator(
        task_id="fetch_ad_users",
        python_callable=fetch_ad_users,
    )

    trigger_cmdb = TriggerDagRunOperator(
        task_id="send_to_cmdb_account",
        trigger_dag_id="cmdb_universal_uploader_v2",
        conf={
            "ke_type": "ACCOUNT",
            "system": "ad",
            "data": "{{ ti.xcom_pull(task_ids='fetch_ad_users', key='ACCOUNT') | tojson }}",
        },
    )

    collect_task >> trigger_cmdb
