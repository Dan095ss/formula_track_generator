import re

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
from airflow.api.common.trigger_dag import trigger_dag
from airflow.utils import timezone
import pymysql
from datetime import datetime
import logging
import ssl
import requests
from requests.auth import HTTPBasicAuth
from airflow.models import Connection
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from ldap3 import Server, Connection as LdapConnection, ALL, SUBTREE

default_args = {
    "owner": "Sevryuk.DA@dns-shop.ru",
    "retries": 2,
}

GLPI_INSTANCES = ["GLPI", "ADM_GLPI", "ADM_RZN_GLPI"]
LEBOWSKI_BASE_URL = "https://lebowski.dns-shop.ru/services/hs/api"
LEBOWSKI_CONN_ID = "lebowski_api"
VCENTER_URL = Variable.get("VCENTER_URL")
VCENTER_USERNAME = Variable.get("VCENTER_USERNAME")
VCENTER_PASSWORD = Variable.get("VCENTER_PASSWORD")


def get_short_hostname(hostname):
    if not hostname or not isinstance(hostname, str):
        return ""
    return hostname.split('.')[0].lower()


def extract_hostname_parts(full_hostname):
    if not full_hostname or not isinstance(full_hostname, str) or not full_hostname.strip():
        return "", ""

    hostname = full_hostname.strip().lower()

    if "." not in hostname:
        return hostname, ""

    parts = hostname.split(".")

    if len(parts) >= 2:
        domain = ".".join(parts[-2:])
        shorthost = ".".join(parts[:-2]) if len(parts) > 2 else ""
    else:
        domain = hostname
        shorthost = ""

    return shorthost, domain


def extract_role_env_from_comments_or_hostname(comments, hostname):
    comments_lower = (comments or "").lower()
    hostname_lower = hostname.lower()

    env_match = re.search(r'\b(env|environment)\s*[:=]\s*(prod|test|dev)\b', comments_lower)
    environment = env_match.group(2) if env_match else None

    role_match = re.search(r'\brole\s*[:=]\s*(db|web|app|monitoring|user)\b', comments_lower)
    role = role_match.group(1) if role_match else None

    if environment is None:
        if "prod" in hostname_lower:
            environment = "prod"
        elif "test" in hostname_lower:
            environment = "test"
        elif "dev" in hostname_lower or "develop" in hostname_lower:
            environment = "dev"
        else:
            environment = "N/A"

    if role is None:
        if "db" in hostname_lower or "database" in hostname_lower:
            role = "db"
        elif "web" in hostname_lower:
            role = "web"
        elif "app" in hostname_lower or "application" in hostname_lower:
            role = "app"
        elif "monitor" in hostname_lower:
            role = "monitoring"
        elif "user" in hostname_lower:
            role = "user"
        else:
            role = "N/A"

    return role, environment



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
            logging.warning("Lebowski API: не найдены креды")
    session.headers.update({"Accept": "application/json"})
    return session


def _extract_lebowski_team(detail: dict) -> str:
    d = detail.get("data", detail) if isinstance(detail, dict) else detail
    if not isinstance(d, dict):
        return ""
    team = d.get("team", {})
    if isinstance(team, dict):
        return str(team.get("name", "") or "").strip()
    return str(team or "").strip()


def make_lebowski_team_lookup(server_index: dict):
    """Возвращает lookup(hostname) -> team_name. Результаты кэшируются."""
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
            if r.status_code == 200:
                team = _extract_lebowski_team(r.json())
                cache[server_id] = team
                if team:
                    logging.info(f"Lebowski hit: '{hostname}' → team='{team}'")
                return team
        except Exception as e:
            logging.debug(f"Lebowski /server/{server_id}: {e}")
        cache[server_id] = ""
        return ""

    return lookup


