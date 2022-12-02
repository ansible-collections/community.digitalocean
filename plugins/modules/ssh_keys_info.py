#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ssh_keys_info

short_description: List all of the keys in your account

version_added: 2.0.0

description:
  - List all of the keys in your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/sshKeys_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get SSH keys
  community.digitalocean.ssh_keys_info:
    token: "{{ token }}"
"""


RETURN = r"""
ssh_keys:
  description: SSH keys.
  returned: success
  type: list
  elements: dict
  sample:
    - id: 289794
      fingerprint: '3b:16:e4:bf:8b:00:8b:b8:59:8c:a9:d3:f0:19:fa:45'
      public_key: 'ssh-rsa ANOTHEREXAMPLEaC1yc2EAAAADAQABAAAAQ...owLh64b72pxekALga2oi4GvT+TlWNhzPH4V anotherexample'
      name: Other Public Key
msg:
  description: SSH keys result information.
  returned: always
  type: str
  sample:
    - Current SSH keys
    - No SSH keys
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


class SSHKeysInformation:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            ssh_keys = self.client.ssh_keys.list()
            if ssh_keys.get("ssh_keys"):
                self.module.exit_json(
                    changed=False,
                    msg="Current SSH keys",
                    ssh_keys=ssh_keys.get("ssh_keys"),
                )
            self.module.exit_json(changed=False, msg="No SSH keys", ssh_keys=[])
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

    SSHKeysInformation(module)


if __name__ == "__main__":
    main()
