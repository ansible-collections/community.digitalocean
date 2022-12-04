#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: kubernetes_clusters_info

short_description: Retrieve a list of all of the Kubernetes clusters in your account

version_added: 2.0.0

description:
  - Retrieve a list of all of the Kubernetes clusters kin your account.
  - View the API documentation at (https://docs.digitalocean.com/reference/api/api-reference/#operation/kubernetes_list_clusters).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get Kubernetes clusters
  community.digitalocean.kubernetes_clusters_info:
    token: "{{ token }}"
"""


RETURN = r"""
kubernetes_clusters:
  description: Kubernetes clusters.
  returned: always
  type: list
  elements: dict
  sample:
    - id: bd5f5959-5e1e-4205-a714-a914373942af
      name: prod-cluster-01
      region: nyc1
      version: 1.18.6-do.0
      cluster_subnet: 10.244.0.0/16
      service_subnet: 10.245.0.0/16
      vpc_uuid: c33931f2-a26a-4e61-b85c-4e95a2ec431b
      ipv4: 68.183.121.157
      endpoint: https://bd5f5959-5e1e-4205-a714-a914373942af.k8s.ondigitalocean.com
      tags:
        - production
        - web-team
        - k8s
        - k8s:bd5f5959-5e1e-4205-a714-a914373942af
      node_pools:
        - id: cdda885e-7663-40c8-bc74-3a036c66545d
          name: frontend-pool
          size: s-1vcpu-2gb
          count: 3
          tags:
            - production
            - web-team
            - k8s
            - k8s:bd5f5959-5e1e-4205-a714-a914373942af
            - k8s:worker
          labels: null
          taints: []
          auto_scale: false
          min_nodes: 0
          max_nodes: 0
          nodes:
            - id: 478247f8-b1bb-4f7a-8db9-2a5f8d4b8f8f
              name: adoring-newton-3niq
              status:
                state: provisioning
              droplet_id: '205545370'
              created_at: '2018-11-15T16:00:11Z'
              updated_at: '2018-11-15T16:00:11Z'
            - id: ad12e744-c2a9-473d-8aa9-be5680500eb1
              name: adoring-newton-3nim
              status:
                state: provisioning
              droplet_id: '205545371'
              created_at: '2018-11-15T16:00:11Z'
              updated_at: '2018-11-15T16:00:11Z'
            - id: e46e8d07-f58f-4ff1-9737-97246364400e
              name: adoring-newton-3ni7
              status:
                state: provisioning
              droplet_id: '205545372'
              created_at: '2018-11-15T16:00:11Z'
              updated_at: '2018-11-15T16:00:11Z'
        - id: f49f4379-7e7f-4af5-aeb6-0354bd840778
          name: backend-pool
          size: g-4vcpu-16gb
          count: 2
          tags:
            - production
            - web-team
            - k8s
            - k8s:bd5f5959-5e1e-4205-a714-a914373942af
            - k8s:worker
          labels:
            service: backend
            priority: high
          taints: []
          auto_scale: true
          min_nodes: 2
          max_nodes: 5
          nodes:
            - id: 3385619f-8ec3-42ba-bb23-8d21b8ba7518
              name: affectionate-nightingale-3nif
              status:
                state: provisioning
              droplet_id: '205545373'
              created_at: '2018-11-15T16:00:11Z'
              updated_at: '2018-11-15T16:00:11Z'
            - id: 4b8f60ff-ba06-4523-a6a4-b8148244c7e6
              name: affectionate-nightingale-3niy
              status:
                state: provisioning
              droplet_id: '205545374'
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
  description: Kubernetes clusters result information.
  returned: always
  type: str
  sample:
    - Current domains
    - No domains
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.digitalocean.plugins.module_utils.common import (
    DigitalOceanOptions,
    DigitalOceanFunctions,
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


class KubernetesClustersInformation:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        if self.state == "present":
            self.present()

    def present(self):
        kubernetes_clusters = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.kubernetes,
            meth="list_clusters",
            key="kubernetes_clusters",
            exc=HttpResponseError,
        )
        if kubernetes_clusters:
            self.module.exit_json(
                changed=False,
                msg="Current Kubernetes clusters",
                kubernetes_clusters=kubernetes_clusters,
            )
        self.module.exit_json(
            changed=False, msg="No Kubernetes clusters", kubernetes_clusters=[]
        )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
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

    KubernetesClustersInformation(module)


if __name__ == "__main__":
    main()
