"""
Dry-run: показывает что будет отправлено в CMDB из Lebowski /subsystems.
Запуск: python lebowski_is_dry_run.py
"""

import json
import re
import sys
import urllib3
from collections import defaultdict

import requests
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://lebowski.dns-shop.ru/services/hs/api"

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


def get_session(login: str, password: str) -> requests.Session:
    s = requests.Session()
    s.auth = HTTPBasicAuth(login, password)
    s.headers.update({"Accept": "application/json"})
    return s


def fetch(session, endpoint):
    try:
        r = session.get(f"{BASE_URL}/{endpoint}", timeout=30, verify=False)
        if r.status_code in (403, 404):
            return None
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [WARN] /{endpoint}: {e}")
        return None


def parse_role(name):
    n = name.lower()
    for pattern, role in _ROLE_PATTERNS:
        if re.search(pattern, n):
            return role
    return ''


def parse_env(name):
    n = name.lower()
    for pattern, env in _ENV_PATTERNS:
        if re.search(pattern, n):
            return env
    return ''


def location_prefix(name):
    return name.split('-')[0].upper() if name else ''


def print_section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def main():
    login = input("Логин: ").strip()
    password = input("Пароль: ").strip()
    session = get_session(login, password)

    limit = input("Показать первые N подсистем (Enter = все): ").strip()
    limit = int(limit) if limit.isdigit() else None

    print("\n→ Загружаем /subsystems...")
    resp = fetch(session, "subsystems")
    if not resp or resp.get("code") != 0:
        print("Не удалось получить /subsystems")
        sys.exit(1)

    subsystems = resp.get("data", [])
    if limit:
        subsystems = subsystems[:limit]
    print(f"  Подсистем: {len(subsystems)}")

    server_cache: dict = {}

    def get_server(srv_id):
        if srv_id in server_cache:
            return server_cache[srv_id]
        detail = fetch(session, f"server/{srv_id}")
        data = detail.get("data", {}) if detail and detail.get("code") == 0 else {}
        server_cache[srv_id] = data
        return data

    is_list = []
    components_list = []
    instances_map = {}

    print("→ Обрабатываем подсистемы...")
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

        seen: set = set()
        for srv in (sub.get("servers") or []):
            srv_id = srv.get("id", "")
            srv_name = (srv.get("name") or "").strip()
            if not srv_name or srv_id in seen:
                continue
            seen.add(srv_id)

            detail = get_server(srv_id)
            srv_owner = (detail.get("owner") or "").strip() or sub_owner
            srv_admin = (detail.get("team") or "").strip() or sub_team

            loc = location_prefix(srv_name)
            env = parse_env(srv_name)
            instance_name = f"{sub_name} | {loc}"
            key = (sub_name, loc)
            if key not in instances_map:
                instances_map[key] = {"name": instance_name, "IS_name": sub_name, "location": loc, "environment": env}
            elif not instances_map[key]["environment"] and env:
                instances_map[key]["environment"] = env

            components_list.append({
                "component_id": srv_id,
                "name": srv_name.lower(),
                "IS_name": sub_name,
                "instance_name": instance_name,
                "deployment_target": srv_name.lower(),
                "owner": srv_owner,
                "admin": srv_admin,
                "role": parse_role(srv_name),
            })

    instances_list = [
        {"instance_id": str(i), **inst}
        for i, inst in enumerate(instances_map.values(), start=1)
    ]

    # ── IS ──────────────────────────────────────────────────────────
    print_section(f"КЕ: IS  ({len(is_list)} записей)")
    print(f"  {'IS_id':<38} {'name':<40} {'owner':<35} admin")
    print(f"  {'-'*38} {'-'*40} {'-'*35} {'-'*30}")
    for r in is_list:
        print(f"  {r['IS_id']:<38} {r['name'][:39]:<40} {r['owner'][:34]:<35} {r['admin']}")

    # ── IS_COMPONENT ─────────────────────────────────────────────────
    print_section(f"КЕ: IS_COMPONENT  ({len(components_list)} записей)")
    print(f"  {'component_id':<38} {'name':<35} {'IS_name':<35} {'instance_name':<50} {'role':<12} {'owner':<30} admin")
    print(f"  {'-'*38} {'-'*35} {'-'*35} {'-'*50} {'-'*12} {'-'*30} {'-'*25}")
    for r in components_list:
        print(
            f"  {r['component_id']:<38} {r['name'][:34]:<35} {r['IS_name'][:34]:<35} "
            f"{r['instance_name'][:49]:<50} {r['role']:<12} {r['owner'][:29]:<30} {r['admin']}"
        )

    # ── IS_INSTANCE ──────────────────────────────────────────────────
    print_section(f"КЕ: IS_INSTANCE  ({len(instances_list)} записей)")
    print(f"  {'#':<6} {'name':<55} {'IS_name':<40} {'location':<10} environment")
    print(f"  {'-'*6} {'-'*55} {'-'*40} {'-'*10} {'-'*10}")
    for r in instances_list:
        print(f"  {r['instance_id']:<6} {r['name'][:54]:<55} {r['IS_name'][:39]:<40} {r['location']:<10} {r['environment']}")

    # ── Итого ────────────────────────────────────────────────────────
    print_section("ИТОГО")
    print(f"  IS            : {len(is_list)}")
    print(f"  IS_COMPONENT  : {len(components_list)}")
    print(f"  IS_INSTANCE   : {len(instances_list)}")
    print(f"  /server/ запросов (уник.): {len(server_cache)}")

    save = input("\nСохранить данные в JSON? (y/n): ").strip().lower()
    if save == 'y':
        out = {
            "IS": is_list,
            "IS_COMPONENT": components_list,
            "IS_INSTANCE": instances_list,
        }
        with open("lebowski_dry_run_output.json", "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print("  Сохранено в lebowski_dry_run_output.json")


if __name__ == "__main__":
    main()