def fetch_lebowski_server_index() -> dict:
    """Возвращает {server_name.lower(): server_id} из /servers."""
    result = {}
    try:
        session = get_lebowski_session()
        r = session.get(f"{LEBOWSKI_BASE_URL}/servers", timeout=30, verify=False)
        logging.info(f"Lebowski /servers → HTTP {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if data.get("code") == 0 and isinstance(data.get("data"), list):
                for srv in data["data"]:
                    if srv.get("name") and srv.get("id"):
                        result[srv["name"].lower()] = srv["id"]
                logging.info(f"Lebowski /servers: {len(result)} серверов в индексе")
        elif r.status_code == 403:
            logging.warning("Lebowski /servers: 403 Forbidden")
        else:
            logging.warning(f"Lebowski /servers: HTTP {r.status_code}")
    except Exception as e:
        logging.warning(f"Lebowski /servers: {e}")
    return result


def make_ad_group_lookup():
    """
    Возвращает функцию lookup(username) -> group_name.
    Берёт первую группу из memberOf для пользователя (sAMAccountName).
    Результаты кэшируются на время DAG run.
    """
    cache: dict = {}
    try:
        ad_server = Variable.get("AD_SERVER")
        ad_user = Variable.get("AD_USER")
        ad_password = Variable.get("AD_PASSWORD")
        ad_base_dn = Variable.get("AD_BASE_DN")
    except Exception as e:
        logging.warning(f"AD lookup: не удалось получить переменные: {e}")
        return lambda username: ""

    try:
        server = Server(ad_server, get_info=ALL)
        ldap_conn = LdapConnection(server, ad_user, ad_password, auto_bind=True)
        logging.info(f"AD lookup: подключение к {ad_server} успешно")
    except Exception as e:
        logging.warning(f"AD lookup: не удалось подключиться к {ad_server}: {e}")
        return lambda username: ""

    def lookup(username: str) -> str:
        if not username or username == "N/A":
            return ""
        username = strip_domain(username)
        key = username.lower()
        if key in cache:
            return cache[key]
        try:
            ldap_conn.search(
                search_base=ad_base_dn,
                search_filter=f"(sAMAccountName={username})",
                search_scope=SUBTREE,
                attributes=["memberOf"],
            )
            if ldap_conn.entries:
                member_of = ldap_conn.entries[0].memberOf.values
                if member_of:
                    first_dn = member_of[0]
                    cn_match = re.match(r"CN=([^,]+)", first_dn, re.IGNORECASE)
                    group = cn_match.group(1) if cn_match else first_dn
                    cache[key] = group
                    logging.info(f"AD: '{username}' → group='{group}'")
                    return group
                logging.debug(f"AD: '{username}' найден, но memberOf пуст")
            else:
                logging.debug(f"AD: '{username}' не найден в каталоге")
        except Exception as e:
            logging.warning(f"AD lookup для '{username}' завершился с ошибкой: {e}")
        cache[key] = ""
        return ""

    return lookup


def resolve_owner(hostname: str, group: str, user: str, contact: str, lebowski_lookup, ad_lookup) -> tuple[str, str]:
    """Fallback-цепочка для owner: Lebowski → GLPI group → AD(user) → user → contact.
    Возвращает (значение, источник)."""
    if hostname:
        team = lebowski_lookup(get_short_hostname(hostname))
        if team:
            return team, "lebowski"
    if group and group != "N/A":
        return group, "glpi_group"
    if user and user != "N/A":
        user = strip_domain(user)
        ad_group = ad_lookup(user)
        if ad_group:
            return ad_group, "ad"
        return user, "user"
    if contact and contact.strip() and contact.strip() != "N/A":
        contact = strip_domain(contact.strip())
        ad_group = ad_lookup(contact)
        if ad_group:
            return ad_group, "ad_contact"
        return contact, "contact"
    return "N/A", "na"


def resolve_admin(group: str, user: str, ad_lookup) -> tuple[str, str]:
    """Fallback-цепочка для admin: GLPI group → AD(user) → user.
    Возвращает (значение, источник)."""
    if group and group != "N/A":
        return group, "glpi_group"
    if user and user != "N/A":
        user = strip_domain(user)
        ad_group = ad_lookup(user)
        if ad_group:
            return ad_group, "ad"
        return user, "user"
    return "", "na"


def strip_domain(username: str) -> str:
    """Sevryuk.DA@PARTNER → Sevryuk.DA"""
    return username.split("@")[0].strip() if username else username


def normalize_for_conn(os_name, os_version):
    name_part = re.sub(r'\s+', ' ', (os_name or "").strip().lower())
    version_part = re.sub(r'\s+', ' ', (os_version or "").strip().lower())

    return f"{name_part}|{version_part}" if version_part else f"{name_part}|"


def get_cluster_for_host(host):
    if not hasattr(host, 'parent') or not host.parent:
        return "N/A"
    parent = host.parent
    if isinstance(parent, vim.ClusterComputeResource):
        return getattr(parent, 'name', "CLUSTER_NO_NAME")
    return "N/A"


def fetch_vcenter_clusters(hostnames):
    logger = logging.getLogger("airflow.task")
    shortname_to_cluster = {}

    if not hostnames:
        logger.info("Нет ESXi-хостов для обогащения кластерами")
        return shortname_to_cluster

    logger.info(f"Попытка обогатить {len(hostnames)} ESXi-хостов данными о кластерах из vCenter")

    search_set = {get_short_hostname(h) for h in hostnames if h}
    logger.info(f"Короткие имена для поиска в vCenter: {sorted(search_set)}")

    try:
        vcenter_host = VCENTER_URL.strip()
        for prefix in ["https://", "http://"]:
            if vcenter_host.startswith(prefix):
                vcenter_host = vcenter_host[len(prefix):]
        vcenter_host = vcenter_host.split("/")[0].split(":")[0].strip()

        context_ssl = ssl.create_default_context()
        context_ssl.check_hostname = False
        context_ssl.verify_mode = ssl.CERT_NONE

        si = SmartConnect(
            host=vcenter_host,
            user=VCENTER_USERNAME,
            pwd=VCENTER_PASSWORD,
            sslContext=context_ssl
        )
        logger.info("Успешное подключение к vCenter")

        content = si.RetrieveContent()
        container_view = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.HostSystem], True
        )
        hosts = container_view.view
        logger.info(f"Найдено {len(hosts)} ESXi-хостов в vCenter")

        matched = 0
        for host in hosts:
            host_name = getattr(host, 'name', "").strip()
            if not host_name:
                continue

            host_short_name = get_short_hostname(host_name)

            if host_short_name in search_set:
                cluster = get_cluster_for_host(host)
                shortname_to_cluster[host_short_name] = cluster
                logger.debug(f"Сопоставлен хост '{host_name}' (короткое: '{host_short_name}') -> кластер '{cluster}'")
                matched += 1

        logger.info(f"Сопоставлено кластеров: {matched} из {len(search_set)}")
        Disconnect(si)
        logger.info("Отключение от vCenter завершено")

    except Exception as e:
        logger.warning(f"Не удалось получить данные о кластерах: {e}. Продолжаем без обогащения.")

    return shortname_to_cluster


