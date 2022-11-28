#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: one_clicks_info

short_description: List all available 1-Click applications

version_added: 2.0.0

description:
  - List all available 1-Click applications.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/oneClicks_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  type:
    description:
      - Limit by type of 1-Click application.
    type: str
    required: false
    choices: [ droplet, kubernetes ]

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get DigitalOcean 1-Click applications
  community.digitalocean.one_click_info:
    token: "{{ token }}"

- name: Get DigitalOcean Droplet 1-Click applications
  community.digitalocean.one_click_info:
    token: "{{ token }}"
    type: droplet

- name: Get DigitalOcean Kubernetes 1-Click applications
  community.digitalocean.one_click_info:
    token: "{{ token }}"
    type: kubernetes
"""


RETURN = r"""
account:
  description: DigitalOcean account information.
  returned: success
  type: list
  elements: dict
  sample:
    - slug: cpanel-cpanelwhm-7-9
      type: droplet
    - slug: npool
      type: droplet
    - slug: optimajet-workflowserver-18-04
      type: droplet
    - ...
    - slug: netdata
      type: kubernetes
    - slug: okteto
      type: kubernetes
    - slug: fyipe
      type: kubernetes
msg:
  description: 1-Click applications result information.
  returned: failed
  type: str
  sample: 1-Click applications not found
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
        one_clicks_info = client.one_clicks.list()
        one_clicks = one_clicks_info.get("1_clicks")
        if one_clicks:
            click_type = module.params.get("type")
            if click_type:
                filtered_clicks = list(filter(lambda val: val.get("type") == click_type, one_clicks))
                module.exit_json(changed=False, one_clicks=filtered_clicks)
            module.exit_json(changed=False, one_clicks=one_clicks)
        module.fail_json(changed=False, msg="1-Click applications not found")
    except HttpResponseError as err:
        error = {
            "Message": err.error.message,
            "Status Code": err.status_code,
            "Reason": err.reason,
        }
        module.fail_json(changed=False, msg=error.get("Message"), error=error)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        type=dict(type="str", choices=["droplet", "kubernetes"], required=False),
    )
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
