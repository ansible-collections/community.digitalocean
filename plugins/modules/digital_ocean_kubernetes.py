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
    - Create and delete a Kubernetes cluster in DigitalOcean and optionally wait for it to be running.
author: "Gurchet Rai (@gurch101)"
# options:
#   state:
#     description:
#      - Indicate desired state of the target.
#     default: present
#     choices: ['present', 'absent']
#   id:
#     description:
#      - Numeric, the droplet id you want to operate on.
#     aliases: ['droplet_id']
#   name:
#     description:
#      - String, this is the name of the droplet - must be formatted by hostname rules.
#   unique_name:
#     description:
#      - require unique hostnames.  By default, DigitalOcean allows multiple hosts with the same name.  Setting this to "yes" allows only one host
#        per name.  Useful for idempotence.
#     default: False
#     type: bool
#   size:
#     description:
#      - This is the slug of the size you would like the droplet created with.
#     aliases: ['size_id']
#   image:
#     description:
#      - This is the slug of the image you would like the droplet created with.
#     aliases: ['image_id']
#   region:
#     description:
#      - This is the slug of the region you would like your server to be created in.
#     aliases: ['region_id']
#   ssh_keys:
#     description:
#      - array of SSH key Fingerprint that you would like to be added to the server.
#     required: False
#   private_networking:
#     description:
#      - add an additional, private network interface to droplet for inter-droplet communication.
#     default: False
#     type: bool
#   vpc_uuid:
#     description:
#      - A string specifying the UUID of the VPC to which the Droplet will be assigned. If excluded, Droplet will be
#        assigned to the account's default VPC for the region.
#     type: str
#     version_added: 0.1.0
#   user_data:
#     description:
#       - opaque blob of data which is made available to the droplet
#     required: False
#   ipv6:
#     description:
#       - enable IPv6 for your droplet.
#     required: False
#     default: False
#     type: bool
#   wait:
#     description:
#      - Wait for the droplet to be active before returning.  If wait is "no" an ip_address may not be returned.
#     required: False
#     default: True
#     type: bool
#   wait_timeout:
#     description:
#      - How long before wait gives up, in seconds, when creating a droplet.
#     default: 120
#   backups:
#     description:
#      - indicates whether automated backups should be enabled.
#     required: False
#     default: False
#     type: bool
#   monitoring:
#     description:
#      - indicates whether to install the DigitalOcean agent for monitoring.
#     required: False
#     default: False
#     type: bool
#   tags:
#     description:
#      - List, A list of tag names as strings to apply to the Droplet after it is created. Tag names can either be existing or new tags.
#     required: False
#   maintenance_policy:
#     description:
#      - Dict, An object specifying the maintenance window policy for the Kubernetes cluster (see table below).
#   volumes:
#     description:
#      - List, A list including the unique string identifier for each Block Storage volume to be attached to the Droplet.
#     required: False
#   oauth_token:
#     description:
#      - DigitalOcean OAuth token. Can be specified in C(DO_API_KEY), C(DO_API_TOKEN), or C(DO_OAUTH_TOKEN) environment variables
#     aliases: ['API_TOKEN']
#     required: True
requirements:
    - "python >= 2.6"
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
        self.unique_name = self.module.params.pop('unique_name', False)
        # pop the oauth token so we don't include it in the POST data
        self.module.params.pop('oauth_token')

    def get_by_id(self, cluster_id):
        if not cluster_id:
            return None
        response = self.rest.get('kubernetes/clusters/{0}'.format(cluster_id))
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

    def ensure_running(self, cluster_id):
        end_time = time.time() + self.wait_timeout
        while time.time() < end_time:
            cluster = self.get_by_id(cluster_id)
            if cluster['kubernetes_cluster']['status']['state'] == 'running':
                return cluster
            time.sleep(min(2, end_time - time.time()))
        self.module.fail_json(msg='Wait for Kubernetes cluster to be running')

    def create(self):
        # Get valid Kubernetes options
        kubernetes_options = self.get_kubernetes_options()['options']
        valid_regions = [ str(x['slug']) for x in kubernetes_options['regions'] ]
        # Validate region
        if self.module.params.get('region') not in valid_regions:
            self.module.fail_json(msg='Invalid region {} (valid regions are {})'.format(self.module.params.get('region'), ', '.join(valid_regions)))

        json_data = self.get_kubernetes()

        if json_data:
            self.module.exit_json(changed=False, data=json_data)

        if self.module.check_mode:
            self.module.exit_json(changed=True)

        request_params = dict(self.module.params)
        response = self.rest.post('kubernetes/clusters', data=request_params)
        json_data = response.json

        if response.status_code >= 400:
            self.module.fail_json(changed=False, msg=json_data['message'])

        if self.wait:
            json_data = self.ensure_running(
                json_data['kubernetes_cluster']['id'])

        self.module.exit_json(changed=True, data=json_data['message'])

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
            unique_name=dict(type='bool', default=True),
            region=dict(aliases=['region_id'], default='nyc4'),
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
