#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2018, Ansible Project
# Copyright: (c) 2021, Mark Mercado <mamercad@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: digital_ocean_vpc
short_description: Create and delete DigitalOcean VPCs
version_added: 1.7.0
description:
  - This module can be used to create and delete DigitalOcean VPCs.
author: "Mark Mercado (@mamercad)"
options:
  state:
    description:
      - Whether the VPC should be present (created) or absent (deleted).
    default: present
    choices:
      - present
      - absent
    type: str
  name:
    description:
      - The name of the VPC.
      - Must be unique and contain alphanumeric characters, dashes, and periods only.
    type: str
  description:
    description:
      - A free-form text field for describing the VPC's purpose.
      - It may be a maximum of 255 characters.
    type: str
  region:
    description:
      - The slug identifier for the region where the VPC will be created.
    type: str
  ip_range:
    description:
      - The requested range of IP addresses for the VPC in CIDR notation.
      - Network ranges cannot overlap with other networks in the same account and must be in range of private addresses as defined in RFC1918.
      - It may not be smaller than /24 nor larger than /16.
      - If no IP range is specified, a /20 network range is generated that won't conflict with other VPC networks in your account.
    type: str
  vpc_id:
    description:
      - VPC ID to delete.
    type: str
extends_documentation_fragment:
- community.digitalocean.digital_ocean.documentation

"""


EXAMPLES = r"""
- name: Create a VPC
  community.digitalocean.digital_ocean_vpc:
    state: present
    name: myvpc1
    region: nyc1

- name: Delete a VPC
  community.digitalocean.digital_ocean_vpc:
    state: absent
    vpc_id: a3b72d97-192f-4984-9d71-08a5faf2e0c7
"""


RETURN = r"""
data:
  description: A DigitalOcean VPC.
  returned: success
  type: dict
  sample:
    created_at: '2021-06-17T11:43:12.12121565Z'
    default: false
    description: ''
    id: a3b72d97-192f-4984-9d71-08a5faf2e0c7
    ip_range: 10.116.16.0/20
    name: testvpc1
    region: nyc1
    urn: do:vpc:a3b72d97-192f-4984-9d71-08a5faf2e0c7
"""


import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.digitalocean.plugins.module_utils.digital_ocean import (
    DigitalOceanHelper,
)


class DOVPC(object):
    def __init__(self, module):
        self.rest = DigitalOceanHelper(module)
        self.module = module
        # pop the oauth token so we don't include it in the POST data
        self.module.params.pop("oauth_token")
        self.name = module.params.get("name", None)
        self.description = module.params.get("description", None)
        self.region = module.params.get("region", None)
        self.ip_range = module.params.get("ip_range", None)
        self.vpc_id = module.params.get("vpc_id", None)

    def create(self):
        if self.module.check_mode:
            return self.module.exit_json(changed=True)

        data = {
            "name": self.name,
            "region": self.region,
        }
        if self.description is not None:
            data["description"] = self.description
        if self.ip_range is not None:
            data["ip_range"] = self.ip_range

        response = self.rest.post("vpcs", data=data)
        status = response.status_code
        json = response.json
        if status == 201:
            self.module.exit_json(changed=True, data=json["vpc"])
        else:
            self.module.fail_json(
                changed=False,
                msg="Failed to create VPC: {0}".format(json["message"]),
            )

    def delete(self):
        if self.module.check_mode:
            return self.module.exit_json(changed=True)

        response = self.rest.delete("vpcs/{0}".format(str(self.vpc_id)))
        status = response.status_code
        if status == 204:
            self.module.exit_json(
                changed=True,
                msg="Deleted VPC {0}".format(str(self.vpc_id)),
            )
        else:
            json = response.json
            self.module.fail_json(
                changed=False,
                msg="Failed to delete VPC {0}: {1}".format(
                    self.vpc_id, json["message"]
                ),
            )


def run(module):
    state = module.params.pop("state")
    vpc = DOVPC(module)
    if state == "present":
        vpc.create()
    elif state == "absent":
        vpc.delete()


def main():
    argument_spec = DigitalOceanHelper.digital_ocean_argument_spec()
    argument_spec.update(
        state=dict(choices=["present", "absent"], default="present"),
        name=dict(type="str"),
        description=dict(type="str"),
        region=dict(type="str"),
        ip_range=dict(type="str"),
        vpc_id=dict(type="str"),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ["state", "present", ["name", "region"]],
            ["state", "absent", ["vpc_id"]],
        ],
        mutually_exclusive=[["name", "vpc_id"]],
        supports_check_mode=True,
    )

    run(module)


if __name__ == "__main__":
    main()
