#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cdn_endpoints_info

short_description: List all of the CDN endpoints available on your account

version_added: 2.0.0

description:
  - List all of the CDN endpoints available on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/cdn_list_endpoints).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get CDN endpoints
  community.digitalocean.cdn_endpoints_info:
    token: "{{ token }}"
"""


RETURN = r"""
endpoints:
  description: CDN endpoints.
  returned: always
  type: list
  sample:
    - id: 19f06b6a-3ace-4315-b086-499a0e521b76
      origin: static-images.nyc3.digitaloceanspaces.com
      endpoint: static-images.nyc3.cdn.digitaloceanspaces.com
      created_at: '2018-07-19T15:04:16Z'
      certificate_id: 892071a0-bb95-49bc-8021-3afd67a210bf
      custom_domain: static.example.com
      ttl: 3600
msg:
  description: CDN endpoints result information.
  returned: always
  type: str
  sample:
    - Current CDN endpoints
    - No CDN endpoints
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


class CDNEndpointsInformation:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            endpoints = self.client.cdn.list_endpoints()
            if endpoints.get("endpoints"):
                self.module.exit_json(
                    changed=False,
                    msg="Current CDN endpoints",
                    endpoints=endpoints.get("endpoints"),
                )
            self.module.exit_json(changed=False, msg="No CDN endpoints", endpoints=[])
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

    CDNEndpointsInformation(module)


if __name__ == "__main__":
    main()
