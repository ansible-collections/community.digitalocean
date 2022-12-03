#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: regions_info

short_description: List all of the regions that are available

version_added: 2.0.0

description:
  - List all of the regions that are available.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/regions_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get regions
  community.digitalocean.regions_info:
    token: "{{ token }}"
"""


RETURN = r"""
regions:
  description: Regions.
  returned: success
  type: list
  elements: dict
  sample:
    - available: true
      features:
        - backups
        - ipv6
        - metadata
        - install_agent
        - storage
        - image_transfer
      name: New York 1
      sizes:
        - s-1vcpu-512mb-10gb
        - s-1vcpu-1gb
        - s-1vcpu-1gb-amd
        - s-1vcpu-1gb-intel
        - s-1vcpu-2gb
        - ...
      slug: nyc1
    - ...
msg:
  description: Regions result information.
  returned: always
  type: str
  sample:
    - Current regions
    - No regions
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


class RegionsInformation:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        if self.state == "present":
            self.present()

    def present(self):
        regions = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.regions,
            meth="list",
            key="regions",
            exc=HttpResponseError,
        )
        if regions:
            self.module.exit_json(
                changed=False,
                msg="Current regions",
                regions=regions,
            )
        self.module.exit_json(changed=False, msg="No regions", regions=[])


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

    RegionsInformation(module)


if __name__ == "__main__":
    main()
