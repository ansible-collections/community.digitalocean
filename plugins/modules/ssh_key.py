#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ssh_key

short_description: Create or delete SSH keys

version_added: 2.0.0

description:
  - Create or delete SSH keys.
  - View the create API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/SSH-Keys).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  public_key:
    description:
      - The entire public key string that was uploaded.
      - |
        Embedded into the root user's authorized_keys file if you include this key during
        Droplet creation.
    type: str
    required: true
  name:
    description:
      - |
        A human-readable display name for this key, used to easily identify the SSH keys when
        they are displayed.
    type: str
    required: true

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create SSH key
  community.digitalocean.ssh_key:
    token: "{{ token }}"
    state: present
    public_key: >-
      ssh-rsa AEXAMPLEaC1yc2EAAAADAQABAAAAQQDDHr/jh2Jy4yALcK4JyWbVkPRaWmhck3IgCoeOO3z1e2dBowLh64QAM+Qb72pxekALga2oi4GvT+TlWNhzPH4V example
    name: "My SSH Public Key"
"""


RETURN = r"""
ssh_key:
  description: SSH key information.
  returned: always
  type: dict
  sample:
    id: 512189
    fingerprint: 3b:16:bf:e4:8b:00:8b:b8:59:8c:a9:d3:f0:19:45:fa
    public_key: >-
      ssh-rsa AEXAMPLEaC1yc2EAAAADAQABAAAAQQDDHr/jh2Jy4yALcK4JyWbVkPRaWmhck3IgCoeOO3z1e2dBowLh64QAM+Qb72pxekALga2oi4GvT+TlWNhzPH4V example
    name: My SSH Public Key
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Droplet result information.
  returned: always
  type: str
  sample:
    - Created SSH key My SSH Public Key (3b:16:bf:e4:8b:00:8b:b8:59:8c:a9:d3:f0:19:45:fa)
    - Deleted SSH key My SSH Public Key (3b:16:bf:e4:8b:00:8b:b8:59:8c:a9:d3:f0:19:45:fa)
    - SSH key My SSH Public Key would be created
    - SSH key My SSH Public Key (3b:16:bf:e4:8b:00:8b:b8:59:8c:a9:d3:f0:19:45:fa) exists
    - SSH key My SSH Public Key does not exist
    - SSH key My SSH Public Key (3b:16:bf:e4:8b:00:8b:b8:59:8c:a9:d3:f0:19:45:fa) would be deleted
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


class SSHKey:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.public_key = module.params.get("public_key")
        self.name = module.params.get("name")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_ssh_keys(self):
        try:
            ssh_keys = self.client.ssh_keys.list()["ssh_keys"]
            found_ssh_keys = []
            for ssh_key in ssh_keys:
                if self.name == ssh_key["name"]:
                    found_ssh_keys.append(ssh_key)
            return found_ssh_keys
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                ssh_key=[],
            )

    def create_ssh_key(self):
        try:
            body = {
                "public_key": self.public_key,
                "name": self.name,
            }
            ssh_key = self.client.ssh_keys.create(body=body)["ssh_key"]

            self.module.exit_json(
                changed=True,
                msg=f"Created SSH key {self.name} ({ssh_key['fingerprint']})",
                ssh_key=ssh_key,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, ssh_key=[]
            )

    def delete_ssh_key(self, ssh_key):
        try:
            self.client.ssh_keys.delete(ssh_key_identifier=ssh_key["fingerprint"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted SSH key {self.name} ({ssh_key['fingerprint']})",
                ssh_key=ssh_key,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                ssh_key=[],
            )

    def present(self):
        ssh_keys = self.get_ssh_keys()
        if len(ssh_keys) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"SSH key {self.name} would be created",
                    ssh_key=[],
                )
            else:
                self.create_ssh_key()
        elif len(ssh_keys) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"SSH key {self.name} ({ssh_keys[0]['fingerprint']}) exists",
                ssh_key=ssh_keys[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(ssh_keys)} named {self.name}",
                firewall=[],
            )

    def absent(self):
        ssh_keys = self.get_ssh_keys()
        if len(ssh_keys) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"SSH key {self.name} does not exist",
                firewall=[],
            )
        elif len(ssh_keys) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"SSH key {self.name} ({ssh_keys[0]['fingerprint']}) would be deleted",
                    ssh_key=ssh_keys[0],
                )
            else:
                self.delete_ssh_key(ssh_key=ssh_keys[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(ssh_keys)} SSH keys named {self.name}",
                ssh_keys=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        public_key=dict(type="str", required=True),
        name=dict(type="str", required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

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

    SSHKey(module)


if __name__ == "__main__":
    main()
