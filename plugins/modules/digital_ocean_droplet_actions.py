#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from ansible_collections.community.digitalocean.plugins.module_utils.digital_ocean import DigitalOceanHelper
from ansible.module_utils.basic import AnsibleModule, env_fallback
import traceback
import json
import time
__metaclass__ = type

DOCUMENTATION = r'''
---
module: digital_ocean_droplet_actions
short_description: Perform various DigitalOcean droplet actions
description:
   - Perform various DigitalOcean droplet actions, currently: resize
author: "Mark Mercado (@mamercad)"
options:
  oauth_token:
    description:
     - DigitalOcean OAuth token. Can be specified in C(DO_API_KEY), C(DO_API_TOKEN), or C(DO_OAUTH_TOKEN) environment variables
    aliases: ['API_TOKEN']
    required: True
  id:
    description:
      - The ID of the droplet that you want to operate on.
    type: int
    required: yes
    aliases: ['droplet_id']
  name:
    description:
      - This is the name of the droplet - must be formatted by hostname rules.
    type: string
    required: yes
  action:
    description:
      - Action to perform, currently supported are: resize
    type: string
    required: yes
  action_arguments:
    description:
      - Arguments to pass to the action.
    type: dict
    required: yes

requirements:
  - "python >= 2.6"
'''


EXAMPLES = r'''
- name: Resize an existing droplet
  community.digitalocean.digital_ocean_droplet_actions:
    state: present
    name: mydroplet
    oauth_token: XXX
    size: 2gb
    region: sfo1
    image: ubuntu-16-04-x64
    wait_timeout: 500
    ssh_keys: [ .... ]
  register: my_droplet

- debug:
    msg: "ID is {{ my_droplet.data.droplet.id }}, IP is {{ my_droplet.data.ip_address }}"

- name: Ensure a droplet is present
  community.digitalocean.digital_ocean_droplet:
    state: present
    id: 123
    name: mydroplet
    oauth_token: XXX
    size: 2gb
    region: sfo1
    image: ubuntu-16-04-x64
    wait_timeout: 500

- name: Ensure a droplet is present with SSH keys installed
  community.digitalocean.digital_ocean_droplet:
    state: present
    id: 123
    name: mydroplet
    oauth_token: XXX
    size: 2gb
    region: sfo1
    ssh_keys: ['1534404', '1784768']
    image: ubuntu-16-04-x64
    wait_timeout: 500
'''

RETURN = r'''
# Digital Ocean API info https://developers.digitalocean.com/documentation/v2/#droplets
data:
    description: a DigitalOcean Droplet
    returned: changed
    type: dict
    sample: {
        "ip_address": "104.248.118.172",
        "ipv6_address": "2604:a880:400:d1::90a:6001",
        "private_ipv4_address": "10.136.122.141",
        "droplet": {
            "id": 3164494,
            "name": "example.com",
            "memory": 512,
            "vcpus": 1,
            "disk": 20,
            "locked": true,
            "status": "new",
            "kernel": {
                "id": 2233,
                "name": "Ubuntu 14.04 x64 vmlinuz-3.13.0-37-generic",
                "version": "3.13.0-37-generic"
            },
            "created_at": "2014-11-14T16:36:31Z",
            "features": ["virtio"],
            "backup_ids": [],
            "snapshot_ids": [],
            "image": {},
            "volume_ids": [],
            "size": {},
            "size_slug": "512mb",
            "networks": {},
            "region": {},
            "tags": ["web"]
        }
    }
'''


class DODropletActions(object):
    def __init__(self, module):
        self.rest = DigitalOceanHelper(module)
        self.module = module
        # Pop these parameters so that we don't include them in the POST data
        self.module.params.pop('oauth_token')
        self.module.params.pop('action')
        self.module.params.pop('action_arguments')

    def get_by_id(self, droplet_id):
        if not droplet_id:
            return None
        response = self.rest.get('droplets/{0}'.format(droplet_id))
        json_data = response.json
        if response.status_code == 200:
            return json_data
        return None

    def get_by_name(self, droplet_name):
        if not droplet_name:
            return None
        page = 1
        while page is not None:
            response = self.rest.get('droplets?page={0}'.format(page))
            json_data = response.json
            if response.status_code == 200:
                for droplet in json_data['droplets']:
                    if droplet['name'] == droplet_name:
                        return {'droplet': droplet}
                if 'links' in json_data and 'pages' in json_data['links'] and 'next' in json_data['links']['pages']:
                    page += 1
                else:
                    page = None
        return None

    def get_addresses(self, data):
        """
         Expose IP addresses as their own property allowing users extend to additional tasks
        """
        _data = data
        for k, v in data.items():
            setattr(self, k, v)
        networks = _data['droplet']['networks']
        for network in networks.get('v4', []):
            if network['type'] == 'public':
                _data['ip_address'] = network['ip_address']
            else:
                _data['private_ipv4_address'] = network['ip_address']
        for network in networks.get('v6', []):
            if network['type'] == 'public':
                _data['ipv6_address'] = network['ip_address']
            else:
                _data['private_ipv6_address'] = network['ip_address']
        return _data

    def get_droplet(self):
        json_data = self.get_by_id(self.module.params['id'])
        if not json_data and self.unique_name:
            json_data = self.get_by_name(self.module.params['name'])
        return json_data

    def create(self):
        json_data = self.get_droplet()
        droplet_data = None
        if json_data:
            droplet_data = self.get_addresses(json_data)
            self.module.exit_json(changed=False, data=droplet_data)
        if self.module.check_mode:
            self.module.exit_json(changed=True)
        request_params = dict(self.module.params)
        del request_params['id']
        response = self.rest.post('droplets', data=request_params)
        json_data = response.json
        if response.status_code >= 400:
            self.module.fail_json(changed=False, msg=json_data['message'])
        if self.wait:
            json_data = self.ensure_power_on(json_data['droplet']['id'])
            droplet_data = self.get_addresses(json_data)
        self.module.exit_json(changed=True, data=droplet_data)

    def delete(self):
        json_data = self.get_droplet()
        if json_data:
            if self.module.check_mode:
                self.module.exit_json(changed=True)
            response = self.rest.delete(
                'droplets/{0}'.format(json_data['droplet']['id']))
            json_data = response.json
            if response.status_code == 204:
                self.module.exit_json(changed=True, msg='Droplet deleted')
            self.module.fail_json(
                changed=False, msg='Failed to delete droplet')
        else:
            self.module.exit_json(changed=False, msg='Droplet not found')

    def ensure_power_on(self, droplet_id):
        end_time = time.time() + self.wait_timeout
        while time.time() < end_time:
            response = self.rest.get('droplets/{0}'.format(droplet_id))
            json_data = response.json
            if json_data['droplet']['status'] == 'active':
                return json_data
            time.sleep(min(2, end_time - time.time()))
        self.module.fail_json(msg='Wait for droplet powering on timeout')


def core(module):
    state = module.params.pop('state')
    droplet = DODropletActions(module)
    if state == 'present':
        droplet.create()
    elif state == 'absent':
        droplet.delete()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            oauth_token=dict(
                aliases=['API_TOKEN'],
                no_log=True,
                fallback=(env_fallback, ['DO_API_TOKEN',
                                         'DO_API_KEY', 'DO_OAUTH_TOKEN'])
            ),
            id=dict(aliases=['droplet_id'], type='int'),
            name=dict(type='str'),
            action=dict(type='str'),
            action_arguments=dict(type=dict),
        ),
        required_one_of=(
            ['id', 'name'],
        ),
        supports_check_mode=True,
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == '__main__':
    main()
