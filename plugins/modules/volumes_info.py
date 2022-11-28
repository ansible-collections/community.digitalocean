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
- name: Get DigitalOcean volumes
  community.digitalocean.volumes_info:
    token: "{{ token }}"
"""


RETURN = r"""
volumes:
  description: DigitalOcean volumes.
  returned: success
  type: list
  elements: dict
  sample:
    - created_at: '2022-11-28T02:07:45Z'
      description: ''
      droplet_ids: []
      filesystem_label: ''
      filesystem_type: ''
      id: 72b1d6de-6ec1-11ed-8a0d-0a58ac1466a8
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
      tags: []
msg:
  description: Volumes result information.
  returned: failed
  type: str
  sample: Volumes not found
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


def core(module):
    client = Client(token=module.params.get("token"))
    try:
        volumes = client.volumes.list()
        if volumes:
            module.exit_json(changed=False, volumes=volumes)
        module.fail_json(changed=False, msg="Volumes not found")
    except HttpResponseError as err:
        error = {
            "Message": err.error.message,
            "Status Code": err.status_code,
            "Reason": err.reason,
        }
        module.fail_json(changed=False, msg=error.get("Message"), error=error)


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

    core(module)


if __name__ == "__main__":
    main()
