#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: snapshot

short_description: Delete snapshots

version_added: 2.0.0

description:
  - Delete snapshots.
  - View the delete API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/snapshots_delete).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  snapshot_id:
    description:
      - Either the ID of an existing snapshot.
      - This will be an integer for a Droplet snapshot or a string for a volume snapshot.
    type: str
    required: false
  snapshot_name:
    description:
      - The name of an existing snapshot.
      - The module will fail if there is more than one by the same name, use C(snapshot)id).
    type: str
    required: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Delete Droplet snapshot
  community.digitalocean.snapshot:
    token: "{{ token }}"
    state: absent
    snapshot_id: 11223344

- name: Delete volume snapshot
  community.digitalocean.snapshot:
    token: "{{ token }}"
    state: absent
    snapshot_id: fbe805e8-866b-11e6-96bf-000f53315a41
"""


RETURN = r"""
snapshot:
  description: Snapshot information.
  returned: always
  type: dict
  elements: dict
  sample:
    id: '6372321'
    name: web-01-1595954862243
    created_at: '2020-07-28T16:47:44Z'
    regions: []
    resource_id: '200776916'
    resource_type: droplet
    min_disk_size: 25
    size_gigabytes: 2.34
    tags: []
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
    - Deleted snapshot 125349720
    - Deleted snapshot test-snapshot-1
    - Snapshot 125349720 would be deleted
    - Snapshot test-snapshot-1 would be deleted
    - Snapshot 125349720 not found
    - Snapshot test-snapshot-1 not found
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


class Snapshot:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.snapshot_id = module.params.get("snapshot_id")
        self.snapshot_name = module.params.get("snapshot_name")

        if self.state == "absent":
            self.absent()

    def delete_snapshot(self, snapshot):
        try:
            self.client.snapshots.delete(snapshot_id=snapshot["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted snapshot {snapshot['id']}",
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

    def get_snapshot_by_id(self, snapshot_id):
        snapshots = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.snapshots,
            meth="list",
            key="snapshots",
            params=None,
            exc=HttpResponseError,
        )
        for snapshot in snapshots:
            if snapshot["id"] == snapshot_id:
                return snapshot
        return None

    def get_snapshot_by_name(self, snapshot_name):
        snapshots = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.snapshots,
            meth="list",
            key="snapshots",
            params=None,
            exc=HttpResponseError,
        )
        found_snapshots = []
        for snapshot in snapshots:
            if snapshot["name"] == snapshot_name:
                found_snapshots.append(snapshot)

        if len(found_snapshots) == 0:
            return None

        elif len(found_snapshots) == 1:
            return found_snapshots[0]

        self.module.fail_json(
            changed=True,
            msg=f"More than one ({len(found_snapshots)}) found named {snapshot_name})",
            snapshot=[],
        )

    def absent(self):
        if self.snapshot_id:
            snapshot = self.get_snapshot_by_id(snapshot_id=self.snapshot_id)

            if not snapshot:
                self.module.exit_json(
                    changed=False,
                    msg=f"Snapshot {self.snapshot_id} not found",
                    snapshot=[],
                )

            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Snapshot {self.snapshot_id} would be deleted",
                    snapshot=snapshot,
                )

            self.delete_snapshot(snapshot=snapshot)

        elif self.snapshot_name:
            snapshot = self.get_snapshot_by_name(snapshot_name=self.snapshot_name)

            if not snapshot:
                self.module.exit_json(
                    changed=False,
                    msg=f"Snapshot {self.snapshot_name} not found",
                    snapshot=[],
                )

            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Snapshot {self.snapshot_name} would be deleted",
                    snapshot=snapshot,
                )

            self.delete_snapshot(snapshot=snapshot)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        snapshot_id=dict(type="str", required=False),
        snapshot_name=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[("snapshot_id", "snapshot_name")],
        mutually_exclusive=[("snapshot_id", "snapshot_name")],
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

    Snapshot(module)


if __name__ == "__main__":
    main()
