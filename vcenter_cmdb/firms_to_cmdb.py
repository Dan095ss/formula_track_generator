import logging
import json
import re
import psycopg2
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.api.common.trigger_dag import trigger_dag
from airflow.utils import timezone

logger = logging.getLogger("airflow.task")

# === КОНФИГУРАЦИЯ ===
GP_HOST = Variable.get("GP_1C_HOST")
GP_PORT = int(Variable.get("GP_1C_PORT", default_var="5432"))
GP_USER = Variable.get("GP_1C_USER")
GP_PASSWORD = Variable.get("GP_1C_PASSWORD")
GP_DATABASE = Variable.get("GP_1C_DATABASE")

REF_TYPE_NAME = "branches"

_SQL = """
    SELECT
        Фирмы.Ссылка                AS id,
        Фирмы.Наименование          AS name,
        Фирмы.Код                   AS number,
        Фирмы.ПометкаУдаления       AS deleted,
        ГруппыРассылок.Наименование AS email_group_name,
        ГруппыРассылок.ЭлПочта      AS email,
        ТерриторииУр1.Наименование  AS ter_lvl_1,
        ТерриторииУр2.Наименование  AS ter_lvl_2,
        ТерриторииУр3.Наименование  AS ter_lvl_3
    FROM "cdc.adm-1c-dns-m.dns_m"."S.Firmy" AS Фирмы
         LEFT JOIN "cdc.adm-1c-dns-m.dns_m"."S.Firmy.IerarhijaTerritorij" AS ИерархияТерриторийУр1
                ON ИерархияТерриторийУр1.Ссылка = Фирмы.Ссылка
               AND ИерархияТерриторийУр1.Уровень = 1
         LEFT JOIN "cdc.adm-1c-dns-m.dns_m"."S.Territorii" AS ТерриторииУр1
                ON ИерархияТерриторийУр1.Территория = ТерриторииУр1.Ссылка
         LEFT JOIN "cdc.adm-1c-dns-m.dns_m"."S.Firmy.IerarhijaTerritorij" AS ИерархияТерриторийУр2
                ON ИерархияТерриторийУр2.Ссылка = Фирмы.Ссылка
               AND ИерархияТерриторийУр2.Уровень = 2
         LEFT JOIN "cdc.adm-1c-dns-m.dns_m"."S.Territorii" AS ТерриторииУр2
                ON ИерархияТерриторийУр2.Территория = ТерриторииУр2.Ссылка
         LEFT JOIN "cdc.adm-1c-dns-m.dns_m"."S.Firmy.IerarhijaTerritorij" AS ИерархияТерриторийУр3
                ON ИерархияТерриторийУр3.Ссылка = Фирмы.Ссылка
               AND ИерархияТерриторийУр3.Уровень = 3
         LEFT JOIN "cdc.adm-1c-dns-m.dns_m"."S.Territorii" AS ТерриторииУр3
                ON ИерархияТерриторийУр3.Территория = ТерриторииУр3.Ссылка
         LEFT JOIN "cdc.adm-1c-dns-m.dns_m"."RS.SostavGruppRassylok" AS ГруппыРассылок_Состав
                ON Фирмы.Ссылка = ГруппыРассылок_Состав.Элемент
         LEFT JOIN "cdc.adm-1c-dns-m.dns_m"."S.GruppyRassylok" AS ГруппыРассылок
                ON ГруппыРассылок_Состав.ГруппаРассылки = ГруппыРассылок.Ссылка
"""


def _s(val) -> str:
    if val is None:
        return ""
    return str(val).strip()


def clean_name(val: str) -> str:
    """Чистит название фирмы/группы:
    - снимает экранирование \" → "
    - убирает всё в круглых скобках (включая сами скобки)
    - схлопывает лишние пробелы
    """
    if not val:
        return val
    val = val.replace('\\"', '"')           # \" → "
    val = re.sub(r'\([^)]*\)|\([^)]*$', '', val)  # убираем (...) и обрезанное (ЗА...
    val = re.sub(r'\s{2,}', ' ', val)       # двойные пробелы → один
    return val.strip()


