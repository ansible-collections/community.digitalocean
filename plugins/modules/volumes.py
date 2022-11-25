#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: volumes

short_description: Create or delete volumes

version_added: 2.0.0

description:
  - This module creates or deletes volumes.

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - A human-readable name for the block storage volume.
      - Must be lowercase and be composed only of numbers, letters and "-", up to a limit of 64 characters.
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
      - Labels for ext4 type filesystems may contain 16 characters while labels for xfs type filesystems are limited to 12 characters.
      - May only be used in conjunction with filesystem_type.
    type: str
    required: false

extends_documentation_fragment:
  - community.digitalocean.common_options.documentation
"""


EXAMPLES = r"""
- name: Create DigitalOcean volume
  community.digitalocean.volumes:
    token: "{{ token }}"
    state: present
    name: test-vol-delete-1
    region: nyc3
    size_gigabytes: 1
"""


RETURN = r"""
volume:
  description: DigitalOcean volume information.
  returned: success
  type: dict
  sample:
    created_at: '2022-11-24T19:23:01Z'
    description: ''
    droplet_ids: null
    filesystem_label: ''
    filesystem_type: ''
    id: 698d7221-6c2d-11ed-93f9-0a58ac14790c
    name: test-vol-delete-1
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
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.digitalocean.plugins.module_utils.common_options import (
    DigitalOceanOptions,
)
from ansible_collections.community.digitalocean.plugins.module_utils.common_functions import (
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


def find_volume(module, client, volume_name, region):
    page = 1
    paginated = True
    while paginated:
        try:
            resp = client.volumes.list(per_page=10, page=page)
            for volume in resp.get("volumes"):
                if volume.get("name") == volume_name:
                    volume_region = volume.get("region")
                    if volume_region:
                        volume_region_slug = volume_region.get("slug")
                        if volume_region_slug == region:
                            return volume
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            module.fail_json(changed=False, msg=error.get("Message"), error=error)

        next_page = DigitalOceanFunctions.get_next_page(links=resp.get("links"))
        if next_page:
            return next_page

        paginated = False

    return None


def delete_volume(module, client, volume_id):
    try:
        client.volumes.delete(volume_id=volume_id)
    except HttpResponseError as err:
        error = {
            "Message": err.error.message,
            "Status Code": err.status_code,
            "Reason": err.reason,
        }
        module.fail_json(changed=False, msg=error.get("Message"), error=error)


def core(module):
    client = Client(token=module.params.get("token"))
    volume_name = module.params.get("name")
    region = module.params.get("region")

    if module.params.get("state") == "present":
        try:
            body = {
                "name": module.params.get("name"),
                "region": module.params.get("region"),
                "size_gigabytes": int(module.params.get("size_gigabytes")),
            }
            volume = client.volumes.create(body=body)
            module.exit_json(changed=True, volume=volume.get("volume"))
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            module.fail_json(changed=False, msg=error.get("Message"), error=error)

    elif module.params.get("state") == "absent":
        volume = find_volume(
            module=module,
            client=client,
            volume_name=module.params.get("name"),
            region=module.params.get("region"),
        )

        if not volume:
            module.exit_json(
                changed=False, msg=f"Volume {volume_name} in {region} not found"
            )
        else:
            volume_id = volume.get("id")
            delete_volume(module=module, client=client, volume_id=volume_id)
            module.exit_json(
                changed=True,
                msg=f"Volume {volume_name} in {region} deleted",
                volume=volume,
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

    core(module)


if __name__ == "__main__":
    main()
