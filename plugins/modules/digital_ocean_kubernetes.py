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
import traceback
__metaclass__ = type

DOCUMENTATION = r'''
---
module: digital_ocean_kubernetes
short_description: Create and delete a DigitalOcean Kubernetes cluster
description:
    - Create and delete a Kubernetes cluster in DigitalOcean (and optionally wait for it to be running)
author: "Mark Mercado (@mamercad)"
options:
  oauth_token:
    description:
      - DigitalOcean OAuth token; can be specified in C(DO_API_KEY), C(DO_API_TOKEN), or C(DO_OAUTH_TOKEN) environment variables
    aliases: ['API_TOKEN']
    required: yes
  state:
    description:
      - The usual, C(present) to create, C(absent) to destroy
    choices: ['present', 'absent']
    default: C(present)
    required: yes
  name:
    description:
      - A human-readable name for a Kubernetes cluster.
    type: str
    required: yes
  region:
    description:
      - The slug identifier for the region where the Kubernetes cluster will be created.
    type: str
    required: yes
    default: nyc1
  version:
    description:
      - The slug identifier for the version of Kubernetes used for the cluster. See the /v2/kubernetes/options endpoint for available versions.
    type: str
    required: no
    default: 1.18.8-do.0
  auto_upgrade:
    description:
      - A boolean value indicating whether the cluster will be automatically upgraded to new patch releases during its maintenance window.
    type: bool
    required: no
    default: C(False)
  surge_upgrade:
    description:
      - A boolean value indicating whether surge upgrade is enabled/disabled for the cluster. Surge upgrade makes cluster upgrades fast and reliable by bringing up new nodes before destroying the outdated nodes.
    type: bool
    required: no
    default: C(False)
  tags:
    description:
      - A flat array of tag names as strings to be applied to the Kubernetes cluster. All clusters will be automatically tagged "k8s" and "k8s:$K8S_CLUSTER_ID" in addition to any tags provided by the user.
    type: list(str)
    required: no
  maintenance_policy:
    description:
      - An object specifying the maintenance window policy for the Kubernetes cluster (see table below).
    type: dict
    required: no
  node_pools:
    description:
      - An object specifying the details of the worker nodes available to the Kubernetes cluster (see table below).
    type: dict
    required: no
  vpc_uuid:
    description:
      - A string specifying the UUID of the VPC to which the Kubernetes cluster will be assigned. If excluded, the cluster will be assigned to your account's default VPC for the region.
    type: str
    required: no
  return_kubeconfig:
    description:
      - Controls whether or not to return the C(kubeconfig).
    type: bool
    required: no
    default: C(False)
  wait:
    description:
     - Wait for the cluster to be running before returning.
    type: bool
    required: no
    default: C(True)
  wait_timeout:
    description:
      - How long before wait gives up, in seconds, when creating a cluster.
    type: int
    default: 600
requirements:
    - python >= 2.6
'''


EXAMPLES = r'''
- name: Create a new DigitalOcean Kubernetes cluster in New York 1
  community.digitalocean.digital_ocean_kubernetes:
    state: present
    oauth_token: "{{ lookup('env', 'DO_API_TOKEN') }}"
    name: hacktoberfest
    region: nyc1
    node_pools:
        - name: hacktoberfest-workers
        size: s-1vcpu-2gb
        count: 3
    return_kubeconfig: yes
    wait_timeout: 600
    register: my_cluster

- name: Show the kubeconfig for the cluster we just created
  debug:
    msg: "{{ my_cluster.data.kubeconfig }}"

- name: Destroy (delete) an existing DigitalOcean Kubernetes cluster
  community.digitalocean.digital_ocean_kubernetes:
    state: absent
    oauth_token: "{{ lookup('env', 'DO_API_TOKEN') }}"
    name: hacktoberfest
'''

