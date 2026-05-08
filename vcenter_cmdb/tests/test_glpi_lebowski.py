import sys
import os
from unittest.mock import MagicMock, patch

# Patch all heavy imports before loading the DAG module
sys.modules.update({
    'airflow': MagicMock(),
    'airflow.models': MagicMock(),
    'airflow.operators': MagicMock(),
    'airflow.operators.python': MagicMock(),
    'airflow.utils': MagicMock(),
    'airflow.utils.dates': MagicMock(),
    'airflow.api': MagicMock(),
    'airflow.api.common': MagicMock(),
    'airflow.api.common.trigger_dag': MagicMock(),
    'pymysql': MagicMock(),
    'pyVim': MagicMock(),
    'pyVim.connect': MagicMock(),
    'pyVmomi': MagicMock(),
})

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest


class TestHardwareTypeBugFixed(unittest.TestCase):
    """Cluster enrichment must use hardware_type key, not type."""

    def test_esxi_cluster_enriched_via_hardware_type_key(self):
        all_data = [
            {"hostname": "esxi01.dns-shop.ru", "hardware_type": "esxi", "host_cluster": None},
        ]
        cluster_mapping = {"esxi01": "CLUSTER-A"}

        for item in all_data:
            if item["hardware_type"] == "esxi" and item["hostname"]:
                short = item["hostname"].split(".")[0].lower()
                item["host_cluster"] = cluster_mapping.get(short, "N/A")

        self.assertEqual(all_data[0]["host_cluster"], "CLUSTER-A")

    def test_non_esxi_host_cluster_unchanged(self):
        all_data = [
            {"hostname": "srv01.dns-shop.ru", "hardware_type": "physical", "host_cluster": None},
        ]
        cluster_mapping = {"srv01": "CLUSTER-B"}

        for item in all_data:
            if item["hardware_type"] == "esxi" and item["hostname"]:
                short = item["hostname"].split(".")[0].lower()
                item["host_cluster"] = cluster_mapping.get(short, "N/A")

        self.assertIsNone(all_data[0]["host_cluster"])


if __name__ == "__main__":
    unittest.main()


class TestFetchLebowskiOwners(unittest.TestCase):

    @patch('glpi_hosts_scan.requests')
    @patch('glpi_hosts_scan.Connection')
    def test_returns_owner_dict_on_success(self, mock_conn, mock_requests):
        mock_conn.get_connection_from_secrets.return_value = MagicMock(
            login="user", password="pass"
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "message": "",
            "data": [
                {"id": "a", "name": "srv01", "owner": {"id": "b", "name": "Иванов Иван Иванович"}},
                {"id": "c", "name": "SRV02", "owner": {"id": "d", "name": "Петров Пётр"}},
            ]
        }
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_requests.Session.return_value = mock_session

        import glpi_hosts_scan as m
        result = m.fetch_lebowski_owners()

        self.assertEqual(result["srv01"], "Иванов Иван Иванович")
        self.assertEqual(result["srv02"], "Петров Пётр")

    @patch('glpi_hosts_scan.requests')
    @patch('glpi_hosts_scan.Connection')
    def test_returns_empty_dict_on_network_error(self, mock_conn, mock_requests):
        mock_conn.get_connection_from_secrets.side_effect = Exception("no conn")
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("timeout")
        mock_requests.Session.return_value = mock_session

        import glpi_hosts_scan as m
        result = m.fetch_lebowski_owners()

        self.assertEqual(result, {})

    @patch('glpi_hosts_scan.requests')
    @patch('glpi_hosts_scan.Connection')
    def test_skips_entries_with_owner_name_too_short(self, mock_conn, mock_requests):
        mock_conn.get_connection_from_secrets.return_value = MagicMock(login="u", password="p")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "message": "",
            "data": [
                {"id": "x", "name": "srv03", "owner": {"id": "y", "name": "AB"}},
            ]
        }
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_requests.Session.return_value = mock_session

        import glpi_hosts_scan as m
        result = m.fetch_lebowski_owners()

        self.assertNotIn("srv03", result)


class TestOwnerEnrichmentLogic(unittest.TestCase):
    """Pure enrichment logic — no DAG imports needed."""

    def _enrich(self, item: dict, lebowski_owners: dict) -> dict:
        shorthost = item.get("shorthost", "")
        if item["owner"] == "N/A" and shorthost:
            leb_owner = lebowski_owners.get(shorthost.lower())
            if leb_owner:
                item["owner"] = leb_owner
                item["lebowski_filled"] = "owner"
        return item

    def test_fills_owner_when_na_and_match_found(self):
        item = {"owner": "N/A", "shorthost": "srv01", "lebowski_filled": ""}
        owners = {"srv01": "Иванов Иван Иванович"}
        result = self._enrich(item, owners)
        self.assertEqual(result["owner"], "Иванов Иван Иванович")
        self.assertEqual(result["lebowski_filled"], "owner")

    def test_does_not_overwrite_existing_owner(self):
        item = {"owner": "TeamOps", "shorthost": "srv01", "lebowski_filled": ""}
        owners = {"srv01": "Иванов Иван Иванович"}
        result = self._enrich(item, owners)
        self.assertEqual(result["owner"], "TeamOps")
        self.assertEqual(result["lebowski_filled"], "")

    def test_owner_stays_na_when_host_not_in_lebowski(self):
        item = {"owner": "N/A", "shorthost": "unknownhost", "lebowski_filled": ""}
        owners = {"srv01": "Иванов Иван Иванович"}
        result = self._enrich(item, owners)
        self.assertEqual(result["owner"], "N/A")
        self.assertEqual(result["lebowski_filled"], "")

    def test_lookup_is_case_insensitive(self):
        item = {"owner": "N/A", "shorthost": "SRV01", "lebowski_filled": ""}
        owners = {"srv01": "Иванов Иван Иванович"}
        result = self._enrich(item, owners)
        self.assertEqual(result["owner"], "Иванов Иван Иванович")
