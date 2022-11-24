#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sizes_info

short_description: Get current Droplet sizes

version_added: 2.0.0

description:
  - This module gets the current Droplet sizes.

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - community.digitalocean.token.documentation
"""


EXAMPLES = r"""
- name: Get DigitalOcean Droplet sizes
  community.digitalocean.sizes_info:
    token: "{{ token }}"
"""


RETURN = r"""
sizes:
  description: DigitalOcean Droplet sizes information.
  returned: success
  type: dict
  sample:
    links:
      pages:
        last: https://api.digitalocean.com/v2/sizes?page=4&per_page=20
        next: https://api.digitalocean.com/v2/sizes?page=2&per_page=20
    meta:
      total: 73
    sizes:
    - available: true
      description: Basic
      disk: 10
      memory: 512
      price_hourly: 0.00595
      price_monthly: 4.0
      regions:
        - ams3
        - fra1
        - nyc1
        - sfo3
        - sgp1
        - syd1
      slug: s-1vcpu-512mb-10gb
      transfer: 0.5
      vcpus: 1
    - ...
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.digitalocean.plugins.module_utils.common_options import (
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
        sizes = client.sizes.list()
        module.exit_json(changed=False, sizes=sizes)
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
