#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: billing_history_info

short_description: Retrieve a list of all billing history entries

version_added: 2.0.0

description:
  - Retrieve a list of all billing history entries.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/billingHistory_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get billing history information
  community.digitalocean.billing_history_info:
    token: "{{ token }}"
"""


RETURN = r"""
billing_history:
  description: Billing history information.
  returned: success
  type: list
  sample:
    - description: Invoice for May 2018
      amount: 12.34
      invoice_id: 123
      invoice_uuid: example-uuid
      date: '2018-06-01T08:44:38Z'
      type: Invoice
msg:
  description: Billing history result information.
  returned: always
  type: str
  sample:
    - Current billing history
    - No billing history
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


class BillingHistoryInformation:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        if self.state == "present":
            self.present()

    def present(self):
        billing_history = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.cdn,
            meth="list",
            key="billing_history",
            exc=HttpResponseError,
        )
        if billing_history:
            self.module.exit_json(
                changed=False,
                msg="Current billing history",
                billing_history=billing_history,
            )
        self.module.exit_json(changed=False, msg="No billing history", endpoints=[])


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

    BillingHistoryInformation(module)


if __name__ == "__main__":
    main()
