"""
Обновляет attr3 в справочнике MRU через CMDB брокер.
Запуск: python mru_attr3_update.py
"""

import json
import uuid
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CMDB_URL = "https://cmdb.dns-shop.ru/broker/cmdb-sources"
REF_TYPE = "MRU"
SYSTEM = "manual"

MRU_DATA = [
    {"name": "MRU_ADM",  "attr1": "2",  "attr3": "ADM"},
    {"name": "MRU_DV",   "attr1": "10", "attr3": "DV"},
    {"name": "MRU_MSK",  "attr1": "5",  "attr3": "MOW"},
    {"name": "MRU_MSK2", "attr1": "6",  "attr3": "MOW2"},
    {"name": "MRU_URAL", "attr1": "3",  "attr3": "URAL"},
]


def send(payload: dict) -> bool:
    try:
        resp = requests.post(
            CMDB_URL,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            verify=False,
            timeout=30,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    run_uuid = str(uuid.uuid4())
    print(f"UUID сессии: {run_uuid}\n")

    ok = 0
    for item in MRU_DATA:
        payload = {
            "is_reference_data": True,
            "system": SYSTEM,
            "action": "insert",
            "uuid": run_uuid,
            "data": {
                "citem_type_name": REF_TYPE,
                "attrs": item,
            },
        }
        success = send(payload)
        status = "OK" if success else "FAIL"
        print(f"  [{status}] {item['name']} → attr3={item['attr3']}")
        if success:
            ok += 1

    print(f"\nГотово: {ok}/{len(MRU_DATA)} записей обновлено")


if __name__ == "__main__":
    main()
