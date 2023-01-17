#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: monitoring_alert_policies_info

short_description: Returns all alert policies that are configured for the given account

version_added: 2.0.0

description:
  - Returns all alert policies that are configured for the given account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/monitoring_list_alertPolicy).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get monitoring alert policies
  community.digitalocean.monitoring_alert_policies_info:
    token: "{{ token }}"
"""


RETURN = r"""
policies:
  description: Monitoring alert policies.
  returned: always
  type: list
  elements: dict
  sample:
    - alerts:
        email:
          - bob@example.com
        slack:
          - channel: Production Alerts
            url: https://hooks.slack.com/services/T1234567/AAAAAAAA/ZZZZZZ"
      compare: GreaterThan
      description: CPU Alert
      enabled: true
      entities:
        - 192018292
      tags:
        - production_droplets
      type: v1/insights/droplet/cpu
      uuid: 78b3da62-27e5-49ba-ac70-5db0b5935c64
      value: 80
      window: 5m
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Monitoring alert policies result information.
  returned: always
  type: str
  sample:
    - Current alert polices
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


class MonitoringAlertPoliciesInformation:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")

        if self.state == "present":
            self.present()

    def present(self):
        policies = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.monitoring,
            meth="list_alert_policy",
            key="policies",
            exc=HttpResponseError,
        )
        self.module.exit_json(
            changed=False,
            msg="Current alert policies",
            policies=policies,
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

    MonitoringAlertPoliciesInformation(module)


if __name__ == "__main__":
    main()
