"""
Lebowski API — детальная карточка сервера через /server/{id}.
Запуск: python test_lebowski.py
"""

import json
import sys
import urllib3

import requests
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://lebowski.dns-shop.ru/services/hs/api"


def get_session(login: str, password: str) -> requests.Session:
    s = requests.Session()
    s.auth = HTTPBasicAuth(login, password)
    s.headers.update({"Accept": "application/json"})
    return s


def fetch(session: requests.Session, endpoint: str) -> dict | None:
    url = f"{BASE_URL}/{endpoint}"
    try:
        r = session.get(url, timeout=30, verify=False)
        if r.status_code == 401:
            print("  ОШИБКА: неверные логин/пароль")
            sys.exit(1)
        if r.status_code in (403, 404):
            return None
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"  ОШИБКА: {e}")
        return None


def main():
    print("=== Lebowski API — /server/{id} детальная карточка ===\n")

    login = input("Логин: ").strip()
    password = input("Пароль: ").strip()

    session = get_session(login, password)

    # --- Список серверов ---
    print("\n→ Загружаем список серверов...")
    data = fetch(session, "servers")
    if not data or data.get("code") != 0:
        print("Не удалось получить /servers")
        sys.exit(1)

    servers = data.get("data", [])
    print(f"  Серверов: {len(servers)}")

    # --- Детальная карточка первых N серверов ---
    N = 10
    print(f"\n{'=' * 70}")
    print(f"Детальные карточки первых {N} серверов (/server/{{id}})")
    print('=' * 70)

    detail_keys = set()

    for srv in servers[:N]:
        srv_id = srv["id"]
        srv_name = srv["name"]
        detail = fetch(session, f"server/{srv_id}")
        if detail is None:
            print(f"\n[{srv_name}] — /server/{srv_id} → 404/403")
            continue
        print(f"\n[{srv_name}]")
        print(json.dumps(detail, ensure_ascii=False, indent=2))
        if isinstance(detail, dict):
            detail_keys.update(detail.keys())
        elif isinstance(detail.get("data"), dict):
            detail_keys.update(detail["data"].keys())

    if detail_keys:
        print(f"\nВсе поля детальной карточки: {sorted(detail_keys)}")

    # --- Таблица: name | team | owner для первых N ---
    print(f"\n{'=' * 70}")
    print(f"{'СЕРВЕР':<35} {'TEAM':<30} {'OWNER'}")
    print('=' * 70)

    for srv in servers[:N]:
        srv_id = srv["id"]
        srv_name = srv["name"]
        detail = fetch(session, f"server/{srv_id}")
        if detail is None:
            print(f"{srv_name:<35} {'—':<30} —")
            continue

        # Пробуем разные варианты структуры ответа
        d = detail.get("data", detail) if isinstance(detail, dict) else detail
        owner = ""
        team = ""
        if isinstance(d, dict):
            owner_val = d.get("owner", {})
            team_val = d.get("team", {})
            owner = owner_val.get("name", "") if isinstance(owner_val, dict) else str(owner_val or "")
            team = team_val.get("name", "") if isinstance(team_val, dict) else str(team_val or "")

        print(f"{srv_name:<35} {team:<30} {owner}")


if __name__ == "__main__":
    main()
