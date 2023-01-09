#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: firewall

short_description: Create or delete firewalls

version_added: 2.0.0

description:
  - Create or delete firewalls.
  - |
    DigitalOcean Cloud Firewalls provide the ability to restrict network access to and from a
    Droplet allowing you to define which ports will accept inbound or outbound connections.
  - View the create API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Firewalls).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - A human-readable name for a firewall.
      - The name must begin with an alphanumeric character.
      - Subsequent characters must either be alphanumeric characters, a period (.), or a dash (-).
    type: str
    required: true
  droplet_ids:
    description:
      - An array containing the IDs of the Droplets assigned to the firewall.
    type: list
    elements: int
    required: false
  tags:
    description:
      - A flat array of tag names as strings to be applied to the resource.
      - Tag names may be for either existing or new tags.
    type: list
    elements: str
    required: false
  inbound_rules:
    description:
      - Array of inbound firewall rules.
    type: list
    elements: dict
  outbound_rules:
    description:
      - Array of outbound firewall rules.
    type: list
    elements: dict

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
firewall:
  description: Firewall information.
  returned: always
  type: dict
  sample:
    firewall:
      id: bb4b2611-3d72-467b-8602-280330ecd65c
      name: firewall
      status: waiting
      inbound_rules:
        - protocol: tcp
          ports: '80'
          sources:
            load_balancer_uids:
              - 4de7ac8b-495b-4884-9a69-1050c6793cd6
        - protocol: tcp
          ports: '22'
          sources:
            tags:
              - gateway
            addresses:
              - 18.0.0.0/8
      outbound_rules:
        - protocol: tcp
          ports: '80'
          destinations:
            addresses:
              - 0.0.0.0/0
              - '::/0'
      created_at: '2017-05-23T21:24:00Z'
      droplet_ids:
        - 8043964
      tags: []
      pending_changes:
        - droplet_id: 8043964
          removing: false
          status: waiting
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
    - Created firewall test-firewall (e23647ff-4b57-4da0-8f31-72616d932c0d)
    - Deleted firewall test-firewall (e23647ff-4b57-4da0-8f31-72616d932c0d)
    - Firewall test-firewall would be created
    - Firewall test-firewall (e23647ff-4b57-4da0-8f31-72616d932c0d) exists
    - Firewall test-firewall does not exist
    - Firewall test-firewall (e23647ff-4b57-4da0-8f31-72616d932c0d) would be deleted
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


class Firewall:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.name = module.params.get("name")
        self.droplet_ids = module.params.get("droplet_ids")
        self.tags = module.params.get("tags")
        self.inbound_rules = module.params.get("inbound_rules")
        self.outbound_rules = module.params.get("outbound_rules")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_firewalls(self):
        try:
            firewalls = self.client.firewalls.list()["firewalls"]
            found_firewalls = []
            for firewall_cluster in firewalls:
                if self.name == firewall_cluster["name"]:
                    found_firewalls.append(firewall_cluster)
            return found_firewalls
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

    def create_firewall(self):
        try:
            body = {
                "name": self.name,
                "droplet_ids": self.droplet_ids,
                "tags": self.tags,
                "inbound_rules": self.inbound_rules,
                "outbound_rules": self.outbound_rules,
            }
            firewall = self.client.firewalls.create(body=body)["firewall"]

            self.module.exit_json(
                changed=True,
                msg=f"Created firewall {self.name} ({firewall['id']})",
                firewall=firewall,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, firewall=[]
            )

    def delete_firewall(self, firewall):
        try:
            self.client.firewalls.delete(firewall_id=firewall["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted firewall {self.name} ({firewall['id']})",
                firewall=firewall,
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
                firewall=[],
            )

    def present(self):
        firewalls = self.get_firewalls()
        if len(firewalls) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Firewall {self.name} would be created",
                    firewall=[],
                )
            else:
                self.create_firewall()
        elif len(firewalls) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Firewall {self.name} ({firewalls[0]['id']}) exists",
                firewall=firewalls[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(firewalls)} named {self.name}",
                firewall=[],
            )

    def absent(self):
        firewalls = self.get_firewalls()
        if len(firewalls) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"Firewall {self.name} does not exist",
                firewall=[],
            )
        elif len(firewalls) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Firewall {self.name} ({firewalls[0]['id']}) would be deleted",
                    firewall=firewalls[0],
                )
            else:
                self.delete_firewall(firewall=firewalls[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(firewalls)} firewalls named {self.name}",
                database=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        droplet_ids=dict(type="list", elements="int", required=False),
        tags=dict(type="list", elements="str", required=False),
        inbound_rules=dict(type="list", elements="dict", required=False),
        outbound_rules=dict(type="list", elements="dict", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "present", ("inbound_rules", "outbound_rules"), True),
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

    Firewall(module)


if __name__ == "__main__":
    main()
