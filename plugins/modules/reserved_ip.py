#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: reserved_ip

short_description: Create or delete reserved IPs

version_added: 2.0.0

description:
  - Create or delete reserved IPs.
  - View the create API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Floating-IPs).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  droplet_id:
    description:
      - The ID of the Droplet that the floating IP will be assigned to.
    type: int
    required: false
  floating_ip:
    description:
      - A floating IP address.
    type: str
    required: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create firewall
  community.digitalocean.firewall:
    token: "{{ token }}"
    state: present
    name: firewall
    inbound_rules:
      - protocol: tcp
        ports: 80
        sources:
          - load_balancer_uids:
              - "4de7ac8b-495b-4884-9a69-1050c6793cd6"
    outbound_rules:
      - protocol: tcp
        ports: 80
        destinations:
          - addresses:
            - "0.0.0.0/0"
            - "::/0"
    droplet_ids:
      - 8043964
"""


RETURN = r"""
reserved_ip:
  description: Reserved IP information.
  returned: always
  type: dict
  sample:
    ip: 45.55.96.47
    droplet: null
    region:
      name: New York 3
      slug: nyc3
      features:
        - private_networking
        - backups
        - ipv6
        - metadata
        - install_agent
        - storage
        - image_transfer
      available: true
      sizes:
        - s-1vcpu-1gb
        - s-1vcpu-2gb
        - s-1vcpu-3gb
        - s-2vcpu-2gb
        - s-3vcpu-1gb
        - s-2vcpu-4gb
        - s-4vcpu-8gb
        - s-6vcpu-16gb
        - s-8vcpu-32gb
        - s-12vcpu-48gb
        - s-16vcpu-64gb
        - s-20vcpu-96gb
        - s-24vcpu-128gb
        - s-32vcpu-192g
    locked: true
    project_id: 746c6152-2fa2-11ed-92d3-27aaa54e4988
  links:
    droplets:
      - id: 213939433
        rel: droplet
        href: 'https://api.digitalocean.com/v2/droplets/213939433'
    actions:
      - id: 1088924622
        rel: assign_ip
        href: 'https://api.digitalocean.com/v2/actions/1088924622'
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
    - TODO
"""

import time
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


class ReservedIP:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.droplet_id = module.params.get("droplet_id")
        self.floating_ip = module.params.get("floating_ip")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_reserved_ips(self):
        try:
            reserved_ips = self.client.reserved_ips.list()["reserved_ips"]
            found_reserved_ips = []
            for reserved_ip in reserved_ips:
                if self.state == "present":
                    if reserved_ip["droplet"]:
                        if reserved_ip["droplet"]["id"] == self.droplet_id:
                            found_reserved_ips.append(reserved_ip)
                elif self.state == "absent":
                    if reserved_ip["ip"] == self.floating_ip:
                        found_reserved_ips.append(reserved_ip)
            return found_reserved_ips
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
                firewall=[],
            )

    def create_reserved_ip(self):
        try:
            body = {
                "droplet_id": self.droplet_id,
            }
            reserved_ip = self.client.reserved_ips.create(body=body)["reserved_ip"]
            self.module.exit_json(
                changed=True,
                msg=f"Created reserved IP {reserved_ip['ip']} for Droplet ID {self.droplet_id}",
                reserved_ip=reserved_ip,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, reserved_ip=[]
            )

    def delete_reserved_ip(self, reserved_ip):
        try:
            self.client.reserved_ips.delete(reserved_ip=reserved_ip["ip"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted reserved IP {reserved_ip['ip']}",
                reserved_ip=reserved_ip,
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
                database=[],
            )

    def present(self):
        reserved_ips = self.get_reserved_ips()
        if len(reserved_ips) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Reserved IP for Droplet ID {self.droplet_id} would be created",
                    reserved_ip=[],
                )
            else:
                self.create_reserved_ip()
        elif len(reserved_ips) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Reserved IP for Droplet ID {self.droplet_id} ({reserved_ips[0]['ip']}) exists",
                reserved_ip=reserved_ips[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(reserved_ips)} for Droplet ID {self.droplet_id}",
                reserved_ip=[],
            )

    def absent(self):
        reserved_ips = self.get_reserved_ips()
        if len(reserved_ips) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"Reserved IP {self.floating_ip} does not exist",
                reserved_ip=[],
            )
        elif len(reserved_ips) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Reserved IP {reserved_ips[0]['ip']} would be deleted",
                    reserved_ips=reserved_ips[0],
                )
            else:
                self.delete_reserved_ip(reserved_ip=reserved_ips[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(reserved_ips)} reserved IPs",
                database=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        droplet_id=dict(type="int", required=False),
        floating_ip=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "present", ("droplet_id",)),
            ("state", "absent", ("floating_ip",)),
        ],
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

    ReservedIP(module)


if __name__ == "__main__":
    main()
