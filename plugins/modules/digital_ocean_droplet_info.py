#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2018, Ansible Project
# Copyright: (c) 2020, Tyler Auerbeck <tauerbec@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: digital_ocean_droplet_info
short_description: Gather information about DigitalOcean Droplets
description:
    - This module can be used to gather information about Droplets.
author: "Tyler Auerbeck (@tylerauerbeck)"

requirements:
  - "python >= 2.6"

extends_documentation_fragment:
- community.digitalocean.digital_ocean.documentation
'''


EXAMPLES = r'''
- name: Gather information about all droplets
  community.digitalocean.digital_ocean_droplet_info:
    oauth_token: "{{ oauth_token }}"

- name: Gather information about a specific droplet by name
  community.digitalocean.digital_ocean_account_info:
    oauth_token: "{{ oauth_token }}"
    name: my-droplet-name

- name: Gather information about a specific droplet by id
  community.digitalocean.digital_ocean_account_info:
    oauth_token: "{{ oauth_token }}"
    id: abc-123-d45
'''

#TODO: Update return example
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

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.digitalocean.plugins.module_utils.digital_ocean import DigitalOceanHelper
from ansible.module_utils._text import to_native


def core(module):
    rest = DigitalOceanHelper(module)

    if module.params["id"] is None and module.params["name"] is None:
      response = rest.get("droplets")

      if response.status_code != 200:
        module.fail_json(msg="Failed to fetch 'droplets' information due to error : %s" % response.json['message'])

      data = response.json["droplets"]

    elif module.params["id"] is not None:
      response = rest.get("droplets/" + module.params["id"])

      if response.status_code != 200:
        module.fail_json(msg="Failed to fetch 'droplets' information due to error : %s" % response.json['message'])

      data = response.json["droplet"]

    elif module.params["name"] is not None:
      response = rest.get("droplets")

      if response.status_code != 200:
        module.fail_json(msg="Failed to fetch 'droplets' information due to error : %s" % response.json['message'])

      else:
        for droplet in response.json["droplets"]:
          if droplet["name"] == module.params["name"]:
            data = {"droplet": droplet}
            break
          else:
            data = {}

    module.exit_json(changed=False, data=data)


def main():
    argument_spec = DigitalOceanHelper.digital_ocean_argument_spec()
    argument_spec.update(
            name=dict(type='str', required=False, default=None),
            id=dict(type='str', required=False, default=None)
    )
    module = AnsibleModule(argument_spec=argument_spec)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == '__main__':
    main()
