import json
import logging
import uuid

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger("airflow.task")

# === КОНФИГУРАЦИЯ ===
CMDB_BASE_URL = Variable.get("CMDB_BASE_URL", default_var="https://cmdb.dns-shop.ru/api/v1")
CMDB_USER = Variable.get("CMDB_USER")
CMDB_PASSWORD = Variable.get("CMDB_PASSWORD")


# === CMDB ХЕЛПЕРЫ ===

def _cmdb_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    resp = session.post(
        f"{CMDB_BASE_URL}/auth/login",
        data={"username": CMDB_USER, "password": CMDB_PASSWORD},
        verify=False,
        timeout=30,
    )
    resp.raise_for_status()
    token = resp.json().get("access_token", "")
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    logger.info("CMDB: аутентификация успешна")
    return session


def _get_or_create_ref_type(session: requests.Session, ref_type_name: str) -> tuple:
    """
    Возвращает (ref_type_uuid, attr_map), где attr_map = {attr_name: attr_type_uuid}.
    Если RefType с таким именем не существует — создаёт его на основе ключей первой записи данных.
    Создание откладывается до момента вызова upload, чтобы знать реальные атрибуты.
    """
    resp = session.get(
        f"{CMDB_BASE_URL}/ref_type/search/",
        params={"name": ref_type_name, "exclude_attrs": "false"},
        verify=False,
        timeout=30,
    )
    resp.raise_for_status()

    existing = next(
        (rt for rt in resp.json().get("data", []) if rt.get("name") == ref_type_name),
        None,
    )

    if existing:
        rt_uuid = existing["uuid"]
        logger.info(f"CMDB: RefType '{ref_type_name}' найден ({rt_uuid})")
        if not existing.get("attrs"):
            r = session.get(f"{CMDB_BASE_URL}/ref_type/{rt_uuid}", verify=False, timeout=30)
            r.raise_for_status()
            existing = r.json()
        attr_map = {a["name"]: a["uuid"] for a in (existing.get("attrs") or [])}
        return rt_uuid, attr_map

    return None, {}


def _create_ref_type(session: requests.Session, ref_type_name: str, field_names: list) -> tuple:
    rt_uuid = str(uuid.uuid4())
    attrs_payload = [
        {
            "uuid":          str(uuid.uuid4()),
            "name":          name,
            "type":          "str",
            "ref_type_uuid": rt_uuid,
            "is_name":       (name == "name"),
            "is_required":   False,
            "priority":      i,
            "order":         i,
        }
        for i, name in enumerate(field_names)
    ]
    r = session.post(
        f"{CMDB_BASE_URL}/ref_type/{rt_uuid}",
        json={"name": ref_type_name, "attrs": attrs_payload},
        verify=False,
        timeout=30,
    )
    r.raise_for_status()
    logger.info(f"CMDB: RefType '{ref_type_name}' создан ({rt_uuid}), атрибуты: {field_names}")
    attr_map = {a["name"]: a["uuid"] for a in attrs_payload}
    return rt_uuid, attr_map


def _post_ref(session: requests.Session, rt_uuid: str, attr_map: dict, record: dict) -> bool:
    ref_uuid = str(uuid.uuid4())
    attrs = [
        {
            "uuid":           str(uuid.uuid4()),
            "attr_type_uuid": atype_uuid,
            "bvalue":         str(record.get(aname, "") or ""),
            "ref_uuid":       ref_uuid,
        }
        for aname, atype_uuid in attr_map.items()
        if aname in record
    ]
    try:
        r = session.post(
            f"{CMDB_BASE_URL}/ref/{ref_uuid}",
            json={"ref_type_uuid": rt_uuid, "is_visible": True, "attrs": attrs},
            verify=False,
            timeout=30,
        )
        r.raise_for_status()
        return True
    except requests.HTTPError as e:
        logger.error(f"Ref POST {e.response.status_code}: {e.response.text[:300]}")
        return False
    except Exception as e:
        logger.error(f"Ref POST ошибка: {e}")
        return False


# === ОСНОВНАЯ ЗАДАЧА ===

def upload_refs(**context):
    """
    Универсальный загрузчик записей в CMDB справочник (RefType).

    Ожидаемые параметры в dag_run.conf:
        ref_type_name (str):  имя справочника (напр. "Филиалы")
        system        (str):  источник данных (для логов)
        data          (list): список записей — каждая запись это dict {field: value}
    """
    dag_run = context["dag_run"]
    conf = dag_run.conf or {}

    ref_type_name = conf.get("ref_type_name")
    system = conf.get("system", "unknown")
    data = conf.get("data", [])

    if not ref_type_name:
        raise ValueError("Обязателен параметр 'ref_type_name'")

    if isinstance(data, str):
        logger.warning("data передана строкой — десериализуем JSON")
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"data не является валидным JSON: {e}")

    if not isinstance(data, list):
        raise ValueError(f"Ожидался список, получен {type(data)}")

    if not data:
        logger.info("Нет данных для загрузки")
        return

    logger.info(f"Загрузка {len(data)} записей в справочник '{ref_type_name}' (system={system})")

    session = _cmdb_session()
    rt_uuid, attr_map = _get_or_create_ref_type(session, ref_type_name)

    if not rt_uuid:
        field_names = list(data[0].keys())
        rt_uuid, attr_map = _create_ref_type(session, ref_type_name, field_names)

    logger.info(f"RefType UUID: {rt_uuid} | атрибуты: {list(attr_map.keys())}")

    ok = err = 0
    for record in data:
        if _post_ref(session, rt_uuid, attr_map, record):
            ok += 1
        else:
            err += 1
            logger.error(f"Не удалось загрузить запись: {record}")

    logger.info(f"Итог: {ok} OK / {err} ошибок из {len(data)}")
    if err:
        raise RuntimeError(f"Часть записей не загружена: {err} ошибок")


# === DAG ===

default_args = {
    "owner": "Sevryuk.DA@dns-shop.ru",
    "retries": 0,
}

with DAG(
    dag_id="cmdb_ref_uploader",
    default_args=default_args,
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["cmdb", "ref", "uploader"],
) as dag:

    PythonOperator(
        task_id="upload_refs",
        python_callable=upload_refs,
    )
