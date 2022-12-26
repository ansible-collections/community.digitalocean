#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: volume

short_description: Create or delete volumes

version_added: 2.0.0

description:
  - Creates or deletes volumes.
  - View the create API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/volumes_create).
  - View the delete API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/volumes_delete_byName).
  - |
    Optionally, a filesystem_type attribute may be provided in order to
    automatically format the volume's filesystem.
  - |
    Pre-formatted volumes are automatically mounted when attached to Ubuntu, Debian, Fedora, Fedora
    Atomic, and CentOS Droplets created on or after April 26, 2018.
  - |
    Attaching pre-formatted volumes to Droplets without support for
    auto-mounting is not recommended.

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - A human-readable name for the block storage volume.
      - |
        Must be lowercase and be composed only of numbers, letters and "-", up to a limit of 64
        characters.
      - The name must begin with a letter.
    type: str
    required: true
  description:
    description:
      - An optional free-form text field to describe a block storage volume.
    type: str
    required: false
  size_gigabytes:
    description:
      - The size of the block storage volume in GiB C(1024^3).
    type: int
    required: false
  tags:
    description:
      - A flat array of tag names as strings to be applied to the resource.
      - Tag names may be for either existing or new tags.
    type: list
    elements: str
    required: false
  snapshot_id:
    description:
      - The unique identifier for the volume snapshot from which to create the volume.
    type: str
    required: false
  filesystem_type:
    description:
      - The name of the filesystem type to be used on the volume.
      - When provided, the volume will automatically be formatted to the specified filesystem type.
      - Currently, the available options are C(ext4) and C(xfs).
      - |
        Pre-formatted volumes are automatically mounted when attached to Ubuntu, Debian, Fedora,
        Fedora Atomic, and CentOS Droplets created on or after April 26, 2018.
      - Attaching pre-formatted volumes to other Droplets is not recommended.
    type: str
    choices: ["ext4", "xfs"]
    required: false
  region:
    description:
      - The slug identifier for the region where the resource will initially be available.
    choices: ["ams1", "ams2", "ams3", "blr1", "fra1", "lon1", "nyc1", "nyc2", "nyc3", "sfo1", "sfo2", "sfo3", "sgp1", "tor1"]
    type: str
    required: true
  filesystem_label:
    description:
      - The label applied to the filesystem.
      - |
        Labels for ext4 type filesystems may contain 16 characters while labels for xfs type
        filesystems are limited to 12 characters.
      - May only be used in conjunction with filesystem_type.
    type: str
    required: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create DigitalOcean volume
  community.digitalocean.volume:
    token: "{{ token }}"
    state: present
    name: test-vol-delete-1
    region: nyc3
    size_gigabytes: 1

- name: Delete DigitalOcean volume
  community.digitalocean.volume:
    token: "{{ token }}"
    state: absentj
    name: test-vol-delete-1
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


class Volume:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.name = module.params.get("name")
        self.description = module.params.get("description")
        self.size_gigabytes = int(module.params.get("size_gigabytes"))
        self.tags = module.params.get("tags")
        self.snapshot_id = module.params.get("snapshot_id")
        self.filesystem_type = module.params.get("filesystem_type")
        self.region = module.params.get("region")
        self.filesystem_label = module.params.get("filesystem_label")
        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_volumes_by_name_and_region(self):
        volumes = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.volumes,
            meth="list",
            key="volumes",
            params=dict(name=self.name),
            exc=HttpResponseError,
        )
        found_volumes = []
        for volume in volumes:
            volume_name = volume.get("name")
            if volume_name == self.name:
                volume_region = volume.get("region")
                if volume_region:
                    volume_region_slug = volume_region.get("slug")
                    if volume_region_slug == self.region:
                        found_volumes.append(volume)
        return found_volumes

    def create_volume(self):
        try:
            body = {
                "name": self.name,
                "description": self.description,
                "size_gigabytes": self.size_gigabytes,
                "tags": self.tags,
                "snapshot_id": self.snapshot_id,
                "filesystem_type": self.filesystem_type,
                "region": self.region,
                "filesystem_label": self.filesystem_label,
            }
            volume = self.client.volumes.create(body=body)
            self.module.exit_json(
                changed=True,
                msg=f"Created volume {self.name} in {self.region}",
                volume=volume.get("volume"),
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(changed=False, msg=error.get("Message"), error=error)

    def delete_volume(self):
        try:
            resp = self.client.volumes.delete_by_name(
                name=self.name, region=self.region
            )
            if resp:
                message = resp.get("message")
                id = resp.get("id")
                if id == "not_found":
                    self.module.exit_json(changed=False, msg=message)
            self.module.exit_json(
                changed=True, msg=f"Deleted volume {self.name} in {self.region}"
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(changed=False, msg=error.get("Message"), error=error)

    def present(self):
        volumes = self.get_volumes_by_name_and_region()
        if len(volumes) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Volume {self.name} in {self.region} would be created",
                    volume=[],
                )
            else:
                self.create_volume()
        elif len(volumes) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Volume {self.name} ({volumes[0]['id']}) in {self.region} exists",
                volume=volumes[0],
            )
        elif len(volumes) > 1:
            volume_ids = ", ".join([str(volume["id"]) for volume in volumes])
            self.module.fail_json(
                changed=False,
                msg=f"There are currently {len(volumes)} volumes named {self.name} in {self.region}: {volume_ids}",
                droplet=[],
            )

    def absent(self):
        volumes = self.get_volumes_by_name_and_region()
        if len(volumes) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=False,
                    msg=f"Volume {self.name} in {self.region} not found",
                    volume=[],
                )
            else:
                self.module.fail_json(
                    changed=False,
                    msg=f"Volume {self.name} in {self.region} not found",
                    volume=[],
                )
        elif len(volumes) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Volume {self.name} ({volumes[0]['id']}) in {self.region} would be deleted",
                    volume=volumes[0],
                )
            else:
                self.delete_volume()
        elif len(volumes) > 1:
            volume_ids = ", ".join([str(volume["id"]) for volume in volumes])
            self.module.fail_json(
                changed=False,
                msg=f"There are currently {len(volumes)} volumes named {self.name} in {self.region}: {volume_ids}",
                volume=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        size_gigabytes=dict(type="int", required=False),
        tags=dict(type="list", elements="str", required=False),
        snapshot_id=dict(type="str", required=False),
        filesystem_type=dict(type="str", choices=["ext4", "xfs"], required=False),
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
        filesystem_label=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "present", ["size_gigabytes"]),
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

    Volume(module)


if __name__ == "__main__":
    main()
