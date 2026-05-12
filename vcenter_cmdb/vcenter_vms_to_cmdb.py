from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.models import Variable, Connection
from airflow.utils.dates import days_ago
import ssl
import re
import pymysql
import requests
from requests.auth import HTTPBasicAuth
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("airflow.task")

# === КОНФИГУРАЦИЯ ===
VCENTER_URL = Variable.get("VCENTER_URL")
VCENTER_USERNAME = Variable.get("VCENTER_USERNAME")
VCENTER_PASSWORD = Variable.get("VCENTER_PASSWORD")

LEBOWSKI_BASE_URL = "https://lebowski.dns-shop.ru/services/hs/api"
LEBOWSKI_CONN_ID = "lebowski_api"

GLPI_INSTANCES = ["GLPI", "ADM_GLPI", "ADM_RZN_GLPI"]

_SYSTEM_FOLDERS = {"vm", "datacenter", "cluster", "templates", "discovered virtual machine"}


# === СТРУКТУРА РЕЗУЛЬТАТА ПАРСИНГА АННОТАЦИИ ===
@dataclass
class AnnotationFields:
    owner_tag: Optional[str] = None   # явный тег Owner/Владелец/Команда
    admin_tag: Optional[str] = None   # явный тег Admin/Ответственный/Администратор
    email: Optional[str] = None       # первый @dns-shop.ru email
    login: Optional[str] = None       # первый логин вида Surname.XX


# === ПАРСИНГ АННОТАЦИИ ===
def parse_annotation(text: str) -> AnnotationFields:
    if not text or text == "N/A":
        return AnnotationFields()

    result = AnnotationFields()
    clean = re.sub(r'https?://\S+', '', text)

    owner_patterns = [
        r'(?:owner|владелец|команда разработки|ответственная команда|отдел)[:\s]+([^\n\r,;]{3,60})',
    ]
    admin_patterns = [
        r'(?:admin|администратор|ответственный|devops)[:\s]+([^\n\r,;]{2,60})',
    ]

    for pattern in owner_patterns:
        m = re.search(pattern, clean, re.IGNORECASE)
        if m:
            val = m.group(1).strip().strip('"\'')
            if len(val) > 2:
                result.owner_tag = val
                break

    for pattern in admin_patterns:
        m = re.search(pattern, clean, re.IGNORECASE)
        if m:
            val = m.group(1).strip().strip('"\'')
            if len(val) > 2:
                result.admin_tag = val
                break

    email_m = re.search(r'\b([\w.+-]+@dns-shop\.ru)\b', clean, re.IGNORECASE)
    if email_m:
        result.email = email_m.group(1).lower()

    login_m = re.search(r'\b([A-Z][a-z]{1,15}\.[A-Z]{1,3}\d?)\b', text)
    if login_m:
        candidate = login_m.group(1)
        if not re.search(r'[\\/]' + re.escape(candidate), text):
            result.login = candidate

    return result


# === ИЗВЛЕЧЕНИЕ ПАПКИ vCENTER ===
def get_vm_folder_path(vm) -> str:
    parts = []
    current = vm.parent
    while current is not None:
        if hasattr(current, 'name') and current.name:
            parts.append(current.name)
        current = getattr(current, 'parent', None)
    parts.reverse()
    return '/'.join(parts)


def extract_folder_department(folder_path: str) -> Optional[str]:
    """Возвращает название отдела из папки vCenter (первая папка после /vm/)."""
    parts = [p.strip() for p in folder_path.split('/') if p.strip()]
    try:
        vm_index = next(i for i, p in enumerate(parts) if p.lower() == 'vm')
        if vm_index + 1 < len(parts):
            name = parts[vm_index + 1].lstrip('_').strip()
            if name and len(name) > 2 and name.lower() not in _SYSTEM_FOLDERS:
                return name
    except StopIteration:
        pass
    return None


# === RESOLVE OWNER ===
def resolve_owner(
    folder_path: str,
    hostname: str,
    lebowski_lookup,
    ann: AnnotationFields,
) -> tuple[str, str]:
    """
    Возвращает (owner, source).
    Приоритет: папка vCenter → Lebowski team (/server/{id}) → тег аннотации → N/A
    """
    dept = extract_folder_department(folder_path)
    if dept:
        return dept, "folder"

    team = lebowski_lookup(hostname)
    if team:
        return team, "lebowski"

    if ann.owner_tag:
        return ann.owner_tag, "annotation"

    return "N/A", "none"


