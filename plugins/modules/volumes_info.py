#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: volumes_info

short_description: List all of the block storage volumes available on your account

version_added: 2.0.0

description:
  - List all of the block storage volumes available on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/volumes_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get volumes
  community.digitalocean.volumes_info:
    token: "{{ token }}"
"""


RETURN = r"""
volumes:
  description: Volumes.
  returned: success
  type: list
  elements: dict
  sample:
    - created_at: '2022-11-28T02:07:45Z'
      description: Block store for examples
      droplet_ids: []
      filesystem_label: example
      filesystem_type: ext4
      id: 72b1d6de-6ec1-11ed-8a0d-0a58ac1466a8
      name: example
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
      tags: []
msg:
  description: Volumes result information.
  returned: always
  type: str
  sample:
    - Current volumes
    - No volumes
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


class VolumesInformation:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            volumes = self.client.volumes.list()
            if volumes.get("volumes"):
                self.module.exit_json(
                    changed=False, msg="Current volumes", volumes=volumes.get("volumes")
                )
            self.module.exit_json(changed=False, msg="No volumes", volumes=[])
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(changed=False, msg=error.get("Message"), error=error)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
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

    VolumesInformation(module)


if __name__ == "__main__":
    main()
