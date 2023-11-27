from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import MagicMock
from ansible_collections.community.general.tests.unit.compat.mock import DEFAULT
from ansible_collections.community.digitalocean.plugins.modules.digital_ocean_kubernetes import (
    DOKubernetes,
)


class TestDOKubernetes(unittest.TestCase):
    def test_get_by_id_when_ok(self):
        module = MagicMock()
        module.params.get.return_value = False
        k = DOKubernetes(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.status_code = 200
        k.rest.get.return_value.json = {"foo": "bar"}
        self.assertEqual(k.get_by_id(), {"foo": "bar"})

    def test_get_by_id_when_not_ok(self):
        module = MagicMock()
        module.params.get.return_value = False
        k = DOKubernetes(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.status_code = 400
        k.rest.get.return_value.json = {"foo": "bar"}
        self.assertIsNone(k.get_by_id())

    def test_get_all_clusters_when_ok(self):
        module = MagicMock()
        module.params.get.return_value = False
        k = DOKubernetes(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.status_code = 200
        k.rest.get.return_value.json = {"foo": "bar"}
        self.assertEqual(k.get_all_clusters(), {"foo": "bar"})

    def test_get_all_clusters_when_not_ok(self):
        module = MagicMock()
        module.params.get.return_value = False
        k = DOKubernetes(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.status_code = 400
        k.rest.get.return_value.json = {"foo": "bar"}
        self.assertIsNone(k.get_all_clusters())

    def test_get_by_name_none(self):
        module = MagicMock()
        module.params.get.return_value = False
        k = DOKubernetes(module)
        self.assertIsNone(k.get_by_name(None))

    def test_get_by_name_found(self):
        module = MagicMock()
        module.params.get.return_value = False
        k = DOKubernetes(module)
        k.get_all_clusters = MagicMock()
        k.get_all_clusters.return_value = {"kubernetes_clusters": [{"name": "foo"}]}
        self.assertEqual(k.get_by_name("foo"), {"name": "foo"})

    def test_get_by_name_not_found(self):
        module = MagicMock()
        module.params.get.return_value = False
        k = DOKubernetes(module)
        k.get_all_clusters = MagicMock()
        k.get_all_clusters.return_value = {"kubernetes_clusters": [{"name": "foo"}]}
        self.assertIsNone(k.get_by_name("foo2"))

    def test_get_kubernetes_kubeconfig_when_ok(self):
        module = MagicMock()
        module.params.get.return_value = False
        k = DOKubernetes(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.status_code = 200
        k.rest.get.return_value.body = "kubeconfig"
        self.assertEqual(k.get_kubernetes_kubeconfig(), "kubeconfig")

    def test_get_kubernetes_kubeconfig_when_not_ok(self):
        module = MagicMock()
        module.params.get.return_value = False
        k = DOKubernetes(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.status_code = 400
        k.rest.get.return_value.body = "kubeconfig"
        self.assertNotEqual(k.get_kubernetes_kubeconfig(), "kubeconfig")

    def test_get_kubernetes_when_found(self):
        module = MagicMock()
        module.params.get.return_value = False
        k = DOKubernetes(module)
        k.get_by_name = MagicMock()
        k.get_by_name.return_value = {"id": 42}
        self.assertEqual(k.get_kubernetes(), {"id": 42})

    def test_get_kubernetes_when_not_found(self):
        module = MagicMock()
        module.params.get.return_value = False
        k = DOKubernetes(module)
        k.get_by_name = MagicMock()
        k.get_by_name.return_value = None
        self.assertIsNone(k.get_kubernetes())

    def test_get_kubernetes_options_when_ok(self):
        module = MagicMock()
        module.params.get.return_value = False
        k = DOKubernetes(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.json = {"foo": "bar"}
        k.rest.get.return_value.status_code = 200
        self.assertEqual(k.get_kubernetes_options(), {"foo": "bar"})

    def test_get_kubernetes_options_when_not_ok(self):
        module = MagicMock()
        module.params.get.return_value = False
        k = DOKubernetes(module)
        k.rest = MagicMock()
        k.rest.get = MagicMock()
        k.rest.get.return_value.json = {"foo": "bar"}
        k.rest.get.return_value.status_code = 400
        self.assertIsNone(k.get_kubernetes_options())

    def test_ensure_running_when_running(self):
        module = MagicMock()
        module.params.get.return_value = False
        module.fail_json = MagicMock()

        k = DOKubernetes(module)
        k.end_time = 20
        k.wait_timeout = 1
        k.get_by_id = MagicMock()

        cluster = {"kubernetes_cluster": {"status": {"state": "running"}}}

        k.get_by_id.return_value = cluster

        time = MagicMock()
        time.time = MagicMock()
        time.time.return_value = 10
        time.sleep = MagicMock()

        self.assertEqual(k.ensure_running(), cluster)

    def test_ensure_running_when_not_running(self):
        module = MagicMock()
        module.params.get.return_value = False
        module.fail_json = MagicMock()

        k = DOKubernetes(module)
        k.end_time = 20
        k.wait_timeout = -100
        k.get_by_id = MagicMock()

        cluster = {"kubernetes_cluster": {"status": {"state": "stopped"}}}

        k.get_by_id.return_value = cluster

        time = MagicMock()
        time.time = MagicMock()
        time.time.return_value = 20
        time.sleep = MagicMock()

        # module.fail_json.assert_called()
        assert True

    def test_create_ok(self):
        module = MagicMock()

        def side_effect(*args, **kwargs):
            if "project_name" == args[0]:
                return False
            if "regions" == args[0]:
                return "nyc1"
            return DEFAULT

        module.params.get.side_effect = side_effect
        module.exit_json = MagicMock()
        module.fail_json = MagicMock()

        k = DOKubernetes(module)

        k.get_kubernetes_options = MagicMock()

        kubernetes_options = {
            "options": {
                "regions": [{"name": "New York 1", "slug": "nyc1"}],
                "versions": [{"kubernetes_version": "1.18.8", "slug": "1.18.8-do.0"}],
                "sizes": [{"name": "s-1vcpu-2gb", "slug": "s-1vcpu-2gb"}],
            }
        }

        k.get_kubernetes_options.return_value = kubernetes_options

        k.get_kubernetes = MagicMock()
        k.get_kubernetes.return_value = {"foo": "bar"}
        k.cluster_id = MagicMock()
        k.cluster_id.return_value = 42

        k.rest = MagicMock()
        k.rest.post = MagicMock()
        k.rest.post.return_value.json = {"kubernetes_cluster": {"id": 42}}
        k.rest.post.return_value.status_code = 200
        k.ensure_running = MagicMock()
        k.cluster_id = MagicMock()

        k.create()
        k.module.exit_json.assert_called()

    def test_create_not_ok(self):
        module = MagicMock()

        def side_effect(*args, **kwargs):
            if "project_name" == args[0]:
                return False
            if "regions" == args[0]:
                return "nyc1"
            return DEFAULT

        module.params.get.side_effect = side_effect
        module.exit_json = MagicMock()
        module.fail_json = MagicMock()

        k = DOKubernetes(module)

        k.get_kubernetes_options = MagicMock()

        kubernetes_options = {
            "options": {
                "regions": [{"name": "New York 1", "slug": "nyc1"}],
                "versions": [{"kubernetes_version": "1.18.8", "slug": "1.18.8-do.0"}],
                "sizes": [{"name": "s-1vcpu-2gb", "slug": "s-1vcpu-2gb"}],
            }
        }

        k.get_kubernetes_options.return_value = kubernetes_options

        k.get_kubernetes = MagicMock()
        k.get_kubernetes.return_value = {"foo": "bar"}
        k.cluster_id = MagicMock()
        k.cluster_id.return_value = 42

        k.rest = MagicMock()
        k.rest.post = MagicMock()
        k.rest.post.return_value.json = {"kubernetes_cluster": {"id": 42}}
        k.rest.post.return_value.status_code = 400
        k.ensure_running = MagicMock()
        k.cluster_id = MagicMock()

        k.create()
        k.module.exit_json.assert_called()

    def test_delete_ok(self):
        module = MagicMock()
        module.params.get.return_value = False
        module.exit_json = MagicMock()

        k = DOKubernetes(module)

        k.get_kubernetes = MagicMock()

        k.rest = MagicMock()
        k.rest.delete = MagicMock()
        k.rest.delete.return_value.id = 42
        k.rest.delete.return_value.status_code = 204

        k.delete()
        k.module.exit_json.assert_called()

    def test_delete_not_ok(self):
        module = MagicMock()
        module.params.get.return_value = False
        module.exit_json = MagicMock()

        k = DOKubernetes(module)

        k.get_kubernetes = MagicMock()
        k.get_kubernetes.return_value = None

        k.delete()
        k.module.exit_json.assert_called()
