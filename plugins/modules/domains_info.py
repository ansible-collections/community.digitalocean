#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: domains_info

short_description: Retrieve a list of all of the domains in your account

version_added: 2.0.0

description:
  - Retrieve a list of all of the domains in your account.
  - View the API documentation at (https://docs.digitalocean.com/reference/api/api-reference/#operation/domains_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get domains
  community.digitalocean.domains_info:
    token: "{{ token }}"
"""


RETURN = r"""
domains:
  description: Domains.
  returned: success
  type: list
  elements: dict
  sample:
    - name: example.com
      ttl: 1800
      zone_file: |-
        $ORIGIN example.com.
        $TTL 1800
        example.com. IN SOA ns1.digitalocean.com. hostmaster.example.com 1657981824 10800 3600 604800 1800
        test.example.com. 300 IN A 1.2.3.4
        example.com. 1800 IN NS ns1.digitalocean.com.
        example.com. 1800 IN NS ns2.digitalocean.com.
        example.com. 1800 IN NS ns3.digitalocean.com.
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


class DomainsInformation:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            domains = self.client.domains.list()
            if domains.get("domains"):
                self.module.exit_json(
                    changed=False, msg="Current domains", domains=domains.get("domains")
                )
            self.module.exit_json(changed=False, msg="No domains", domains=[])
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(changed=False, msg=error.get("Message"), error=error)

        # NOTE: Our API doesn't paginate (have per_page) for domains list:
        #       https://docs.digitalocean.com/reference/api/api-reference/#operation/domains_list
        #
        # domains = DigitalOceanFunctions.get_paginated(
        #     module=self.module,
        #     obj=self.client.domains,
        #     meth="list",
        #     key="domains",
        #     exc=HttpResponseError,
        # )
        # if domains:
        #     self.module.exit_json(
        #         changed=False,
        #         msg="Current domains",
        #         domains=domains,
        #     )
        # self.module.exit_json(changed=False, msg="No domains", domains=[])


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

    DomainsInformation(module)


if __name__ == "__main__":
    main()
