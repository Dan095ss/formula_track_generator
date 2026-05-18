import json
import logging
import uuid

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger("airflow.task")

CMDB_URL = "https://cmdb.dns-shop.ru/broker/cmdb-sources"
TIMEDELTA_SECONDS = 604800  # 7 дней


def upload_refs(**context):
    """
    Загружает данные в справочник CMDB (RefType).
    Аналог cmdb_universal_uploader_v2, но для Ref, а не для CItem.

    Ожидаемые параметры в dag_run.conf:
        ref_type_name (str):  имя справочника (напр. "Филиалы")
        system        (str):  источник данных
        data          (list): список записей [{field: value}, ...]
    """
    dag_run = context["dag_run"]
    conf = dag_run.conf or {}

    ref_type_name = conf.get("ref_type_name")
    system = conf.get("system", "unknown")
    data = conf.get("data", [])

    if not ref_type_name:
        raise ValueError("Обязателен параметр 'ref_type_name'")

    if isinstance(data, str):
        logger.warning(f"data передана строкой: {data[:200]}...")
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"data не является валидным JSON: {e}")

    if not isinstance(data, list):
        logger.warning(f"data не список (тип: {type(data)}). Пропускаем.")
        return

    if not data:
        logger.info("Нет данных для загрузки.")
        return

    run_uuid = str(uuid.uuid4())
    item_count = len(data)

    # === ШАГ 1: clear — очистка старых записей ===
    clear_payload = {
        "system": system,
        "uuid": run_uuid,
        "action": "clear",
        "data": {
            "ref_type_name": ref_type_name,
            "message_count": item_count,
            "timedelta": TIMEDELTA_SECONDS,
        },
    }

    logger.info(f"Отправка clear для справочника '{ref_type_name}' (старше {TIMEDELTA_SECONDS}с)")
    try:
        resp = requests.post(
            CMDB_URL,
            data=json.dumps(clear_payload, ensure_ascii=False, default=str).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            verify=False,
            timeout=30,
        )
        resp.raise_for_status()
        logger.info(f"Clear отправлен успешно")
    except Exception as e:
        logger.error(f"Ошибка при отправке clear: {e}")

    # === ШАГ 2: insert — загрузка новых записей ===
    logger.info(f"Отправка {item_count} записей в '{ref_type_name}'")

    success = 0
    for item in data:
        insert_payload = {
            "system": system,
            "action": "insert",
            "uuid": run_uuid,
            "data": {
                "ref_type_name": ref_type_name,
                "attrs": item,
            },
        }
        try:
            resp = requests.post(
                CMDB_URL,
                data=json.dumps(insert_payload, ensure_ascii=False, default=str).encode("utf-8"),
                headers={"Content-Type": "application/json; charset=utf-8"},
                verify=False,
                timeout=30,
            )
            resp.raise_for_status()
            success += 1
        except Exception as e:
            logger.error(f"Ошибка записи: {e} | данные: {item}")

    logger.info(f"Итог: {success}/{item_count} записей загружено в '{ref_type_name}'")


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
