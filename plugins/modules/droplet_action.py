#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: droplet_action

short_description: Perform Droplet actions

version_added: 2.0.0

description:
  - Perform Droplet actions.
  - Droplet actions are tasks that can be executed on a Droplet.
  - These can be things like rebooting, resizing, snapshotting, etc.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Droplet-Actions).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  droplet_id:
    description:
      - A unique identifier for a Droplet instance.
      - If provided, C(name) and C(region) are ignore.
    type: int
    required: false
  name:
    description:
      - The name of the Droplet to act on.
      - If provided, must be unique and given with C(region).
    type: str
    required: false
  region:
    description:
      - The name of the Droplet to act on.
      - Required with C(name).
    type: str
    required: false
    choices: ["ams1", "ams2", "ams3", "blr1", "fra1", "lon1", "nyc1", "nyc2", "nyc3", "sfo1", "sfo2", "sfo3", "sgp1", "tor1"]
  type:
    description:
      - The action that will be taken on the Droplet.
      - Some actions will require additional attributes to be set as well.
    type: str
    required: true
    choices:
    #   - enable_backups
    #   - disable_backups
    #   - reboot
    #   - power_cycle
    #   - shutdown
    #   - power_off
    #   - power_on
    #   - restore
    #   - password_reset
    #   - resize
    #   - rebuild
    #   - rename
    #   - change_kernel
    #   - enable_ipv6
      - snapshot
  snapshot_name:
    description:
      - The name to give the new snapshot of the Droplet.
    type: str
    required: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Snapshot a Droplet
  community.digitalocean.droplet_action:
    token: "{{ token }}"
    state: present
    name: my-droplet
    region: nyc3
    type: snapshot
    snapshot_name: my-droplet-snapshot
"""


RETURN = r"""
action:
  description: DigitalOcean action information.
  returned: always
  type: dict
  sample:
    id: 36804636
    status: completed
    type: create
    started_at: '2020-11-14T16:29:21Z'
    completed_at: '2020-11-14T16:30:06Z'
    resource_id: 3164444
    resource_type: droplet
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
    region_slug: string
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: DigitalOcean action information.
  returned: always
  type: str
  sample:
    - No Droplet with ID 336851565
    - No Droplet with name test-droplet-1 in nyc3
    - Droplet test-droplet-1 (336851565) in nyc3 would be sent action 'snapshot'
    - Droplet test-droplet-1 (336851565) in nyc3 sent action 'snapshot'
"""

import time
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.digitalocean.plugins.module_utils.common import (
    DigitalOceanOptions,
    DigitalOceanFunctions,
    DigitalOceanConstants,
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


class DropletAction:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.timeout = module.params.get("timeout")
        self.droplet_id = module.params.get("droplet_id")
        self.name = module.params.get("name")
        self.region = module.params.get("region")
        self.type = module.params.get("type")
        self.snapshot_name = module.params.get("snapshot_name")

        self.droplet = self.find_droplet()

        if self.state == "present":
            self.present()

    def find_droplet(self):
        if self.droplet_id:
            try:
                droplet = self.client.droplets.get(droplet_id=self.droplet_id)[
                    "droplet"
                ]
                if droplet:
                    return droplet
                self.module.fail_json(
                    changed=False,
                    msg=f"No Droplet with ID {self.droplet_id}",
                    action=[],
                )
            except HttpResponseError as err:
                error = {
                    "Message": err.error.message,
                    "Status Code": err.status_code,
                    "Reason": err.reason,
                }
                self.module.fail_json(
                    changed=False, msg=error.get("Message"), error=error, action=[]
                )
        elif self.name and self.region:
            droplets = DigitalOceanFunctions.get_droplet_by_name_in_region(
                module=self.module,
                client=self.client,
                region=self.region,
                name=self.name,
            )
            if len(droplets) == 0:
                self.module.fail_json(
                    changed=False,
                    msg=f"No Droplet named {self.name} in {self.region}",
                    action=[],
                )
            elif len(droplets) > 1:
                self.module.fail_json(
                    changed=False,
                    msg=f"Multiple Droplets ({len(droplets)}) named {self.name} found in {self.region}",
                    action=[],
                )
            return droplets[0]

        self.module.fail_json(
            changed=False,
            msg="Should not reach this",
            action=[],
        )

    def get_action_by_id(self, action_id):
        try:
            action = self.client.actions.get(action_id=action_id)["action"]
            return action
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, action=[]
            )

    def snapshot(self):
        try:
            body = {
                "type": self.type,
                "name": self.snapshot_name,
            }
            action = self.client.droplet_actions.post(
                droplet_id=self.droplet["id"], body=body
            )["action"]

            status = action["status"]
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time and status != "completed":
                time.sleep(DigitalOceanConstants.SLEEP)
                status = self.get_action_by_id(action_id=action["id"])

            self.module.exit_json(
                changed=True,
                msg=f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} sent action '{self.type}'",
                action=action,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, action=[]
            )

    def present(self):
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} would be sent action '{self.type}'",
            )

        if self.type == "snapshot":
            self.snapshot()

        self.module.fail_json(changed=False, msg="Should not get here")


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        droplet_id=dict(type="int", required=False),
        name=dict(type="str", required=False),
        region=dict(
            type="str",
            choices=[
                "ams1",
                "ams2",
                "ams3",
                "blr1",
                "fra1",
                "lon1",
                "nyc1",
                "nyc2",
                "nyc3",
                "sfo1",
                "sfo2",
                "sfo3",
                "sgp1",
                "tor1",
            ],
            required=False,
        ),
        type=dict(
            type="str",
            choices=[
                # "enable_backups",
                # "disable_backups",
                # "reboot",
                # "power_cycle",
                # "shutdown",
                # "power_off",
                # "power_on",
                # "restore",
                # "password_reset",
                # "resize",
                # "rebuild",
                # "rename",
                # "change_kernel",
                # "enable_ipv6",
                "snapshot",
            ],
            required=True,
        ),
        snapshot_name=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[("droplet_id", "name")],
        mutually_exclusive=[("droplet_id", "name")],
        required_together=[("name", "region")],
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

    DropletAction(module)


if __name__ == "__main__":
    main()
