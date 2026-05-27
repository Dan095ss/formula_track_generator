"""
Lebowski /subsystems → CMDB: IS, IS_COMPONENT, IS_INSTANCE

IS          ← каждая подсистема Lebowski
IS_COMPONENT← каждый сервер подсистемы (owner/team с /server/{id}, fallback на подсистему)
IS_INSTANCE ← группировка серверов по (IS_name, location_prefix)
"""

import re
import logging
import urllib3
from collections import defaultdict

import requests
from requests.auth import HTTPBasicAuth
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable, Connection
from airflow.utils.dates import days_ago
from airflow.api.common.trigger_dag import trigger_dag
from airflow.utils import timezone

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

default_args = {
    "owner": "Sevryuk.DA@dns-shop.ru",
    "retries": 1,
}

LEBOWSKI_BASE_URL = "https://lebowski.dns-shop.ru/services/hs/api"
LEBOWSKI_CONN_ID = "lebowski_api"

_ROLE_PATTERNS = [
    (r'\b(db|rds|mysql|pg|postgres|oracle|mssql|mongo)\b', 'DB'),
    (r'\b(web|www|nginx|apache|iis)\b', 'WEB'),
    (r'\b(api|gw|gateway|pgtw)\b', 'API'),
    (r'\b(docker|cont|container|k8s)\b', 'CONTAINER'),
    (r'\b(mon|monitoring|grafana|zabbix|prometheus)\b', 'MONITORING'),
    (r'\b(cache|redis|memcache)\b', 'CACHE'),
    (r'\b(kafka|rabbit|queue|mq)\b', 'QUEUE'),
    (r'\b(backup|bkp)\b', 'BACKUP'),
    (r'\b(cicd|jenkins|gitlab)\b', 'CICD'),
    (r'\b(storage|nas|san|minio)\b', 'STORAGE'),
    (r'\b(hv|hyperv|esxi|vcenter)\b', 'MGMT'),
]

_ENV_PATTERNS = [
    (r'prod', 'PROD'),
    (r'stage', 'STAGE'),
    (r'test', 'TEST'),
    (r'dev', 'DEV'),
    (r'sand', 'SAND'),
]


def _get_session() -> requests.Session:
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
            logging.warning("Lebowski: креды не найдены")
    session.headers.update({"Accept": "application/json"})
    return session


def _fetch(session: requests.Session, endpoint: str) -> dict | None:
    try:
        r = session.get(f"{LEBOWSKI_BASE_URL}/{endpoint}", timeout=30, verify=False)
        if r.status_code in (403, 404):
            return None
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.warning(f"Lebowski /{endpoint}: {e}")
        return None


def _parse_role(name: str) -> str:
    name_lower = name.lower()
    for pattern, role in _ROLE_PATTERNS:
        if re.search(pattern, name_lower):
            return role
    return ''


def _parse_env(name: str) -> str:
    name_lower = name.lower()
    for pattern, env in _ENV_PATTERNS:
        if re.search(pattern, name_lower):
            return env
    return ''


def _location_prefix(name: str) -> str:
    return name.split('-')[0].upper() if name else ''


