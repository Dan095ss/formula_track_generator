#!/usr/bin/env python3
"""
Снапшот топика ha_logs через Kafka UI REST API.

ОГРАНИЧЕНИЕ ПЛАТФОРМЫ:
  Kafka UI v1.0 (эта инсталляция) поддерживает максимум 500 сообщений за запрос.
  OFFSET/TIMESTAMP-пагинация недоступна — сервер возвращает 500.
  Брокеры доступны только по внутреннему k8s DNS (.svc) — прямое подключение невозможно.
  Скрипт получает до 500 актуальных сообщений из текущей позиции Kafka UI consumer.

Запуск:
    python kafka_ha_logs_dump.py
    python kafka_ha_logs_dump.py --limit 500
    python kafka_ha_logs_dump.py --base-url https://kafka-ui.sl-k8s.dns-shop.ru
"""

import argparse
import csv
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── Настройки ────────────────────────────────────────────────────────────────
KAFKA_UI_BASE   = "https://kafka-ui.sl-k8s.dns-shop.ru"
CLUSTER         = "local"
TOPIC           = "ha_logs"
MAX_LIMIT       = 500          # жёсткий предел API (>500 → откат к 100)
REQUEST_TIMEOUT = 60
RETRY_ATTEMPTS  = 3
RETRY_DELAY     = 5

OUTPUT_DIR = Path(__file__).parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── CSV-колонки ───────────────────────────────────────────────────────────────
CSV_COLUMNS = [
    "kafka_offset", "kafka_partition", "kafka_timestamp",
    "datacenter", "host", "file", "source_type", "outer_timestamp",
    "timestamp_haproxy", "frontend_name", "hostname", "frontend_port",
    "remote_ip", "backend_name", "server_name", "active_time_req",
    "responseStatus", "bytesSent", "requestType", "requestUrl",
    "queryString", "httpProtocol", "forwardedIP", "Host",
    "referer", "userAgent", "installationid",
]


# ── HTTP ──────────────────────────────────────────────────────────────────────
def make_session() -> requests.Session:
    s = requests.Session()
    s.trust_env = False  # обходим корпоративный HTTPS_PROXY
    return s


def fetch_sse(session: requests.Session, url: str, params: dict) -> tuple[list[dict], dict]:
    """Читает SSE-стрим, возвращает (messages, consuming_stats)."""
    import time
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            r = session.get(url, params=params, timeout=REQUEST_TIMEOUT,
                            verify=False, stream=True)
            if r.status_code != 200:
                log.warning(f"HTTP {r.status_code} (попытка {attempt}): {r.text[:200]}")
                if attempt < RETRY_ATTEMPTS:
                    time.sleep(RETRY_DELAY)
                continue

            messages, consuming = [], {}
            for raw in r.iter_lines():
                if not raw:
                    continue
                line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
                if not line.startswith("data:"):
                    continue
                try:
                    ev = json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    continue
                t = ev.get("type")
                if t == "MESSAGE" and ev.get("message"):
                    messages.append(ev["message"])
                elif t == "DONE":
                    consuming = ev.get("consuming") or {}
                    break
            return messages, consuming

        except requests.RequestException as e:
            log.warning(f"Ошибка SSE: {e} (попытка {attempt})")
            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_DELAY)
    raise RuntimeError(f"Не удалось получить данные после {RETRY_ATTEMPTS} попыток")


# ── Метаданные топика ─────────────────────────────────────────────────────────
def get_topic_meta(session: requests.Session, base_url: str) -> dict:
    import time
    url = f"{base_url}/api/clusters/{CLUSTER}/topics/{TOPIC}"
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            r = session.get(url, verify=False, timeout=REQUEST_TIMEOUT,
                            headers={"Accept": "application/json"})
            if r.status_code == 200:
                return r.json()
            log.warning(f"Метаданные: HTTP {r.status_code}")
        except Exception as e:
            log.warning(f"Метаданные: {e}")
        if attempt < RETRY_ATTEMPTS:
            time.sleep(RETRY_DELAY)
    raise RuntimeError("Не удалось получить метаданные топика")


