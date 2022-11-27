#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ssh_keys_info

short_description: Get SSH keys

version_added: 2.0.0

description:
  - This module gets SSH keys.

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get DigitalOcean SSH keys
  community.digitalocean.ssh_keys_info:
    token: "{{ token }}"
"""


RETURN = r"""
ssh_keys:
  description: DigitalOcean SSH keys.
  returned: success
  type: list
  elements: dict
  sample:
    - fingerprint: 40:24:52:5c:e1:81:f7:ff:76:70:14:b8:81:f9:ee:f1
      id: 36702776
      name: SSH key name
      public_key: |-
        ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC...x2Ck1mq67aVba+B0wxSGN+j7Fi27quUw== SSH key comment
msg:
  description: Informational message
  returned: failed
  type: str
  sample: Retrieved no SSH keys
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
        ssh_keys_list = client.ssh_keys.list()
        ssh_keys = ssh_keys_list.get("ssh_keys")
        if ssh_keys:
            module.exit_json(changed=False, ssh_keys=ssh_keys)
        module.fail_json(changed=False, msg="Retrieved no SSH keys")
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
