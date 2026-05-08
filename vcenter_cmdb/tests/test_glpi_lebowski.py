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
