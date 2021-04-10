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

options:
  id:
    description:
      - Droplet ID that can be used to identify and reference a droplet.
    required: false
    type: str
  name:
    description:
      - Droplet name that can be used to identify and reference a droplet.
    required: false
    type: str

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

RETURN = r'''
data:
    description: DigitalOcean droplet information
    returned: success
    type: list
    sample: [
        {
            "backup_ids": [],
            "created_at": "2021-04-07T00:44:53Z",
            "disk": 25,
            "features": ["private_networking"],
            "id": 123456789,
            "image":
                "created_at": "2020-10-20T08:49:55Z",
                "description": "Ubuntu 18.04 x86 image",
                "distribution": "Ubuntu",
                "id": 72061309,
                "min_disk_size": 15,
                "name": "18.04 (LTS) x64",
                "public": false,
                "regions": [],
                "size_gigabytes": 0.34,
                "slug": null,
                "status": "retired",
                "tags": [],
                "type": "base"
                },
            "kernel": null,
            "locked": false,
            "memory": 1024,
            "name": "ubuntu-s-1vcpu-1gb-nyc1-1234",
            "networks": {
                "v4": [
                    {
                        "gateway": "",
                        "ip_address": "1.2.3.4",
                        "netmask": "255.255.240.0",
                        "type": "private"
                    },
                    {
                        "gateway": "3.4.5.6",
                        "ip_address": "1.2.3.4",
                        "netmask": "255.255.240.0",
                        "type": "public"
                        }
                ],
                "v6": []
            },
            "next_backup_window": null,
            "region": {
                "available": true,
                "features": ["backups", "ipv6", "metadata", "install_agent", "storage", "image_transfer"],
                "name": "New York 1",
                "sizes" ["list-of-sizes"]
                "slug": "nyc1"
            },
            "size": {
                    "available": true,
                    "description": "Basic",
                    "disk": 25,
                    "memory": 1024,
                    "price_hourly": 0.00744,
                    "price_monthly": 5.0,
                    "regions": ["ams2", "ams3", "blr1", "fra1", "lon1", "nyc1", "nyc2", "nyc3", "sfo1", "sfo3", "sgp1", "tor1"],
                    "slug": "s-1vcpu-1gb",
                    "transfer": 1.0,
                    "vcpus": 1
            },
            "size_slug": "s-1vcpu-1gb",
            "snapshot_ids": [],
            "status": "active",
            "tags": ["tag1"],
            "vcpus": 1,
            "volume_ids": [],
            "vpc_uuid": "1f5e24b6-8c1d-4ace-bd8f-430096ba42ca"
        }
    ]
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
            data = droplet
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
