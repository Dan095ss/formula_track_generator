#!/usr/bin/env python3
"""
Дамп топика ha_logs из Kafka UI за последние 24 часа.
Сохраняет: ha_logs_YYYYMMDD_HHMMSS.ndjson + ha_logs_YYYYMMDD_HHMMSS.csv

Запуск:
    python kafka_ha_logs_dump.py
    python kafka_ha_logs_dump.py --hours 48
    python kafka_ha_logs_dump.py --base-url http://kafka-ui.sl-k8s.dns-shop.ru
"""

import argparse
import csv
import json
import logging
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

# ── Настройки ────────────────────────────────────────────────────────────────
KAFKA_UI_BASE = "http://kafka-ui.sl-k8s.dns-shop.ru"
CLUSTER       = "local"
TOPIC         = "ha_logs"
BATCH_SIZE    = 500          # сообщений за один запрос (макс. ~500 у kafka-ui)
REQUEST_TIMEOUT = 30         # секунды
RETRY_ATTEMPTS  = 3
RETRY_DELAY     = 5          # секунды между ретраями

OUTPUT_DIR = Path(__file__).parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── CSV-колонки (плоская структура outer + inner message) ─────────────────────
CSV_COLUMNS = [
    # outer
    "kafka_offset", "kafka_partition", "kafka_timestamp",
    "datacenter", "host", "file", "source_type", "outer_timestamp",
    # inner (HAProxy)
    "timestamp_haproxy", "frontend_name", "hostname", "frontend_port",
    "remote_ip", "backend_name", "server_name", "active_time_req",
    "responseStatus", "bytesSent", "requestType", "requestUrl",
    "queryString", "httpProtocol", "forwardedIP", "Host",
    "referer", "userAgent", "installationid",
]


# ── HTTP ──────────────────────────────────────────────────────────────────────
def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Accept": "application/json"})
    return s


def api_get(session: requests.Session, url: str, params: dict) -> dict:
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            r = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                return r.json()
            log.warning(f"HTTP {r.status_code} — {url} (попытка {attempt})")
        except requests.RequestException as e:
            log.warning(f"Ошибка запроса: {e} (попытка {attempt})")
        if attempt < RETRY_ATTEMPTS:
            time.sleep(RETRY_DELAY)
    raise RuntimeError(f"Не удалось получить ответ от {url} после {RETRY_ATTEMPTS} попыток")


# ── Метаданные топика ─────────────────────────────────────────────────────────
def get_partition_count(session: requests.Session, base_url: str) -> int:
    url = f"{base_url}/api/clusters/{CLUSTER}/topics/{TOPIC}"
    data = api_get(session, url, {})
    count = data.get("partitionCount") or len(data.get("partitions", [])) or 1
    log.info(f"Топик {TOPIC}: {count} партиций")
    return count


# ── Парсинг сообщения ─────────────────────────────────────────────────────────
def parse_message(msg: dict) -> dict | None:
    """Разбирает одно сообщение Kafka UI → плоский словарь."""
    raw_value = msg.get("content") or msg.get("value") or ""
    if isinstance(raw_value, dict):
        outer = raw_value
    else:
        try:
            outer = json.loads(raw_value)
        except (json.JSONDecodeError, TypeError):
            log.debug(f"Не удалось распарсить value offset={msg.get('offset')}")
            return None

    inner_raw = outer.get("message", "")
    if isinstance(inner_raw, dict):
        inner = inner_raw
    else:
        try:
            inner = json.loads(inner_raw)
        except (json.JSONDecodeError, TypeError):
            inner = {}

    return {
        # kafka meta
        "kafka_offset":    msg.get("offset"),
        "kafka_partition": msg.get("partition"),
        "kafka_timestamp": msg.get("timestamp"),
        # outer
        "datacenter":      outer.get("datacenter", ""),
        "host":            outer.get("host", ""),
        "file":            outer.get("file", ""),
        "source_type":     outer.get("source_type", ""),
        "outer_timestamp": outer.get("timestamp", ""),
        # inner (HAProxy)
        "timestamp_haproxy": inner.get("timestamp_haproxy", ""),
        "frontend_name":     inner.get("frontend_name", ""),
        "hostname":          inner.get("hostname", ""),
        "frontend_port":     inner.get("frontend_port", ""),
        "remote_ip":         inner.get("remote_ip", ""),
        "backend_name":      inner.get("backend_name", ""),
        "server_name":       inner.get("server_name", ""),
        "active_time_req":   inner.get("active_time_req", ""),
        "responseStatus":    inner.get("responseStatus", ""),
        "bytesSent":         inner.get("bytesSent", ""),
        "requestType":       inner.get("requestType", ""),
        "requestUrl":        inner.get("requestUrl", ""),
        "queryString":       inner.get("queryString", ""),
        "httpProtocol":      inner.get("httpProtocol", ""),
        "forwardedIP":       inner.get("forwardedIP", ""),
        "Host":              inner.get("Host", ""),
        "referer":           inner.get("referer", ""),
        "userAgent":         inner.get("userAgent", ""),
        "installationid":    inner.get("installationid", ""),
    }