def collect_and_transform(**context):
    ti = context['ti']
    session = _get_session()

    resp = _fetch(session, "subsystems")
    if not resp or resp.get("code") != 0:
        raise ValueError("Не удалось получить /subsystems")

    subsystems = resp.get("data", [])
    logging.info(f"Подсистем получено: {len(subsystems)}")

    server_cache: dict[str, dict] = {}

    def get_server(srv_id: str) -> dict:
        if srv_id in server_cache:
            return server_cache[srv_id]
        detail = _fetch(session, f"server/{srv_id}")
        data = detail.get("data", {}) if detail and detail.get("code") == 0 else {}
        server_cache[srv_id] = data
        return data

    is_list = []
    components_list = []
    # ключ: (IS_name, location) → первый найденный environment
    instances_map: dict[tuple, dict] = {}

    for sub in subsystems:
        sub_id = sub.get("id", "")
        sub_name = (sub.get("name") or "").strip()
        if not sub_name:
            continue

        owner_obj = sub.get("owner") or {}
        team_obj = sub.get("team") or {}
        sub_owner = (owner_obj.get("name") or "").strip() if isinstance(owner_obj, dict) else ""
        sub_team = (team_obj.get("name") or "").strip() if isinstance(team_obj, dict) else ""

        is_list.append({
            "IS_id": sub_id,
            "name": sub_name,
            "owner": sub_owner,
            "admin": sub_team,
            "description": (sub.get("description") or "").strip(),
        })

        seen_in_sub: set[str] = set()
        for srv in (sub.get("servers") or []):
            srv_id = srv.get("id", "")
            srv_name = (srv.get("name") or "").strip()
            if not srv_name or srv_id in seen_in_sub:
                continue
            seen_in_sub.add(srv_id)

            detail = get_server(srv_id)
            srv_owner = (detail.get("owner") or "").strip() or sub_owner
            srv_admin = (detail.get("team") or "").strip() or sub_team

            components_list.append({
                "component_id": srv_id,
                "name": srv_name.lower(),
                "IS_name": sub_name,
                "deployment_target": srv_name.lower(),
                "owner": srv_owner,
                "admin": srv_admin,
                "role": _parse_role(srv_name),
            })

            location = _location_prefix(srv_name)
            environment = _parse_env(srv_name)
            key = (sub_name, location)
            if key not in instances_map:
                instances_map[key] = {
                    "IS_name": sub_name,
                    "location": location,
                    "environment": environment,
                }
            elif not instances_map[key]["environment"] and environment:
                # уточняем среду если ранее не определили
                instances_map[key]["environment"] = environment

    instances_list = [
        {"instance_id": str(i), **inst}
        for i, inst in enumerate(instances_map.values(), start=1)
    ]

    logging.info(
        f"IS: {len(is_list)} | IS_COMPONENT: {len(components_list)} | IS_INSTANCE: {len(instances_list)} "
        f"| /server/ calls (cached): {len(server_cache)}"
    )

    ti.xcom_push(key="is_data", value=is_list)
    ti.xcom_push(key="components_data", value=components_list)
    ti.xcom_push(key="instances_data", value=instances_list)


def _trigger_upload(ke_type: str, xcom_key: str, **context):
    ti = context['ti']
    data = ti.xcom_pull(task_ids='collect_and_transform', key=xcom_key)

    if not data:
        logging.warning(f"{ke_type}: нет данных, пропускаем")
        return

    logging.info(f"{ke_type}: отправляем {len(data)} записей")
    dag_run = trigger_dag(
        dag_id='cmdb_universal_uploader_v2',
        run_id=f"lebowski_{ke_type.lower()}_{timezone.utcnow().strftime('%Y%m%dT%H%M%S')}",
        conf={"ke_type": ke_type, "system": "lebowski", "data": data},
        replace_microseconds=False,
    )
    logging.info(f"Запущен cmdb_universal_uploader_v2 для {ke_type}, run_id={dag_run.run_id}")


with DAG(
    dag_id='lebowski_is_to_cmdb',
    default_args=default_args,
    schedule_interval='0 10 * * *',
    start_date=days_ago(1),
    catchup=False,
    tags=['inventory', 'lebowski', 'is', 'cmdb'],
) as dag:

    collect_task = PythonOperator(
        task_id='collect_and_transform',
        python_callable=collect_and_transform,
    )

    upload_is = PythonOperator(
        task_id='upload_IS',
        python_callable=_trigger_upload,
        op_kwargs={"ke_type": "IS", "xcom_key": "is_data"},
    )

    upload_components = PythonOperator(
        task_id='upload_IS_COMPONENT',
        python_callable=_trigger_upload,
        op_kwargs={"ke_type": "IS_COMPONENT", "xcom_key": "components_data"},
    )

    upload_instances = PythonOperator(
        task_id='upload_IS_INSTANCE',
        python_callable=_trigger_upload,
        op_kwargs={"ke_type": "IS_INSTANCE", "xcom_key": "instances_data"},
    )

    collect_task >> [upload_is, upload_components, upload_instances]