def collect_glpi_data(**context):
    ti = context["ti"]
    all_data = []
    esxi_hostnames = []
    owner_sources: dict[str, int] = {}
    admin_sources: dict[str, int] = {}

    lebowski_server_index = fetch_lebowski_server_index()
    lebowski_lookup = make_lebowski_team_lookup(lebowski_server_index)
    logging.info(f"Lebowski: {len(lebowski_server_index)} серверов в индексе")
    ad_lookup = make_ad_group_lookup()

    for glpi_prefix in GLPI_INSTANCES:
        logging.info(f"Сбор данных из инстанса: {glpi_prefix}")

        try:
            conn = pymysql.connect(
                host=Variable.get(f"{glpi_prefix}_HOST"),
                user=Variable.get(f"{glpi_prefix}_USER"),
                password=Variable.get(f"{glpi_prefix}_PASSWORD"),
                database=Variable.get(f"{glpi_prefix}_DB"),
                charset='utf8mb4'
            )
        except Exception as e:
            logging.error(f"Не удалось подключиться к {glpi_prefix}: {e}")
            continue

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        c.name AS hostname,
                        ov.name AS os_name,
                        osv.name AS os_version,
                        NULLIF(TRIM(g_own.name), '')  AS owner_group,
                        NULLIF(TRIM(u.name), '')       AS owner_user,
                        NULLIF(TRIM(c.contact), '')    AS owner_contact,
                        NULLIF(TRIM(g_tech.name), '')  AS admin_group,
                        NULLIF(TRIM(u_tech.name), '')  AS admin_user,
                        COALESCE(a.remote_addr, 'OBAMA') AS ip,
                        COALESCE(c.serial, 'N/A') AS serial,
                        COALESCE(dc.name, 'N/A') AS srv_name,
                        COALESCE(
                            (SELECT dcr.name
                             FROM glpi_dcrooms AS dcr
                             WHERE dcr.datacenters_id = c.locations_id
                             ORDER BY dcr.id
                             LIMIT 1),
                            'N/A'
                        ) AS srv_location,
                        c.date_mod AS last_update,
                        ct.name AS computer_type,
                        c.comment AS comments,
                        COALESCE(
                            (SELECT SUM(COALESCE(idp.nbcores, dp.nbcores_default, 0))
                             FROM glpi_items_deviceprocessors AS idp
                             JOIN glpi_deviceprocessors AS dp ON idp.deviceprocessors_id = dp.id
                             WHERE idp.items_id = c.id AND idp.itemtype = 'Computer'),
                            0
                        ) AS cpu_cores,
                        COALESCE(
                            (SELECT ROUND(SUM(idm.size) / 1024)
                             FROM glpi_items_devicememories AS idm
                             WHERE idm.items_id = c.id AND idm.itemtype = 'Computer'),
                            0
                        ) AS ram_gb,
                        COALESCE(
                            (SELECT ROUND(SUM(idhd.capacity) / 1024)
                             FROM glpi_items_deviceharddrives AS idhd
                             WHERE idhd.items_id = c.id AND idhd.itemtype = 'Computer'),
                            0
                        ) AS disk_gb
                    FROM glpi_computers AS c
                    LEFT JOIN glpi_datacenters AS dc ON c.locations_id = dc.id
                    LEFT JOIN glpi_items_operatingsystems AS io
                        ON io.items_id = c.id AND io.itemtype = 'Computer'
                    LEFT JOIN glpi_operatingsystems AS ov
                        ON io.operatingsystems_id = ov.id
                    LEFT JOIN glpi_operatingsystemversions AS osv
                        ON io.operatingsystemversions_id = osv.id
                    LEFT JOIN glpi_users AS u
                        ON c.users_id = u.id
                    LEFT JOIN glpi_groups AS g_own
                        ON c.groups_id = g_own.id
                    LEFT JOIN glpi_users AS u_tech
                        ON c.users_id_tech = u_tech.id
                    LEFT JOIN glpi_groups AS g_tech
                        ON c.groups_id_tech = g_tech.id
                    LEFT JOIN glpi_agents AS a
                        ON c.id = a.items_id AND a.itemtype = 'Computer'
                    LEFT JOIN glpi_computertypes AS ct
                        ON c.computertypes_id = ct.id
                    WHERE c.is_deleted = 0
                """)
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                raw_data = [dict(zip(columns, row)) for row in rows]

                logging.info(f"Из {glpi_prefix} получено {len(raw_data)} записей")

                VM_TYPES = {"Hyper-V", "VMware", "Xen", "VirtualBox", "Docker"}

                for item in raw_data:
                    comp_type = (item.get("computer_type") or "").strip()
                    hostname_lower = (item["hostname"] or "").lower()
                    os_name_raw = item.get("os_name") or ""
                    os_version = item.get("os_version") or ""

                    os_conn_name = normalize_for_conn(os_name_raw, os_version)

                    os_name_lower = os_name_raw.lower()

                    if "esxi" in hostname_lower or "hyperv" in hostname_lower or "xenserver" in hostname_lower or "hyper-v" in hostname_lower:
                        host_type = "esxi"
                    elif "esxi" in os_name_lower or ("vmware" in os_name_lower and "esxi" in os_name_lower):
                        host_type = "esxi"
                    elif comp_type in VM_TYPES:
                        host_type = "virtual_machine"
                    else:
                        host_type = "physical"

                    if host_type == "virtual_machine":
                        continue

                    full_hostname = (item["hostname"] or "").strip()
                    shorthost, domain = extract_hostname_parts(full_hostname)
                    comments = item.get("comments", "") or ""

                    role, environment = extract_role_env_from_comments_or_hostname(comments, full_hostname)

                    owner, owner_src = resolve_owner(
                        full_hostname,
                        item.get("owner_group") or "",
                        item.get("owner_user") or "",
                        item.get("owner_contact") or "",
                        lebowski_lookup,
                        ad_lookup,
                    )
                    admin, admin_src = resolve_admin(
                        item.get("admin_group") or "",
                        item.get("admin_user") or "",
                        ad_lookup,
                    )
                    owner_sources[owner_src] = owner_sources.get(owner_src, 0) + 1
                    admin_sources[admin_src] = admin_sources.get(admin_src, 0) + 1

                    clean_item = {
                        "hostname": full_hostname,
                        "shorthost": shorthost,
                        "domain_name": domain,
                        "os_name": os_conn_name,
                        "owner": owner,
                        "admin": admin if admin != "N/A" else "",
                        "source": glpi_prefix,
                        "hardware_type": host_type,
                        #"srv_name": item["srv_name"],
                        "location": item["srv_location"],
                        "serial": item["serial"],
                        "comments": comments,
                        "environment": environment,
                        "host_cluster": None,
                        "role": role,
                        "business_severity": "",
                        "security_severity": "",
                        "last_update": (
                            item["last_update"].strftime("%Y-%m-%d %H:%M:%S")
                            if isinstance(item["last_update"], datetime)
                            else "N/A"
                        ),
                        "cpu": str(item.get("cpu_cores") or 0),
                        "ram": str(item.get("ram_gb") or 0),
                        "disk": str(item.get("disk_gb") or 0),
                    }

                    if host_type == "esxi" and full_hostname:
                        esxi_hostnames.append(full_hostname)

                    all_data.append(clean_item)

        except Exception as e:
            logging.error(f"Ошибка при обработке {glpi_prefix}: {e}")
        finally:
            conn.close()

    if esxi_hostnames:
        logging.info(f"Обнаружено {len(esxi_hostnames)} ESXi-хостов. Запрашиваем кластеры из vCenter...")
        logging.debug(f"Полные имена ESXi для обогащения: {esxi_hostnames}")

        cluster_mapping = fetch_vcenter_clusters(esxi_hostnames)

        enriched_count = 0
        for item in all_data:
            if item["hardware_type"] == "esxi" and item["hostname"]:
                short_name = get_short_hostname(item["hostname"])
                cluster = cluster_mapping.get(short_name, "N/A")
                item["host_cluster"] = cluster
                enriched_count += 1
                if cluster != "N/A":
                    logging.debug(
                        f"Обогащён хост '{item['hostname']}' (короткое: '{short_name}') -> кластер '{cluster}'")

        logging.info(f"Обогащено кластерами: {enriched_count} ESXi из {len(esxi_hostnames)}")
    else:
        logging.info("ESXi-хостов для обогащения не обнаружено")

    logging.info(f"Всего собрано {len(all_data)} хостов (физические + ESXi)")
    logging.info(f"Owner sources: { {k: owner_sources[k] for k in sorted(owner_sources)} }")
    logging.info(f"Admin sources: { {k: admin_sources[k] for k in sorted(admin_sources)} }")
    ti.xcom_push(key="glpi_data", value=all_data)


def prepare_and_trigger_cmdb(**context):
    ti = context['task_instance']
    data = ti.xcom_pull(task_ids='collect_glpi_data', key='glpi_data')
    logging.info(f"Подготовка CMDB: записей = {len(data) if data else 0}")

    if not isinstance(data, list):
        raise ValueError(f"Ожидался список, получен {type(data)}")

    conf = {
        "ke_type": "HOST",
        "system": "glpi_multi",
        "data": data
    }

    dag_run = trigger_dag(
        dag_id='cmdb_universal_uploader_v2',
        run_id=f"triggered__glpi_{timezone.utcnow().strftime('%Y%m%dT%H%M%S')}",
        conf=conf,
        replace_microseconds=False
    )
    logging.info(f"Запущен DAG 'cmdb_universal_uploader_v2' с run_id={dag_run.run_id}")


with DAG(
        dag_id='glpi_hosts_scan',
        default_args=default_args,
        schedule_interval='0 11 * * *',
        start_date=days_ago(1),
        catchup=False,
        tags=['inventory', 'glpi', 'hosts_only', 'physical', 'esxi'],
) as dag:
    collect_task = PythonOperator(
        task_id='collect_glpi_data',
        python_callable=collect_glpi_data,
    )

    trigger_task = PythonOperator(
        task_id='trigger_cmdb_upload',
        python_callable=prepare_and_trigger_cmdb,
    )

    collect_task >> trigger_task