# Digital Ocean API info https://developers.digitalocean.com/documentation/v2/#kubernetes
# The only variance from the documented response is that the kubeconfig is (if return_kubeconfig is True) merged in at data['kubeconfig']
RETURN = r'''
  data:
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
    kubernetes_cluster:
      auto_upgrade: false
      cluster_subnet: 10.244.0.0/16
      created_at: '2020-09-27T00:55:37Z'
      endpoint: https://REDACTED.k8s.ondigitalocean.com
      id: REDACTED
      ipv4: REDACTED
      maintenance_policy:
        day: any
        duration: 4h0m0s
        start_time: '15:00'
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
        - created_at: '2020-09-27T00:55:37Z'
          droplet_id: '209555245'
          id: REDACTED
          name: hacktoberfest-workers-3tdq1
          status:
            state: running
          updated_at: '2020-09-27T00:58:36Z'
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
      updated_at: '2020-09-27T01:00:37Z'
      version: 1.18.8-do.0
      vpc_uuid: REDACTED
  invocation:
    module_args:
      auto_upgrade: false
      maintenance_policy: null
      name: hacktoberfest
      node_pools:
      - count: 1
        name: hacktoberfest-workers
        size: s-1vcpu-2gb
      region: nyc1
      return_kubeconfig: true
      surge_upgrade: false
      tags: null
      version: 1.18.8-do.0
      vpc_uuid: null
'''


class DOKubernetes(object):
    def __init__(self, module):
        self.rest = DigitalOceanHelper(module)
        self.module = module
        # Pop these values so we don't include them in the POST data
        self.return_kubeconfig = self.module.params.pop(
            'return_kubeconfig', False)
        self.wait = self.module.params.pop('wait', True)
        self.wait_timeout = self.module.params.pop('wait_timeout', 600)
        self.module.params.pop('oauth_token')
        self.cluster_id = None

    def get_by_id(self):
        """Returns an existing DigitalOcean Kubernetes cluster matching on id"""
        response = self.rest.get(
            'kubernetes/clusters/{0}'.format(self.cluster_id))
        json_data = response.json
        if response.status_code == 200:
            return json_data
        return None

    def get_all_clusters(self):
        """Returns all DigitalOcean Kubernetes clusters"""
        response = self.rest.get('kubernetes/clusters')
        json_data = response.json
        if response.status_code == 200:
            return json_data
        return None

    def get_by_name(self, cluster_name):
        """Returns an existing DigitalOcean Kubernetes cluster matching on name"""
        if not cluster_name:
            return None
        clusters = self.get_all_clusters()
        for cluster in clusters['kubernetes_clusters']:
            if cluster['name'] == cluster_name:
                return cluster
        return None

    def get_kubernetes_kubeconfig(self):
        """Returns the kubeconfig for an existing DigitalOcean Kubernetes cluster"""
        response = self.rest.get(
            'kubernetes/clusters/{0}/kubeconfig'.format(self.cluster_id))
        text_data = response.text
        return text_data

    def get_kubernetes(self):
        """Returns an existing DigitalOcean Kubernetes cluster by name"""
        json_data = self.get_by_name(self.module.params['name'])
        if json_data:
            self.cluster_id = json_data['id']
            return json_data
        else:
            return None

    def get_kubernetes_options(self):
        """Fetches DigitalOcean Kubernetes options: regions, sizes, versions.
        API reference: https://developers.digitalocean.com/documentation/v2/#list-available-regions--node-sizes--and-versions-of-kubernetes
        """
        response = self.rest.get('kubernetes/options')
        json_data = response.json
        if response.status_code == 200:
            return json_data
        return None

    def ensure_running(self):
        """Waits for the newly created DigitalOcean Kubernetes cluster to be running"""
        end_time = time.time() + self.wait_timeout
        while time.time() < end_time:
            cluster = self.get_by_id()
            if cluster['kubernetes_cluster']['status']['state'] == 'running':
                return cluster
            time.sleep(min(2, end_time - time.time()))
        self.module.fail_json(msg='Wait for Kubernetes cluster to be running')

    def create(self):
        """Creates a DigitalOcean Kubernetes cluster
        API reference: https://developers.digitalocean.com/documentation/v2/#create-a-new-kubernetes-cluster
        """
        # Get valid Kubernetes options (regions, sizes, versions)
        kubernetes_options = self.get_kubernetes_options()['options']
        # Validate region
        valid_regions = [str(x['slug']) for x in kubernetes_options['regions']]
        if self.module.params.get('region') not in valid_regions:
            self.module.fail_json(msg='Invalid region {} (valid regions are {})'.format(
                self.module.params.get('region'), ', '.join(valid_regions)))
        # Validate version
        valid_versions = [str(x['slug'])
                          for x in kubernetes_options['versions']]
        if self.module.params.get('version') not in valid_versions:
            self.module.fail_json(msg='Invalid version {} (valid versions are {})'.format(
                self.module.params.get('version'), ', '.join(valid_versions)))
        # Validate size
        valid_sizes = [str(x['slug']) for x in kubernetes_options['sizes']]
        for node_pool in self.module.params.get('node_pools'):
            if node_pool['size'] not in valid_sizes:
                self.module.fail_json(msg='Invalid size {} (valid sizes are {})'.format(
                    node_pool['size'], ', '.join(valid_sizes)))

        # Create the Kubernetes cluster
        json_data = self.get_kubernetes()
        if json_data:
            # Add the kubeconfig to the return
            if self.return_kubeconfig:
                json_data['kubeconfig'] = self.get_kubernetes_kubeconfig()
            self.module.exit_json(changed=False, data=json_data)
        if self.module.check_mode:
            self.module.exit_json(changed=True)
        request_params = dict(self.module.params)
        response = self.rest.post('kubernetes/clusters', data=request_params)
        json_data = response.json
        if response.status_code >= 400:
            self.module.fail_json(changed=False, msg=json_data)
        # Set the cluster_id
        self.cluster_id = json_data['kubernetes_cluster']['id']
        if self.wait:
            json_data = self.ensure_running()
        # Add the kubeconfig to the return
        if self.return_kubeconfig:
            json_data['kubeconfig'] = self.get_kubernetes_kubeconfig()
        self.module.exit_json(changed=True, data=json_data)

    def delete(self):
        """Deletes a DigitalOcean Kubernetes cluster
        API reference: https://developers.digitalocean.com/documentation/v2/#delete-a-kubernetes-cluster
        """
        json_data = self.get_kubernetes()
        if json_data:
            if self.module.check_mode:
                self.module.exit_json(changed=True)
            response = self.rest.delete(
                'kubernetes/clusters/{0}'.format(json_data['id']))
            json_data = response.json
            if response.status_code == 204:
                self.module.exit_json(
                    changed=True, msg='Kubernetes cluster deleted')
            self.module.fail_json(
                changed=False, msg='Failed to delete Kubernetes cluster')
        else:
            self.module.exit_json(
                changed=False, msg='Kubernetes cluster not found')