# === RESOLVE ADMIN ===
def resolve_admin(ann: AnnotationFields) -> tuple[str, str]:
    """
    Возвращает (admin, source).
    Приоритет: явный тег → email → логин → пусто
    """
    if ann.admin_tag:
        return ann.admin_tag, "tag"
    if ann.email:
        return ann.email, "email"
    if ann.login:
        return ann.login, "login"
    return "", "none"


# === LEBOWSKI ХЕЛПЕРЫ ===
def get_lebowski_session():
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
            logger.warning("Lebowski API: не найдены креды")
    session.headers.update({"Accept": "application/json"})
    return session


def fetch_lebowski_servers() -> dict:
    """Возвращает {server_name.lower(): server_obj} из /servers."""
    try:
        session = get_lebowski_session()
        r = session.get(f"{LEBOWSKI_BASE_URL}/servers", timeout=30, verify=False)
        logger.info(f"Lebowski /servers → HTTP {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if data.get("code") == 0 and isinstance(data.get("data"), list):
                result = {srv["name"].lower(): srv for srv in data["data"] if "name" in srv}
                logger.info(f"Lebowski /servers: {len(result)} серверов загружено")
                return result
        elif r.status_code == 403:
            logger.warning("Lebowski /servers: 403 Forbidden")
        else:
            logger.warning(f"Lebowski /servers: HTTP {r.status_code}")
    except Exception as e:
        logger.warning(f"Lebowski /servers: {e}")
    return {}


def _extract_lebowski_team(detail: dict) -> str:
    """Извлекает team.name из ответа /server/{id}."""
    d = detail.get("data", detail) if isinstance(detail, dict) else detail
    if not isinstance(d, dict):
        return ""
    team = d.get("team", {})
    if isinstance(team, dict):
        return str(team.get("name", "") or "").strip()
    return str(team or "").strip()


def make_lebowski_team_lookup(server_index: dict):
    """
    Возвращает функцию lookup(hostname) -> team_name.
    Детали сервера загружаются лениво через /server/{id} и кэшируются.
    """
    session = get_lebowski_session()
    cache: dict = {}

    def lookup(hostname: str) -> str:
        server_id = server_index.get(hostname.lower())
        if not server_id:
            return ""
        if server_id in cache:
            return cache[server_id]
        try:
            r = session.get(f"{LEBOWSKI_BASE_URL}/server/{server_id}", timeout=10, verify=False)
            logger.debug(f"Lebowski /server/{server_id} ({hostname}) → HTTP {r.status_code}")
            if r.status_code == 200:
                team = _extract_lebowski_team(r.json())
                cache[server_id] = team
                if team:
                    logger.info(f"Lebowski hit: '{hostname}' → team='{team}'")
                return team
        except Exception as e:
            logger.debug(f"Lebowski /server/{server_id}: {e}")
        cache[server_id] = ""
        return ""

    return lookup


# === GLPI ОС ===
def get_glpi_os_mapping() -> dict:
    hostname_to_os = {}
    for prefix in GLPI_INSTANCES:
        try:
            conn = pymysql.connect(
                host=Variable.get(f"{prefix}_HOST"),
                user=Variable.get(f"{prefix}_USER"),
                password=Variable.get(f"{prefix}_PASSWORD"),
                database=Variable.get(f"{prefix}_DB"),
                charset='utf8mb4',
            )
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.name, os.name
                    FROM glpi_computers c
                    LEFT JOIN glpi_items_operatingsystems io
                        ON io.items_id = c.id AND io.itemtype = 'Computer'
                    LEFT JOIN glpi_operatingsystems os
                        ON io.operatingsystems_id = os.id
                    WHERE c.name IS NOT NULL AND os.name IS NOT NULL
                """)
                for hostname, os_name in cur.fetchall():
                    hostname_to_os[hostname.lower()] = os_name
            conn.close()
        except Exception as e:
            logger.error(f"GLPI {prefix}: {e}")
    return hostname_to_os


# === ВСПОМОГАТЕЛЬНЫЕ ===
def extract_hostname_parts(full_hostname: str) -> tuple[str, str]:
    if not full_hostname or not full_hostname.strip():
        return "", ""
    hostname = full_hostname.strip().lower()
    if "." not in hostname:
        return hostname, ""
    parts = hostname.split(".")
    domain = ".".join(parts[-2:]) if len(parts) >= 2 else hostname
    shorthost = ".".join(parts[:-2]) if len(parts) > 2 else ""
    return shorthost, domain


def extract_role_env(comments: str, vm_name: str) -> tuple[str, str]:
    cl = (comments or "").lower()
    vl = vm_name.lower()

    env_m = re.search(r'\b(?:env|environment)\s*[:=]\s*(prod|test|dev|stage)\b', cl)
    environment = env_m.group(1) if env_m else None
    if environment is None:
        for kw, val in [("prod", "prod"), ("test", "test"), ("dev", "dev"),
                        ("develop", "dev"), ("stage", "stage")]:
            if kw in vl:
                environment = val
                break
        else:
            environment = "N/A"

    role_m = re.search(r'\brole\s*[:=]\s*(db|web|app|monitoring|user)\b', cl)
    role = role_m.group(1) if role_m else None
    if role is None:
        for kw, val in [("database", "db"), ("db", "db"), ("web", "web"),
                        ("application", "app"), ("app", "app"),
                        ("monitor", "monitoring"), ("user", "user")]:
            if kw in vl:
                role = val
                break
        else:
            role = "N/A"

    return role, environment


def get_cluster_for_vm(vm) -> str:
    if not getattr(vm, 'runtime', None) or not vm.runtime.host:
        return "N/A"
    current = vm.runtime.host.parent
    for _ in range(10):
        if current is None:
            break
        if isinstance(current, vim.ClusterComputeResource):
            return getattr(current, 'name', "CLUSTER_NO_NAME")
        current = getattr(current, 'parent', None)
    return "N/A"


# === ОСНОВНАЯ ЗАДАЧА ===
def collect_vcenter_vms_for_cmdb(**context):
    ti = context["ti"]
    logger.info("Запуск сбора VM из vCenter")

    hostname_to_os = get_glpi_os_mapping()
    logger.info(f"GLPI: {len(hostname_to_os)} записей ОС")

    lebowski_servers = fetch_lebowski_servers()
    lebowski_server_index = {k: v["id"] for k, v in lebowski_servers.items() if v.get("id")}
    lebowski_lookup = make_lebowski_team_lookup(lebowski_server_index)
    logger.info(f"Lebowski: {len(lebowski_servers)} серверов в индексе")

    vcenter_host = (
        VCENTER_URL.strip().lstrip("https://").lstrip("http://").split("/")[0].split(":")[0]
    )
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    si = None
    try:
        si = SmartConnect(host=vcenter_host, user=VCENTER_USERNAME, pwd=VCENTER_PASSWORD, sslContext=ssl_ctx)
        content = si.RetrieveContent()
        vms = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True).view
        total = len(vms)
        logger.info(f"Найдено {total} VM")

        results = []
        stats = {
            "owner_folder": 0, "owner_lebowski": 0, "owner_annotation": 0, "owner_none": 0,
            "admin_tag": 0, "admin_email": 0, "admin_login": 0, "admin_none": 0,
            "with_cluster": 0, "without_cluster": 0,
        }

        for i, vm in enumerate(vms, 1):
            if i % 500 == 0:
                logger.info(f"Обработано {i}/{total}...")

            hostname = getattr(vm, 'name', "N/A")
            vm_id = getattr(vm, '_moId', "N/A")

            raw_annotation = ""
            cpu = ram_gb = disk_gb = 0
            if vm.config:
                raw_annotation = getattr(vm.config, 'annotation', "") or ""
                hw = vm.config.hardware
                if hw:
                    cpu = getattr(hw, 'numCPU', 0)
                    ram_gb = (getattr(hw, 'memoryMB', 0) or 0) // 1024
                    for dev in (hw.device or []):
                        if isinstance(dev, vim.vm.device.VirtualDisk):
                            disk_gb += (dev.capacityInKB or 0) // 1024 // 1024

            comments = raw_annotation.strip() or "N/A"
            role, environment = extract_role_env(comments, hostname)

            hypervisor_obj = getattr(vm.runtime, 'host', None) if vm.runtime else None
            hypervisor = getattr(hypervisor_obj, 'name', "N/A") if hypervisor_obj else "N/A"
            if hypervisor == "N/A":
                leb = lebowski_servers.get(hostname.lower())
                if leb and leb.get("host", {}).get("name"):
                    hypervisor = leb["host"]["name"]

            folder_path = get_vm_folder_path(vm)
            ann = parse_annotation(raw_annotation)

            owner, owner_src = resolve_owner(folder_path, hostname, lebowski_lookup, ann)
            admin, admin_src = resolve_admin(ann)

            stats[f"owner_{owner_src}"] = stats.get(f"owner_{owner_src}", 0) + 1
            stats[f"admin_{admin_src}"] = stats.get(f"admin_{admin_src}", 0) + 1

            vm_cluster = get_cluster_for_vm(vm)
            if vm_cluster != "N/A":
                stats["with_cluster"] += 1
            else:
                stats["without_cluster"] += 1

            os_name = hostname_to_os.get(hostname.lower())
            if not os_name and vm.guest:
                os_name = getattr(vm.guest, 'guestFullName', None)
            if not os_name and vm.config:
                os_name = getattr(vm.config, 'guestFullName', None)
            os_name = str(os_name) if os_name else "N/A"

            shorthost, domain = extract_hostname_parts(hostname)

            results.append({
                "hostname": str(hostname),
                "shorthost": str(shorthost),
                "domain_name": str(domain),
                "vm_id": str(vm_id),
                "os_name": str(os_name),
                "hypervisor": str(hypervisor),
                "environment": str(environment),
                "cpu": str(cpu),
                "ram": str(ram_gb),
                "disk": str(disk_gb),
                "owner": str(owner),
                "admin": str(admin),
                "comments": str(comments),
                "vm_cluster": str(vm_cluster),
                "security_severity": "",
                "lebowski_filled": "owner" if owner_src == "lebowski" else "",
            })

        # === СТАТИСТИКА ===
        owner_found = total - stats["owner_none"]
        admin_found = total - stats["admin_none"]

        logger.info("=" * 60)
        logger.info("СТАТИСТИКА СБОРА:")
        logger.info(f"  Всего VM:        {total}")
        logger.info(
            f"  Owner заполнен:  {owner_found}/{total} ({owner_found / max(1, total) * 100:.1f}%)"
            f"  |  папка: {stats['owner_folder']}"
            f"  |  lebowski: {stats['owner_lebowski']}"
            f"  |  аннотация: {stats['owner_annotation']}"
        )
        logger.info(
            f"  Admin заполнен:  {admin_found}/{total} ({admin_found / max(1, total) * 100:.1f}%)"
            f"  |  тег: {stats['admin_tag']}"
            f"  |  email: {stats['admin_email']}"
            f"  |  логин: {stats['admin_login']}"
        )
        logger.info(f"  С кластером:     {stats['with_cluster']}")
        logger.info(f"  Без кластера:    {stats['without_cluster']}")
        logger.info("=" * 60)

        ti.xcom_push(key="VM", value=results)
        logger.info(f"Данные ({len(results)} VM) сохранены в XCom")

    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
        raise
    finally:
        if si:
            Disconnect(si)
            logger.info("Отключились от vCenter")


# === DAG ===
default_args = {
    'owner': 'Sevryuk.DA@dns-shop.ru',
    'retries': 1,
    'retry_delay': 300,
}

with DAG(
    dag_id="vcenter_vms_to_cmdb",
    default_args=default_args,
    schedule_interval="0 11 * * *",
    start_date=days_ago(1),
    catchup=False,
    tags=["inventory", "vcenter", "vm", "cmdb"],
) as dag:

    collect_task = PythonOperator(
        task_id="collect_vcenter_vms",
        python_callable=collect_vcenter_vms_for_cmdb,
    )

    trigger_cmdb = TriggerDagRunOperator(
        task_id="send_to_cmdb_vm",
        trigger_dag_id="cmdb_universal_uploader_v2",
        conf={
            "ke_type": "VM",
            "system": "vcenter",
            "data": "{{ ti.xcom_pull(task_ids='collect_vcenter_vms', key='VM') | tojson }}",
        },
    )

    collect_task >> trigger_cmdb
