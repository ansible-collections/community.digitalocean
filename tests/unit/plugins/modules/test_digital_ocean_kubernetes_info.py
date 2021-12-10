from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import MagicMock
from ansible_collections.community.digitalocean.plugins.modules.digital_ocean_kubernetes_info import (
    DOKubernetesInfo,
)


class TestDOKubernetesInfo(unittest.TestCase):
    def test_get_by_id_when_ok(self):
        module = MagicMock()
        k = DOKubernetesInfo(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.status_code = 200
        k.rest.get.return_value.json = {"foo": "bar"}
        self.assertEqual(k.get_by_id(), {"foo": "bar"})

    def test_get_by_id_when_not_ok(self):
        module = MagicMock()
        k = DOKubernetesInfo(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.status_code = 400
        k.rest.get.return_value.json = {"foo": "bar"}
        self.assertIsNone(k.get_by_id())

    def test_get_all_clusters_when_ok(self):
        module = MagicMock()
        k = DOKubernetesInfo(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.status_code = 200
        k.rest.get.return_value.json = {"foo": "bar"}
        self.assertEqual(k.get_all_clusters(), {"foo": "bar"})

    def test_get_all_clusters_when_not_ok(self):
        module = MagicMock()
        k = DOKubernetesInfo(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.status_code = 400
        k.rest.get.return_value.json = {"foo": "bar"}
        self.assertIsNone(k.get_all_clusters())

    def test_get_by_name_none(self):
        module = MagicMock()
        k = DOKubernetesInfo(module)
        self.assertIsNone(k.get_by_name(None))

    def test_get_by_name_found(self):
        module = MagicMock()
        k = DOKubernetesInfo(module)
        k.get_all_clusters = MagicMock()
        k.get_all_clusters.return_value = {"kubernetes_clusters": [{"name": "foo"}]}
        self.assertEqual(k.get_by_name("foo"), {"name": "foo"})

    def test_get_by_name_not_found(self):
        module = MagicMock()
        k = DOKubernetesInfo(module)
        k.get_all_clusters = MagicMock()
        k.get_all_clusters.return_value = {"kubernetes_clusters": [{"name": "foo"}]}
        self.assertIsNone(k.get_by_name("foo2"))

    def test_get_kubernetes_kubeconfig_when_ok(self):
        module = MagicMock()
        k = DOKubernetesInfo(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.status_code = 200
        k.rest.get.return_value.body = "kubeconfig"
        self.assertEqual(k.get_kubernetes_kubeconfig(), "kubeconfig")

    def test_get_kubernetes_kubeconfig_when_not_ok(self):
        module = MagicMock()
        k = DOKubernetesInfo(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.status_code = 400
        k.rest.get.return_value.body = "kubeconfig"
        self.assertNotEqual(k.get_kubernetes_kubeconfig(), "kubeconfig")

    def test_get_kubernetes_when_found(self):
        module = MagicMock()
        k = DOKubernetesInfo(module)
        k.get_by_name = MagicMock()
        k.get_by_name.return_value = {"id": 42}
        self.assertEqual(k.get_kubernetes(), {"id": 42})

    def test_get_kubernetes_when_not_found(self):
        module = MagicMock()
        k = DOKubernetesInfo(module)
        k.get_by_name = MagicMock()
        k.get_by_name.return_value = None
        self.assertIsNone(k.get_kubernetes())

    def test_get_when_found(self):
        module = MagicMock()
        module.exit_json = MagicMock()
        k = DOKubernetesInfo(module)
        k.get_kubernetes = MagicMock()
        k.get_kubernetes_kubeconfig = MagicMock()
        k.get()
        module.exit_json.assert_called()

    def test_get_when_not_found(self):
        module = MagicMock()
        module.fail_json = MagicMock()
        k = DOKubernetesInfo(module)
        k.get_kubernetes = MagicMock()
        k.get_kubernetes.return_value = None
        k.get()
        module.fail_json.assert_called()
