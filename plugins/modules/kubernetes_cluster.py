#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: kubernetes_cluster

short_description: Create or delete Kubernetes clusters

version_added: 2.0.0

description:
  - Create or delete Kubernetes clusters.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Kubernetes).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - A human-readable name for a Kubernetes cluster.
    type: str
    required: true
  region:
    description:
      - The slug identifier for the region where the Kubernetes cluster is located.
    type: str
    required: true
  version:
    description:
      - The slug identifier for the version of Kubernetes used for the cluster.
      - |
        If set to a minor version (e.g. "1.14"), the latest version within it will be used
        (e.g. "1.14.6-do.1").
      - If set to "latest", the latest published version will be used.
      - See the C(/v2/kubernetes/options endpoint) to find all currently available versions.
    type: str
    required: false
  vpc_uuid:
    description:
      - A string specifying the UUID of the VPC to which the Kubernetes cluster is assigned.
    type: str
    required: false
  tags:
    description:
      - An array of tags applied to the Kubernetes cluster.
      - All clusters are automatically tagged C(k8s) and C(k8s:$K8S_CLUSTER_ID).
    type: list
    elements: str
    required: false
  node_pools:
    description:
      - An object specifying the details of the worker nodes available to the Kubernetes cluster.
    type: list
    elements: dict
    required: false
  maintenance_policy:
    description:
      - An object specifying the maintenance window policy for the Kubernetes cluster.
    type: dict
    required: false
  auto_upgrade:
    description:
      - |
        A boolean value indicating whether the cluster will be automatically upgraded to new patch
        releases during its maintenance window.
    type: bool
    required: false
    default: false
  surge_upgrade:
    description:
      - A boolean value indicating whether surge upgrade is enabled/disabled for the cluster.
      - |
        Surge upgrade makes cluster upgrades fast and reliable by bringing up new nodes before
        destroying the outdated nodes.
    type: bool
    required: false
    default: false
  ha:
    description:
      - |
        A boolean value indicating whether the control plane is run in a highly available
        configuration in the cluster.
      - Highly available control planes incur less downtime. The property cannot be disabled.
    type: bool
    required: false
    default: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create Kubernetes cluster
  community.digitalocean.kubernetes_cluster:
    token: "{{ token }}"
    state: present
    name: prod-cluster-01
    region: nyc1
    version: "1.18.6-do.0"
    node_pools:
      - size: s-1vcpu-2gb
        name: worker-pool
        count: 3
"""


RETURN = r"""
kubernetes_cluster:
  description: Kubernetes cluster information.
  returned: always
  type: dict
  sample:
    id: bd5f5959-5e1e-4205-a714-a914373942af
    name: prod-cluster-01
    region: nyc1
    version: 1.18.6-do.0
    cluster_subnet: 10.244.0.0/16
    service_subnet: 10.245.0.0/16
    vpc_uuid: c33931f2-a26a-4e61-b85c-4e95a2ec431b
    ipv4: ''
    endpoint: ''
    tags:
      - k8s
      - k8s:bd5f5959-5e1e-4205-a714-a914373942af
    node_pools:
      - id: cdda885e-7663-40c8-bc74-3a036c66545d
        name: worker-pool
        size: s-1vcpu-2gb
        count: 3
        tags:
          - k8s
          - 'k8s:bd5f5959-5e1e-4205-a714-a914373942af'
          - 'k8s:worker'
        labels: null
        taints: []
        auto_scale: false
        min_nodes: 0
        max_nodes: 0
        nodes:
          - id: 478247f8-b1bb-4f7a-8db9-2a5f8d4b8f8f
            name: ''
            status:
              state: provisioning
            droplet_id: ''
            created_at: '2018-11-15T16:00:11Z'
            updated_at: '2018-11-15T16:00:11Z'
          - id: ad12e744-c2a9-473d-8aa9-be5680500eb1
            name: ''
            status:
              state: provisioning
            droplet_id: ''
            created_at: '2018-11-15T16:00:11Z'
            updated_at: '2018-11-15T16:00:11Z'
          - id: e46e8d07-f58f-4ff1-9737-97246364400e
            name: ''
            status:
              state: provisioning
            droplet_id: ''
            created_at: '2018-11-15T16:00:11Z'
            updated_at: '2018-11-15T16:00:11Z'
    maintenance_policy:
      start_time: '00:00'
      duration: 4h0m0s
      day: any
    auto_upgrade: false
    status:
      state: provisioning
      message: provisioning
    created_at: '2018-11-15T16:00:11Z'
    updated_at: '2018-11-15T16:00:11Z'
    surge_upgrade: false
    registry_enabled: false
    ha: false
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Kubernetes cluster result information.
  returned: always
  type: str
  sample:
    - Created redis database cluster backend (9cc10173-e9ea-4176-9dbc-a4cee4c4ff30) in nyc3
    - Deleted redis database cluster backend (9cc10173-e9ea-4176-9dbc-a4cee4c4ff30) in nyc3
    - redis database cluster backend in nyc3 would be created
    - redis database cluster backend (9cc10173-e9ea-4176-9dbc-a4cee4c4ff30) in nyc3 exists
    - redis database cluster backend in nyc3 does not exist
    - redis database cluster backend (9cc10173-e9ea-4176-9dbc-a4cee4c4ff30) would be deleted
