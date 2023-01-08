#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: vpc

short_description: Create or delete VPCs

version_added: 2.0.0

description:
  - Create or delete VPCs.
  - |
    VPCs (virtual private clouds) allow you to create virtual networks containing resources that
    can communicate with each other in full isolation using private IP addresses.
  - View the create API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/VPCs).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - The name of the VPC. Must be unique and may only contain alphanumeric characters, dashes, and periods.
    type: str
    required: true
  description:
    description:
      - A free-form text field for describing the VPC's purpose. It may be a maximum of 255 characters.
    type: str
    required: false
  region:
    description:
      - The slug identifier for the region where the VPC will be created.
    type: str
    required: true
  ip_range:
    description:
      - The range of IP addresses in the VPC in CIDR notation.
      - |
        Network ranges cannot overlap with other networks in the same account and must be in range
        of private addresses as defined in RFC1918.
      - It may not be smaller than /28 nor larger than /16.
      - |
        If no IP range is specified, a /20 network range is generated that won't conflict with
        other VPC networks in your account.
    type: str
    required: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create VPC
  community.digitalocean.vpc:
    token: "{{ token }}"
    state: present
    name: env.prod-vpc
    region: nyc1
    ip_range: "10.10.10.0/24"
"""


RETURN = r"""
vpc:
  description: VPC information.
  returned: always
  type: dict
  sample:
    name: env.prod-vpc
    description: VPC for production environment
    region: nyc1
    ip_range: 10.10.10.0/24
    default: true
    id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    urn: 'do:vpc:5a4981aa-9653-4bd1-bef5-d6bff52042e4'
    created_at: '2020-03-13T19:20:47.442049222Z'
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Droplet result information.
  returned: always
  type: str
  sample:
    - Created VPC env.prod-vpc (5a4981aa-9653-4bd1-bef5-d6bff52042e4)
    - Deleted VPC env.prod-vpc (5a4981aa-9653-4bd1-bef5-d6bff52042e4)
    - VPC env.prod-vpc would be created
    - VPC env.prod-vpc (5a4981aa-9653-4bd1-bef5-d6bff52042e4) exists
    - VPC env.prod-vpc does not exist
    - VPC env.prod-vpc (5a4981aa-9653-4bd1-bef5-d6bff52042e4) would be deleted
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.digitalocean.plugins.module_utils.common import (
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


class VPC:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.name = module.params.get("name")
        self.description = module.params.get("description")
        self.region = module.params.get("region")
        self.ip_range = module.params.get("ip_range")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_vpcs(self):
        try:
            vpcs = self.client.vpcs.list()["vpcs"]
            found_vpcs = []
            for vpc in vpcs:
                if self.name == vpc["name"]:
                    found_vpcs.append(vpc)
            return found_vpcs
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
                vpc=[],
            )

    def create_vpc(self):
        try:
            body = {
                "name": self.name,
                "description": self.description,
                "region": self.region,
                "ip_range": self.ip_range,
            }
            vpc = self.client.vpcs.create(body=body)["vpc"]

            self.module.exit_json(
                changed=True,
                msg=f"Created VPC {self.name} ({(vpc['id'])})",
                vpc=vpc,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, droplet=[]
            )

    def delete_vpc(self, vpc):
        try:
            self.client.vpcs.delete(vpc_id=vpc["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted VPC {self.name} ({vpc['id']})",
                vpc=vpc,
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
                vpc=[],
            )

    def present(self):
        vpcs = self.get_vpcs()
        if len(vpcs) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"VPC {self.name} would be created",
                    vpc=[],
                )
            else:
                self.create_vpc()
        elif len(vpcs) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"VPC {self.name} ({vpcs[0]['id']}) exists",
                vpc=vpcs[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(vpcs)} named {self.name}",
                vpc=[],
            )

    def absent(self):
        vpcs = self.get_vpcs()
        if len(vpcs) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"VPC {self.name} does not exist",
                vpc=[],
            )
        elif len(vpcs) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"VPC {self.name} {vpcs[0]['id']} would be deleted",
                    vpc=vpcs[0],
                )
            else:
                self.delete_vpc(vpc=vpcs[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(vpcs)} VPCs named {self.name}",
                vpc=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        region=dict(type="str", required=True),
        ip_range=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
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

    VPC(module)


if __name__ == "__main__":
    main()
