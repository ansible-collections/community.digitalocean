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
volume:
  description: DigitalOcean volume information.
  returned: always
  type: dict
  sample:
    created_at: '2022-11-24T19:23:01Z'
    description: ''
    droplet_ids: null
    filesystem_label: ''
    filesystem_type: ''
    id: 698d7221-6c2d-11ed-93f9-0a58ac14790c
    name: test-vol
    region:
      available: true
      features:
        - backups
        - ipv6
        - metadata
        - install_agent
        - storage
        - image_transfer
      name: New York 3
      sizes:
        - s-1vcpu-1gb
        - s-1vcpu-1gb-amd
        - s-1vcpu-1gb-intel
        - ...
      slug: nyc3
    size_gigabytes: 1
    tags: null
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: DigitalOcean volume information.
  returned: always
  type: str
  sample:
    - Created volume test-vol in nyc3
    - Deleted volume test-vol in nyc3
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

    def get_volumes_by_region(self):
        volumes = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.volumes,
            meth="list",
            key="volumes",
            params=None,
            exc=HttpResponseError,
        )
        found_volumes = []
        for volume in volumes:
            volume_region = volume.get("region")
            if volume_region == self.region:
                found_volumes.append(volume)
        return found_volumes

    def get_droplets_by_region(self):
        droplets = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.droplets,
            meth="list",
            key="droplets",
            params=None,
            exc=HttpResponseError,
        )
        found_droplets = []
        for droplet in droplets:
            droplet_region = droplet["region"]["slug"]
            if droplet_region == self.region:
                found_droplets.append(droplet)
        droplets_id_name_region = [
            {
                "id": droplet["id"],
                "name": droplet["name"],
                "region": droplet["region"]["slug"],
            }
            for droplet in found_droplets
        ]
        return droplets_id_name_region

    def attach_volume(self):
        volumes = self.get_volumes_by_region()
        droplets = self.get_droplets_by_region()
        self.module.exit_json(
            changed=True,
            msg=f"Attached volume {self.volume_name} to {self.droplet_name} in {self.region}",
            volume_action=[],
            volumes=volumes,
            droplets=droplets,
        )

    def detach_volume(self):
        self.module.exit_json(
            changed=True,
            msg=f"Detached volume {self.volume_name} from {self.droplet_name} in {self.region}",
            volume_action=[],
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