# ── Парсинг сообщения ─────────────────────────────────────────────────────────
def parse_message(msg: dict) -> dict | None:
    raw = msg.get("content") or msg.get("value") or ""
    if isinstance(raw, dict):
        outer = raw
    else:
        try:
            outer = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None

    inner_raw = outer.get("message", "")
    inner = inner_raw if isinstance(inner_raw, dict) else {}
    if not inner:
        try:
            inner = json.loads(inner_raw)
        except (json.JSONDecodeError, TypeError):
            inner = {}

    return {
        "kafka_offset":      msg.get("offset"),
        "kafka_partition":   msg.get("partition"),
        "kafka_timestamp":   msg.get("timestamp"),
        "datacenter":        outer.get("datacenter", ""),
        "host":              outer.get("host", ""),
        "file":              outer.get("file", ""),
        "source_type":       outer.get("source_type", ""),
        "outer_timestamp":   outer.get("timestamp", ""),
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


# ── Запись файлов ─────────────────────────────────────────────────────────────
def write_outputs(records: list[dict], run_ts: str) -> tuple[Path, Path]:
    ndjson_path = OUTPUT_DIR / f"ha_logs_{run_ts}.ndjson"
    csv_path    = OUTPUT_DIR / f"ha_logs_{run_ts}.csv"

    with open(ndjson_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    return ndjson_path, csv_path


# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="Снапшот ha_logs из Kafka UI (макс. 500 сообщений)")
    p.add_argument("--base-url", default=KAFKA_UI_BASE)
    p.add_argument("--limit",    type=int, default=MAX_LIMIT,
                   help=f"Кол-во сообщений (max {MAX_LIMIT})")
    return p.parse_args()


def main():
    args = parse_args()
    limit   = min(args.limit, MAX_LIMIT)
    run_ts  = datetime.now().strftime("%Y%m%d_%H%M%S")

    log.info(f"Kafka UI:  {args.base_url}")
    log.info(f"Топик:     {TOPIC}  |  Кластер: {CLUSTER}")
    log.info(f"Лимит:     {limit} сообщений (API max={MAX_LIMIT})")

    session = make_session()

    # Метаданные топика
    try:
        meta = get_topic_meta(session, args.base_url)
        partitions = meta.get("partitions", [])
        log.info(f"Партиций: {len(partitions)}")
        for p in partitions:
            log.info(f"  p={p['partition']}: offsetMin={p['offsetMin']} offsetMax={p['offsetMax']} "
                     f"(~{p['offsetMax'] - p['offsetMin']:,} сообщений в топике)")
    except Exception as e:
        log.error(f"Метаданные: {e}")
        sys.exit(1)

    # Один запрос — BEGINNING, все партиции разом
    url = f"{args.base_url}/api/clusters/{CLUSTER}/topics/{TOPIC}/messages"
    params = {
        "seekType":   "BEGINNING",
        "limit":      limit,
        "keySerde":   "String",
        "valueSerde": "String",
    }

    log.info("Получение сообщений...")
    try:
        raw_msgs, stats = fetch_sse(session, url, params)
    except RuntimeError as e:
        log.error(str(e))
        sys.exit(1)

    log.info(f"Получено: {len(raw_msgs)} сообщений "
             f"(сервер прочитал внутренне: {stats.get('messagesConsumed', '?')}, "
             f"байт: {stats.get('bytesConsumed', '?')})")

    records = [r for msg in raw_msgs if (r := parse_message(msg)) is not None]
    records.sort(key=lambda r: (r.get("kafka_timestamp") or "", r.get("kafka_offset") or 0))

    if not records:
        log.warning("Нет данных для записи")
        sys.exit(0)

    ts_first = records[0].get("kafka_timestamp", "?")
    ts_last  = records[-1].get("kafka_timestamp", "?")
    log.info(f"Временной диапазон: {ts_first} → {ts_last}")

    ndjson_path, csv_path = write_outputs(records, run_ts)
    log.info(f"NDJSON: {ndjson_path}  ({ndjson_path.stat().st_size / 1024:.1f} KB)")
    log.info(f"CSV:    {csv_path}  ({csv_path.stat().st_size / 1024:.1f} KB)")
    log.info("")
    log.warning("ВНИМАНИЕ: Kafka UI v1.0 ограничивает выгрузку до 500 сообщений.")
    log.warning("Для полного дампа 24ч нужен прямой доступ к брокерам (kafka-python).")


if __name__ == "__main__":
    main()
