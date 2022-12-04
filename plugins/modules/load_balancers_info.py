#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: load_balancers_info

short_description: Retrieve a list of all of the load balancers in your account

version_added: 2.0.0

description:
  - Retrieve a list of all of the load balancers in your account.
  - View the API documentation at (https://docs.digitalocean.com/reference/api/api-reference/#operation/loadBalancers_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get load balancers
  community.digitalocean.load_balancers_info:
    token: "{{ token }}"
"""


RETURN = r"""
load_balancers:
  description: Load balancers.
  returned: always
  type: list
  elements: dict
  sample: []
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Domain result information.
  returned: always
  type: str
  sample:
    - Current domains
    - No domains
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


class LoadBalancersInformation:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        if self.state == "present":
            self.present()

    def present(self):
        load_balancers = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.load_balancers,
            meth="list",
            key="load_balancers",
            exc=HttpResponseError,
        )
        if load_balancers:
            self.module.exit_json(
                changed=False,
                msg="Current load balancers",
                load_balancers=load_balancers,
            )
        self.module.exit_json(
            changed=False, msg="No load balancers", load_balancers=load_balancers
        )


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

    LoadBalancersInformation(module)


if __name__ == "__main__":
    main()