# ── Основной сбор ─────────────────────────────────────────────────────────────
def fetch_partition(
    session: requests.Session,
    base_url: str,
    partition: int,
    since_ts_ms: int,
) -> list[dict]:
    """Скачивает все сообщения из одной партиции начиная с since_ts_ms."""
    url = f"{base_url}/api/clusters/{CLUSTER}/topics/{TOPIC}/messages"
    records = []
    seek_type = "TIMESTAMP"
    seek_to   = f"{partition}:{since_ts_ms}"
    total_fetched = 0

    log.info(f"  Партиция {partition}: старт с ts={since_ts_ms}")

    while True:
        params = {
            "seekType":   seek_type,
            "seekTo":     seek_to,
            "limit":      BATCH_SIZE,
            "keySerde":   "String",
            "valueSerde": "String",
        }
        data = api_get(session, url, params)

        messages = data if isinstance(data, list) else data.get("messages", data.get("content", []))
        if not messages:
            break

        batch_records = []
        for msg in messages:
            # пропускаем сообщения старше окна
            msg_ts = msg.get("timestamp", 0)
            if isinstance(msg_ts, str):
                try:
                    msg_ts = int(datetime.fromisoformat(msg_ts.rstrip("Z")).replace(tzinfo=timezone.utc).timestamp() * 1000)
                except ValueError:
                    msg_ts = 0
            if msg_ts < since_ts_ms:
                continue
            parsed = parse_message(msg)
            if parsed:
                batch_records.append(parsed)

        records.extend(batch_records)
        total_fetched += len(messages)

        # пагинация: следующий seek — offset последнего сообщения + 1
        last_offset = messages[-1].get("offset")
        if last_offset is None or len(messages) < BATCH_SIZE:
            break

        seek_type = "OFFSET"
        seek_to   = f"{partition}:{last_offset + 1}"

        log.info(f"  Партиция {partition}: получено {total_fetched}, следующий offset={last_offset + 1}")

    log.info(f"  Партиция {partition}: итого {len(records)} записей (из {total_fetched} сообщений)")
    return records


# ── Запись файлов ─────────────────────────────────────────────────────────────
def write_outputs(records: list[dict], run_ts: str) -> tuple[Path, Path]:
    ndjson_path = OUTPUT_DIR / f"ha_logs_{run_ts}.ndjson"
    csv_path    = OUTPUT_DIR / f"ha_logs_{run_ts}.csv"

    log.info(f"Запись NDJSON → {ndjson_path}")
    with open(ndjson_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    log.info(f"Запись CSV → {csv_path}")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    return ndjson_path, csv_path


# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="Дамп ha_logs из Kafka UI")
    p.add_argument("--base-url", default=KAFKA_UI_BASE, help="Base URL Kafka UI")
    p.add_argument("--hours",    type=int, default=24,   help="Глубина выгрузки в часах (default: 24)")
    return p.parse_args()


def main():
    args = parse_args()
    run_ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    since_dt = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    since_ms = int(since_dt.timestamp() * 1000)

    log.info(f"Kafka UI:  {args.base_url}")
    log.info(f"Топик:     {TOPIC}  |  Кластер: {CLUSTER}")
    log.info(f"Период:    последние {args.hours}ч (с {since_dt.isoformat()})")

    session = make_session()

    try:
        partitions = get_partition_count(session, args.base_url)
    except Exception as e:
        log.error(f"Не удалось получить метаданные топика: {e}")
        sys.exit(1)

    all_records: list[dict] = []
    for p in range(partitions):
        try:
            recs = fetch_partition(session, args.base_url, p, since_ms)
            all_records.extend(recs)
        except Exception as e:
            log.error(f"Ошибка при сборе партиции {p}: {e}")

    all_records.sort(key=lambda r: (r.get("kafka_timestamp") or "", r.get("kafka_offset") or 0))

    log.info(f"Всего записей: {len(all_records)}")

    if not all_records:
        log.warning("Нет данных для записи")
        sys.exit(0)

    ndjson_path, csv_path = write_outputs(all_records, run_ts)
    log.info(f"Готово.  NDJSON: {ndjson_path.stat().st_size / 1024 / 1024:.1f} MB")
    log.info(f"         CSV:    {csv_path.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