def core(module):
    state = module.params.pop('state')
    cluster = DOKubernetes(module)
    if state == 'present':
        cluster.create()
    elif state == 'absent':
        cluster.delete()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=['present', 'absent'], default='present'),
            oauth_token=dict(
                aliases=['API_TOKEN'],
                no_log=True,
                fallback=(env_fallback, ['DO_API_TOKEN',
                                         'DO_API_KEY', 'DO_OAUTH_TOKEN'])
            ),
            name=dict(type='str'),
            region=dict(aliases=['region_id'], default='nyc1'),
            version=dict(type='str', default='1.18.8-do.1'),
            auto_upgrade=dict(type='bool', default=False),
            surge_upgrade=dict(type='bool', default=False),
            tags=dict(type='list'),
            maintenance_policy=dict(
                start_time='',
                day=''
            ),
            node_pools=dict(type='list', default=[
                {
                    'name': 'worker-pool',
                    'size': 's-1vcpu-2gb',
                    'count': 1,
                    'tags': [],
                    'labels': {}
                }
            ]),
            vpc_uuid=dict(type='str'),
            return_kubeconfig=dict(type='bool', default=False),
            wait=dict(type='bool', default=True),
            wait_timeout=dict(type='int', default=600)
        ),
        required_one_of=(
            ['name']
        ),
        required_if=([
            ('state', 'present', ['name', 'region', 'version', 'node_pools']),
        ]),
        supports_check_mode=True,
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())

if __name__ == '__main__':
    main()