def fetch_firms(**context):
    ti = context["ti"]
    logger.info(f"GP: подключение к {GP_HOST}:{GP_PORT}/{GP_DATABASE}")

    conn = psycopg2.connect(
        host=GP_HOST,
        port=GP_PORT,
        user=GP_USER,
        password=GP_PASSWORD,
        database=GP_DATABASE,
        connect_timeout=30,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL)
            columns = [d[0] for d in cur.description]
            rows = cur.fetchall()
    finally:
        conn.close()

    logger.info(f"GP: получено {len(rows)} строк")

    firms: dict = {}
    for row in rows:
        rec = dict(zip(columns, row))
        fid = _s(rec["id"])
        if not fid:
            continue
        if fid not in firms:
            name = clean_name(_s(rec["name"]))
            firms[fid] = {
                "id_1c": fid,
                "name": name,
                "number": _s(rec["number"]),
                "deleted": _s(rec["deleted"]),
                "ter_lvl_1": _s(rec["ter_lvl_1"]),
                "ter_lvl_2": _s(rec["ter_lvl_2"]),
                "ter_lvl_3": _s(rec["ter_lvl_3"]),
                "_groups": [],
                "_emails": [],
                "name_for_link": name,
            }
        if rec.get("email_group_name"):
            firms[fid]["_groups"].append(_s(rec["email_group_name"]))
        if rec.get("email"):
            firms[fid]["_emails"].append(_s(rec["email"]))

    records = [
        {
            "id_1c": f["id_1c"],
            "name": f["name"],
            "number": f["number"],
            "deleted": f["deleted"],
            "ter_lvl_1": f["ter_lvl_1"],
            "ter_lvl_2": f["ter_lvl_2"],
            "ter_lvl_3": f["ter_lvl_3"],
            "email_group_names": "; ".join(f["_groups"]),
            "emails": "; ".join(f["_emails"]),
            "name_for_link": f["name_for_link"]
        }
        for f in firms.values()
    ]

    logger.info(f"Подготовлено {len(records)} уникальных фирм для CMDB")

    # Пушим как Python-объект (список словарей), НЕ как JSON-строку
    ti.xcom_push(key="FIRMS", value=records)


def trigger_cmdb_loader(**context):
    """Запускает cmdb_ref_uploader и cmdb_universal_uploader_v2."""
    ti = context["ti"]
    records = ti.xcom_pull(task_ids='fetch_firms', key='FIRMS')

    if not records:
        raise ValueError("Нет данных для передачи в uploaders")

    logger.info(f"Записей подготовлено: {len(records)}")
    ts = timezone.utcnow().strftime('%Y%m%dT%H%M%S')

    # ── 1. cmdb_ref_uploader (справочник) ────────────────────────────────────
    ref_conf = {
        "ref_type_name": REF_TYPE_NAME,
        "system": "1c_greenplum",
        "data": records,
    }
    ref_run = trigger_dag(
        dag_id='cmdb_ref_uploader',
        run_id=f"triggered__firms_ref_{ts}",
        conf=ref_conf,
        replace_microseconds=False,
    )
    logger.info(f"Запущен cmdb_ref_uploader: run_id={ref_run.run_id}")

    # ── 2. cmdb_universal_uploader_v2 (КЕ) ───────────────────────────────────
    ke_conf = {
        "ke_type": REF_TYPE_NAME,
        "system": "1c_greenplum",
        "data": records,
    }
    ke_run = trigger_dag(
        dag_id='cmdb_universal_uploader_v2',
        run_id=f"triggered__firms_ke_{ts}",
        conf=ke_conf,
        replace_microseconds=False,
    )
    logger.info(f"Запущен cmdb_universal_uploader_v2: run_id={ke_run.run_id}")


default_args = {
    "owner": "Sevryuk.DA@dns-shop.ru",
    "retries": 1,
    "retry_delay": 300,
}

with DAG(
        dag_id="firms_to_cmdb",
        default_args=default_args,
        schedule_interval="0 7 * * *",
        start_date=days_ago(1),
        catchup=False,
        tags=["inventory", "1c", "firms", "cmdb", "ref"],
) as dag:
    fetch_task = PythonOperator(
        task_id="fetch_firms",
        python_callable=fetch_firms,
    )

    # Используем PythonOperator вместо TriggerDagRunOperator
    trigger_task = PythonOperator(
        task_id="send_to_cmdb_ref",
        python_callable=trigger_cmdb_loader,
    )

    fetch_task >> trigger_task