"""

import time
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.digitalocean.plugins.module_utils.common import (
    DigitalOceanConstants,
    DigitalOceanOptions,
)

import traceback

HAS_AZURE_LIBRARY = False
AZURE_LIBRARY_IMPORT_ERROR = None
try:
    from azure.core.exceptions import HttpResponseError
except ImportError:
    AZURE_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_AZURE_LIBRARY = True

HAS_PYDO_LIBRARY = False
PYDO_LIBRARY_IMPORT_ERROR = None
try:
    from pydo import Client
except ImportError:
    PYDO_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_PYDO_LIBRARY = True


class KubernetesCluster:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.timeout = module.params.get("timeout")
        self.name = module.params.get("name")
        self.region = module.params.get("region")
        self.version = module.params.get("version")
        self.vpc_uuid = module.params.get("vpc_uuid")
        self.tags = module.params.get("tags")
        self.node_pools = module.params.get("node_pools")
        self.maintenance_policy = module.params.get("maintenance_policy")
        self.auto_upgrade = module.params.get("auto_upgrade")
        self.surge_upgrade = module.params.get("surge_upgrade")
        self.ha = module.params.get("ha")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_kubernetes_clusters_by_name_and_region(self):
        try:
            kubernetes_clusters = self.client.kubernetes.list_clusters()[
                "kubernetes_clusters"
            ]
            found_kubernetes_clusters = []
            for kubernetes_cluster in kubernetes_clusters:
                if self.name == kubernetes_cluster["name"]:
                    if self.region == kubernetes_cluster["region"]:
                        found_kubernetes_clusters.append(kubernetes_cluster)
            return found_kubernetes_clusters
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                kubernetes_cluster=[],
            )

    def get_kubernetes_cluster_by_id(self, id):
        try:
            kubernetes_cluster = self.client.kubernetes.get_cluster(cluster_id=id)[
                "kubernetes_cluster"
            ]
            return kubernetes_cluster
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                kubernetes_cluster=[],
            )

    def create_kubernetes_cluster(self):
        try:
            body = {
                "name": self.name,
                "region": self.region,
                "version": self.version,
                "vpc_uuid": self.vpc_uuid,
                "tags": self.tags,
                "node_pools": self.node_pools,
                "maintenance_policy": self.maintenance_policy,
                "auto_upgrade": self.auto_upgrade,
                "surge_upgrade": self.surge_upgrade,
                "ha": self.ha,
            }
            kubernetes_cluster = self.client.kubernetes.create_cluster(body=body)[
                "kubernetes_cluster"
            ]

            status = kubernetes_cluster["status"]
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time and status != "online":
                time.sleep(DigitalOceanConstants.SLEEP)
                status = self.get_kubernetes_cluster_by_id(kubernetes_cluster["id"])[
                    "status"
                ]

            self.module.exit_json(
                changed=True,
                msg=f"Created Kubernetes cluster {self.name} ({kubernetes_cluster['id']}) in {self.region}",
                kubernetes_cluster=kubernetes_cluster,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                kubernetes_cluster=[],
            )

    def delete_kubernetes_cluster(self, kubernetes_cluster):
        try:
            self.client.kubernetes.delete_cluster(cluster_id=kubernetes_cluster["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted Kubernetes cluster {self.name} ({kubernetes_cluster['id']}) in {self.region}",
                kubernetes_cluster=kubernetes_cluster,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                kubernetes_cluster=[],
            )

    def present(self):
        kubernetes_clusters = self.get_kubernetes_clusters_by_name_and_region()
        if len(kubernetes_clusters) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Kubernetes cluster {self.name} in {self.region} would be created",
                    kubernetes_cluster=[],
                )
            else:
                self.create_kubernetes_cluster()
        elif len(kubernetes_clusters) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Kubernetes cluster {self.name} ({kubernetes_clusters[0]['id']}) in {self.region} exists",
                kubernetes_cluster=kubernetes_clusters[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(kubernetes_clusters)} Kubernetes clusters named {self.name} in {self.region}",
                kubernetes_cluster=[],
            )

    def absent(self):
        kubernetes_clusters = self.get_kubernetes_clusters_by_name_and_region()
        if len(kubernetes_clusters) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"Kubernetes cluster {self.name} in {self.region} does not exist",
                kubernetes_cluster=[],
            )
        elif len(kubernetes_clusters) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Kubernetes cluster {self.name} ({kubernetes_clusters[0]['id']}) in {self.region} would be deleted",
                    kubernetes_cluster=kubernetes_clusters[0],
                )
            else:
                self.delete_kubernetes_cluster(
                    kubernetes_cluster=kubernetes_clusters[0]
                )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(kubernetes_clusters)} Kubernetes clusters named {self.name} in {self.region}",
                kubernetes_cluster=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        region=dict(type="str", required=True),
        version=dict(type="str", required=False),
        vpc_uuid=dict(type="str", required=False),
        tags=dict(type="list", elements="str", required=False),
        node_pools=dict(type="list", elements="dict", required=False),
        maintenance_policy=dict(type="dict", required=False),
        auto_upgrade=dict(type="bool", required=False, default=False),
        surge_upgrade=dict(type="bool", required=False, default=False),
        ha=dict(type="bool", required=False, default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "present", ("version", "node_pools"))],
    )

    if not HAS_AZURE_LIBRARY:
        module.fail_json(
            msg=missing_required_lib("azure.core.exceptions"),
            exception=AZURE_LIBRARY_IMPORT_ERROR,
        )

    if not HAS_PYDO_LIBRARY:
        module.fail_json(
            msg=missing_required_lib("pydo"),
            exception=PYDO_LIBRARY_IMPORT_ERROR,
        )

    KubernetesCluster(module)


if __name__ == "__main__":
    main()
