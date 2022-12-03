#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: firewalls_info

short_description: List all firewalls on your account

version_added: 2.0.0

description:
  - List all firewall on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/firewalls_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get Droplets
  community.digitalocean.droplets_info:
    token: "{{ token }}"
"""


RETURN = r"""
firewalls:
  description: Firewalls.
  returned: always
  type: list
  elements: dict
  sample:
    - id: fb6045f1-cf1d-4ca3-bfac-18832663025b
      name: firewall
      status: succeeded
      inbound_rules:
        - protocol: tcp
          ports: '80'
          sources:
            load_balancer_uids:
              - 4de7ac8b-495b-4884-9a69-1050c6793cd6
        - protocol: tcp
          ports: '22'
          sources:
            tags:
              - gateway
            addresses:
              - 18.0.0.0/8
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: User cannot enable a cdn for a space they do not own.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Droplets result information.
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


class FirewallsInformation:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        if self.state == "present":
            self.present()

    def present(self):
        firewalls = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.firewalls,
            meth="list",
            key="firewalls",
            exc=HttpResponseError,
        )
        if firewalls:
            self.module.exit_json(
                changed=False,
                msg="Current firewalls",
                firewalls=firewalls,
            )
        self.module.exit_json(changed=False, msg="No firewalls", firewalls=[])


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

    FirewallsInformation(module)


if __name__ == "__main__":
    main()
