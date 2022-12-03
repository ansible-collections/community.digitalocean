#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: reserved_ips_info

short_description: List all reserved IPs on your account

version_added: 2.0.0

description:
  - List all reserved IPs on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/reservedIPs_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get reserved IPs
  community.digitalocean.reserved_ips_info:
    token: "{{ token }}"
"""


RETURN = r"""
reserved_ips:
  description: Reserved IPs.
  returned: always
  type: list
  elements: dict
  sample:
    - ip: 45.55.96.47
      droplet: null
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
          - ...
      locked: false
      project_id: 746c6152-2fa2-11ed-92d3-27aaa54e4988
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: User cannot enable a cdn for a space they do not own.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Reserved IPs result information.
  returned: always
  type: str
  sample:
    - Current Droplets
    - No Droplets
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.six.moves.urllib.parse import urlparse, parse_qs
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


class ReservedIPsInformation:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            reserved_ips = self.client.reserved_ips.list()
            if reserved_ips:
                self.module.exit_json(
                    changed=False, msg="Current reserved IPs", reserved_ips=reserved_ips
                )
            self.module.exit_json(changed=False, msg="No reserved IPs", reserved_ips=[])
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, reserved_ips=[]
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
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

    ReservedIPsInformation(module)


if __name__ == "__main__":
    main()
