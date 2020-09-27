#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from ansible_collections.community.digitalocean.plugins.module_utils.digital_ocean import DigitalOceanHelper
from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible.module_utils._text import to_native
from traceback import format_exc
import json
import time
__metaclass__ = type

DOCUMENTATION = r'''
---
module: digital_ocean_kubernetes_info
short_description: Returns information about an existing DigitalOcean Kubernetes cluster
description:
  - Returns information about an existing DigitalOcean Kubernetes cluster
author: "Mark Mercado (@mamercad)"
options:
  oauth_token:
    description:
      - DigitalOcean OAuth token; can be specified in C(DO_API_KEY), C(DO_API_TOKEN), or C(DO_OAUTH_TOKEN) environment variables
    aliases: ['API_TOKEN']
    required: yes
  name:
    description:
      - A human-readable name for a Kubernetes cluster.
    type: str
    required: yes
  return_kubeconfig:
    description:
      - Controls whether or not to return the C(kubeconfig).
    type: bool
    required: no
    default: C(False)
requirements:
  - python >= 2.6
'''

EXAMPLES = r'''
- name: Get information about an existing DigitalOcean Kubernetes cluster
  community.digitalocean.digital_ocean_droplet_info:
    oauth_token: REDACTED
    name: hacktoberfest
    return_kubeconfig: yes
  register: my_cluster

- debug:
    msg: "Cluster name is {{ my_cluster.data.name}}, ID is {{ my_cluster.data.id }}"

- debug:
    msg: "Cluster kubeconfig is {{ my_cluster.data.kubeconfig }}"
'''

# Digital Ocean API info https://developers.digitalocean.com/documentation/v2/#retrieve-the-kubeconfig-for-a-kubernetes-cluster
# The only variance from the documented response is that the kubeconfig is (if return_kubeconfig is True) merged in at data['kubeconfig']
RETURN = r'''
  data:
    auto_upgrade: false
    cluster_subnet: 10.244.0.0/16
    created_at: '2020-09-26T21:36:18Z'
    endpoint: https://REDACTED.k8s.ondigitalocean.com
    id: REDACTED
    ipv4: REDACTED
    kubeconfig: |-
      apiVersion: v1
      clusters:
      - cluster:
          certificate-authority-data: REDACTED
          server: https://REDACTED.k8s.ondigitalocean.com
        name: do-nyc1-hacktoberfest
      contexts:
      - context:
          cluster: do-nyc1-hacktoberfest
          user: do-nyc1-hacktoberfest-admin
        name: do-nyc1-hacktoberfest
      current-context: do-nyc1-hacktoberfest
      kind: Config
      preferences: {}
      users:
      - name: do-nyc1-hacktoberfest-admin
        user:
          token: REDACTED
    maintenance_policy:
      day: any
      duration: 4h0m0s
      start_time: '13:00'
    name: hacktoberfest
    node_pools:
    - auto_scale: false
      count: 1
      id: REDACTED
      labels: null
      max_nodes: 0
      min_nodes: 0
      name: hacktoberfest-workers
      nodes:
      - created_at: '2020-09-26T21:36:18Z'
        droplet_id: 'REDACTED'
        id: REDACTED
        name: hacktoberfest-workers-3tv46
        status:
          state: running
        updated_at: '2020-09-26T21:40:28Z'
      size: s-1vcpu-2gb
      tags:
      - k8s
      - k8s:REDACTED
      - k8s:worker
      taints: []
    region: nyc1
    service_subnet: 10.245.0.0/16
    status:
      state: running
    surge_upgrade: false
    tags:
    - k8s
    - k8s:REDACTED
    updated_at: '2020-09-26T21:42:29Z'
    version: 1.18.8-do.0
    vpc_uuid: REDACTED
  invocation:
    module_args:
      name: hacktoberfest
data:
'''


class DOKubernetesInfo(object):
    def __init__(self, module):
        self.rest = DigitalOceanHelper(module)
        self.module = module
        # pop these values so we don't include them in the POST data
        self.module.params.pop('oauth_token')
        self.return_kubeconfig = self.module.params.pop('return_kubeconfig')
        self.cluster_id = None

    def get_by_id(self):
        response = self.rest.get('kubernetes/clusters/{0}'.format(self.cluster_id))
        json_data = response.json
        if response.status_code == 200:
            return json_data
        return None

    def get_all_clusters(self):
        response = self.rest.get('kubernetes/clusters')
        json_data = response.json
        if response.status_code == 200:
            return json_data
        return None

    def get_by_name(self, cluster_name):
        if not cluster_name:
            return None
        clusters = self.get_all_clusters()
        for cluster in clusters['kubernetes_clusters']:
            if cluster['name'] == cluster_name:
                return cluster
        return None

    def get_kubernetes_kubeconfig(self):
        response = self.rest.get('kubernetes/clusters/{0}/kubeconfig'.format(self.cluster_id))
        text_data = response.text
        return text_data

    def get_kubernetes(self):
        json_data = self.get_by_name(self.module.params['name'])
        self.cluster_id = json_data['id']
        return json_data

    def get(self):
        """Fetches an existing DigitalOcean Kubernetes cluster

        API reference: https://developers.digitalocean.com/documentation/v2/#retrieve-an-existing-kubernetes-cluster
        """
        json_data = self.get_kubernetes()
        if json_data:
            if self.return_kubeconfig:
                json_data['kubeconfig'] = self.get_kubernetes_kubeconfig()
            self.module.exit_json(changed=True, data=json_data)
        self.module.fail_json(changed=False, msg='Kubernetes cluster not found')


def core(module):
    cluster = DOKubernetesInfo(module)
    cluster.get()


# https://developers.digitalocean.com/documentation/v2/#kubernetes
def main():
    module = AnsibleModule(
        argument_spec=dict(
            oauth_token=dict(
                aliases=['API_TOKEN'],
                no_log=True,
                fallback=(env_fallback, ['DO_API_TOKEN',
                                         'DO_API_KEY', 'DO_OAUTH_TOKEN'])
            ),
            name=dict(type='str'),
            return_kubeconfig=dict(type='bool', default=False)
        ),
        required_one_of=(
            ['name']
        )
    )

    core(module)


if __name__ == '__main__':
    main()
