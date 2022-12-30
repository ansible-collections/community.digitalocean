#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: volume_action

short_description: Attach or detach volumes from Droplets

version_added: 2.0.0

description:
  - Attach or detach volumes from Droplets.
  - Block storage actions are commands that can be given to a DigitalOcean Block Storage Volume.
  - Each volume may only be attached to a single Droplet.
  - However, up to five volumes may be attached to a Droplet at a time.
  - |
    Pre-formatted volumes will be automatically mounted to Ubuntu, Debian, Fedora, Fedora Atomic,
    and CentOS Droplets created on or after April 26, 2018 when attached.
  - On older Droplets, additional configuration is required.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Block-Storage-Actions).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  volume_name:
    description:
      - The name of the block storage volume to attach or detach.
    type: str
    required: true
  droplet_name:
    description:
      - The name of the Droplet to attach or detach to the volume to.
    type: int
    required: true
  region:
    description:
      - Set to the slug representing the region where the volume and Droplet is located.
    choices: ["ams1", "ams2", "ams3", "blr1", "fra1", "lon1", "nyc1", "nyc2", "nyc3", "sfo1", "sfo2", "sfo3", "sgp1", "tor1"]
    type: str
    required: true

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Attach volume to Droplet
  community.digitalocean.volume_action:
    token: "{{ token }}"
    state: present
    volume_name: test-vol-delete-1
    droplet_name: test-droplet-delete-1
    region: nyc3

- name: Detach volume from Droplet
  community.digitalocean.volume_action:
    token: "{{ token }}"
    state: absent
    volume_name: test-vol-delete-1
    droplet_name: test-droplet-delete-1
    region: nyc3
"""


RETURN = r"""
action:
  description: DigitalOcean volume action information.
  returned: always
  type: dict
  sample:
    id: 72531856
    status: completed
    type: attach_volume
    started_at: '2020-11-12T17:51:03Z'
    completed_at: '2020-11-12T17:51:14Z'
    resource_type: volume
    region:
      name: New York 1
      slug: nyc1
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
        - s-32vcpu-192gb
      features:
        - private_networking
        - backups
        - ipv6
        - metadata
      available: true
    region_slug: nyc1
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: DigitalOcean volume action information.
  returned: always
  type: str
  sample:
    - No volume named test-vol in nyc3
    - Multiple volumes named test-vol in nyc3
    - No Droplet named test-droplet in nyc3
    - Multiple Droplets named test-droplet in nyc3
    - Volume test-vol in nyc3 attached to test-droplet
    - Attached volume test-vol in nyc3 to test-droplet
    - Volume test-vol in nyc3 not attached to test-droplet
    - Detached volume test-vol in nyc3 from test-droplet
"""

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


class VolumeAction:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.volume_name = module.params.get("volume_name")
        self.droplet_name = module.params.get("droplet_name")
        self.region = module.params.get("region")
        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_volume_by_name(self):
        volumes = DigitalOceanFunctions.get_volume_by_name_in_region(
            module=self.module,
            client=self.client,
            region=self.region,
            name=self.volume_name,
        )
        if len(volumes) == 0:
            self.module.fail_json(
                changed=False,
                msg=f"No volume named {self.volume_name} in {self.region}",
                action=[],
            )
        elif len(volumes) > 1:
            self.module.fail_json(
                changed=False,
                msg=f"Multiple volumes ({len(volumes)}) found in {self.region}",
                action=[],
            )
        return volumes[0]

    def get_droplet_by_name(self):
        droplets = DigitalOceanFunctions.get_droplet_by_name_in_region(
            module=self.module,
            client=self.client,
            region=self.region,
            name=self.droplet_name,
        )
        if len(droplets) == 0:
            self.module.fail_json(
                changed=False,
                msg=f"No Droplet named {self.droplet_name} in {self.region}",
                action=[],
            )
        elif len(droplets) > 1:
            self.module.fail_json(
                changed=False,
                msg=f"Multiple Droplets ({len(droplets)}) found in {self.region}",
                action=[],
            )
        return droplets[0]

    def attach_volume(self):
        volume = self.get_volume_by_name()
        droplet = self.get_droplet_by_name()

        if droplet["id"] in volume["droplet_ids"]:
            self.module.exit_json(
                changed=False,
                msg=f"Volume {self.volume_name} in {self.region} attached to {self.droplet_name}",
                action=[],
            )

        try:
            body = {
                "type": "attach",
                "volume_name": self.volume_name,
                "droplet_id": droplet["id"],
                "region": self.region,
            }
            action = self.client.volume_actions.post(body=body)["action"]
            self.module.exit_json(
                changed=True,
                msg=f"Attached volume {self.volume_name} in {self.region} to {self.droplet_name}",
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

    def detach_volume(self):
        volume = self.get_volume_by_name()
        droplet = self.get_droplet_by_name()

        if droplet["id"] not in volume["droplet_ids"]:
            self.module.exit_json(
                changed=False,
                msg=f"Volume {self.volume_name} in {self.region} not attached to {self.droplet_name}",
                action=[],
            )

        try:
            body = {
                "type": "detach",
                "volume_name": self.volume_name,
                "droplet_id": droplet["id"],
                "region": self.region,
            }
            action = self.client.volume_actions.post(body=body)["action"]
            self.module.exit_json(
                changed=True,
                msg=f"Detached volume {self.volume_name} in {self.region} from {self.droplet_name}",
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
        self.attach_volume()

    def absent(self):
        self.detach_volume()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        volume_name=dict(type="str", required=True),
        droplet_name=dict(type="str", required=True),
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
            required=True,
        ),
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

    VolumeAction(module)


if __name__ == "__main__":
    main()
