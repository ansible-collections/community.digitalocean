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


# EXAMPLES = r'''
# - name: Create a new droplet
#   community.digitalocean.digital_ocean_droplet:
#     state: present
#     name: mydroplet
#     oauth_token: XXX
#     size: 2gb
#     region: sfo1
#     image: ubuntu-16-04-x64
#     wait_timeout: 500
#     ssh_keys: [ .... ]
#   register: my_droplet

# - debug:
#     msg: "ID is {{ my_droplet.data.droplet.id }}, IP is {{ my_droplet.data.ip_address }}"

# - name: Ensure a droplet is present
#   community.digitalocean.digital_ocean_droplet:
#     state: present
#     id: 123
#     name: mydroplet
#     oauth_token: XXX
#     size: 2gb
#     region: sfo1
#     image: ubuntu-16-04-x64
#     wait_timeout: 500

# - name: Ensure a droplet is present with SSH keys installed
#   community.digitalocean.digital_ocean_droplet:
#     state: present
#     id: 123
#     name: mydroplet
#     oauth_token: XXX
#     size: 2gb
#     region: sfo1
#     ssh_keys: ['1534404', '1784768']
#     image: ubuntu-16-04-x64
#     wait_timeout: 500
# '''

# RETURN = r'''
# # Digital Ocean API info https://developers.digitalocean.com/documentation/v2/#droplets
# data:
#     description: a DigitalOcean Droplet
#     returned: changed
#     type: dict
#     sample: {
#         "ip_address": "104.248.118.172",
#         "ipv6_address": "2604:a880:400:d1::90a:6001",
#         "private_ipv4_address": "10.136.122.141",
#         "droplet": {
#             "id": 3164494,
#             "name": "example.com",
#             "memory": 512,
#             "vcpus": 1,
#             "disk": 20,
#             "locked": true,
#             "status": "new",
#             "kernel": {
#                 "id": 2233,
#                 "name": "Ubuntu 14.04 x64 vmlinuz-3.13.0-37-generic",
#                 "version": "3.13.0-37-generic"
#             },
#             "created_at": "2014-11-14T16:36:31Z",
#             "features": ["virtio"],
#             "backup_ids": [],
#             "snapshot_ids": [],
#             "image": {},
#             "volume_ids": [],
#             "size": {},
#             "size_slug": "512mb",
#             "networks": {},
#             "region": {},
#             "tags": ["web"]
#         }
#     }
# '''


class DOKubernetes(object):
    def __init__(self, module):
        self.rest = DigitalOceanHelper(module)
        self.module = module
        self.wait = self.module.params.pop('wait', True)
        self.wait_timeout = self.module.params.pop('wait_timeout', 120)
        # pop the oauth token so we don't include it in the POST data
        self.module.params.pop('oauth_token')
        self.cluster_id = 0

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
        json_data = response.json
        # if response.status_code == 200:
        #     return json_data
        # return None
        return json_data

    def get_kubernetes(self):
        json_data = self.get_by_name(self.module.params['name'])
        return json_data

    # https://developers.digitalocean.com/documentation/v2/#list-available-regions--node-sizes--and-versions-of-kubernetes
    def get_kubernetes_options(self):
        response = self.rest.get('kubernetes/options')
        json_data = response.json
        if response.status_code == 200:
            return json_data
        return None

    def ensure_running(self):
        end_time = time.time() + self.wait_timeout
        while time.time() < end_time:
            cluster = self.get_by_id()
            if cluster['kubernetes_cluster']['status']['state'] == 'running':
                return cluster
            time.sleep(min(2, end_time - time.time()))
        self.module.fail_json(msg='Wait for Kubernetes cluster to be running')

    def create(self):
        # Get valid Kubernetes options
        kubernetes_options = self.get_kubernetes_options()['options']
        # Validate region
        valid_regions = [ str(x['slug']) for x in kubernetes_options['regions'] ]
        if self.module.params.get('region') not in valid_regions:
            self.module.fail_json(msg='Invalid region {} (valid regions are {})'.format(self.module.params.get('region'), ', '.join(valid_regions)))
        # Validate version
        valid_versions = [ str(x['slug']) for x in kubernetes_options['versions'] ]
        if self.module.params.get('version') not in valid_versions:
            self.module.fail_json(msg='Invalid version {} (valid versions are {})'.format(self.module.params.get('version'), ', '.join(valid_versions)))
        # Validate size
        valid_sizes = [ str(x['slug']) for x in kubernetes_options['sizes'] ]
        for node_pool in self.module.params.get('node_pools'):
            if node_pool['size'] not in valid_sizes:
                self.module.fail_json(msg='Invalid size {} (valid sizes are {})'.format(node_pool['size'], ', '.join(valid_sizes)))

        # Create the Kubernetes cluster
        json_data = self.get_kubernetes()
        if json_data:
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
        json_data['kubeconfig'] = self.get_kubernetes_kubeconfig()
        self.module.exit_json(changed=True, data=json_data)

    def delete(self):
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


# https://developers.digitalocean.com/documentation/v2/#kubernetes
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
            version=dict(type='str', default='1.18.8-do.0'),
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

    core(module)


if __name__ == '__main__':
    main()
