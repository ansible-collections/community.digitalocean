#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: volume_snapshot

short_description: Create or delete volume snapshots

version_added: 2.0.0

description:
  - Create or delete volume snapshots.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Snapshots).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  volume_id:
    description:
      - The ID of the block storage volume.
    type: str
    required: true
  name:
    description:
      - A human-readable name for the volume snapshot.
    type: str
    required: true
  tags:
    description:
      - A flat array of tag names as strings to be applied to the resource.
      - Tag names may be for either existing or new tags.
    type: list
    elements: str
    required: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create a volume snapshot
  community.digitalocean.volume_snapshot:
    token: "{{ token }}"
    state: present
    volume_id: 7724db7c-e098-11e5-b522-000f53304e51
    name: big-data-snapshot1475261774
    tags:
      - aninterestingtag
"""


RETURN = r"""
snapshot:
  description: Volume snapshot information.
  returned: always
  type: dict
  sample:
    id: 8fa70202-873f-11e6-8b68-000f533176b1
    name: big-data-snapshot1475261774
    regions:
      - nyc1
    created_at: '2020-09-30T18:56:14Z'
    resource_id: 82a48a18-873f-11e6-96bf-000f53315a41
    resource_type: volume
    min_disk_size: 10
    size_gigabytes: 10
    tags:
      - aninterestingtag
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
    - Created volume snapshot big-data-snapshot1475261774 (8fa70202-873f-11e6-8b68-000f533176b1) of volume 82a48a18-873f-11e6-96bf-000f53315a41
    - Deleted volume snapshot big-data-snapshot1475261774 (8fa70202-873f-11e6-8b68-000f533176b1) of volume 82a48a18-873f-11e6-96bf-000f53315a41
    - Volume snapshot big-data-snapshot1475261774 of volume 82a48a18-873f-11e6-96bf-000f53315a41
    - Volume snapshot big-data-snapshot1475261774 (8fa70202-873f-11e6-8b68-000f533176b1) of volume 82a48a18-873f-11e6-96bf-000f53315a41 exists
    - Volume snapshot big-data-snapshot1475261774 does not exist
    - Volume snapshot big-data-snapshot1475261774 (8fa70202-873f-11e6-8b68-000f533176b1) of volume 82a48a18-873f-11e6-96bf-000f53315a41 would be deleted
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


class VolumeSnapshot:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.volume_id = module.params.get("volume_id")
        self.name = module.params.get("name")
        self.tags = module.params.get("tags")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_volume_snapshots(self):
        volume_snapshots = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.volume_snapshots,
            meth="list",
            key="snapshots",
            exc=HttpResponseError,
            volume_id=self.volume_id,
        )
        found_volume_snapshots = []
        if volume_snapshots:
            for volume_snapshot in volume_snapshots:
                if self.name == volume_snapshot["name"]:
                    found_volume_snapshots.append(volume_snapshot)
        return found_volume_snapshots

    def create_volume_snapshot(self):
        try:
            body = {
                "name": self.name,
                "tags": self.tags,
            }
            snapshot = self.client.volume_snapshots.create(
                volume_id=self.volume_id, body=body
            )["snapshot"]
            self.module.exit_json(
                changed=True,
                msg=f"Created volume snapshot {self.name} ({snapshot['id']}) of volume {self.volume_id}",
                snapshot=snapshot,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, snapshot=[]
            )

    def delete_volume_snapshot(self, snapshot):
        try:
            self.client.volume_snapshots.delete_by_id(snapshot_id=snapshot["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted volume snapshot {self.name} ({snapshot['id']}) of volume {self.volume_id}",
                snapshot=snapshot,
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
                snapshot=[],
            )

    def present(self):
        volume_snapshots = self.get_volume_snapshots()
        if len(volume_snapshots) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Volume snapshot {self.name} of volume {self.volume_id} would be created",
                    snapshot=[],
                )
            else:
                self.create_volume_snapshot()
        elif len(volume_snapshots) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Volume snapshot {self.name} ({volume_snapshots[0]['id']}) of volume {self.volume_id} exists",
                snapshot=volume_snapshots[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(volume_snapshots)} volume snapshots named {self.name} of volume {self.volume_id}",
                snapshot=[],
            )

    def absent(self):
        volume_snapshots = self.get_volume_snapshots()
        if len(volume_snapshots) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"Volume snapshot {self.name} of volume {self.volume_id} does not exist",
                snapshot=[],
            )
        elif len(volume_snapshots) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Volume snapshot {self.name} ({volume_snapshots[0]['id']}) of volume {self.volume_id} would be deleted",
                    snapshot=volume_snapshots[0],
                )
            else:
                self.delete_volume_snapshot(snapshot=volume_snapshots[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(volume_snapshots)} volume snapshots named {self.name} of volume {self.volume_id}",
                snapshot=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        volume_id=dict(type="str", required=True),
        name=dict(type="str", required=True),
        tags=dict(type="list", elements="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        # required_if=[
        #     ("state", "present", ("purpose",)),
        # ],
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

    VolumeSnapshot(module)


if __name__ == "__main__":
    main()
