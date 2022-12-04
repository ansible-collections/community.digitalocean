#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: droplets_info

short_description: List all Droplets in your account

version_added: 2.0.0

description:
  - List all Droplets in your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/droplets_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  tag_name:
    description:
      - Used to filter Droplets by a specific tag.
      - Cannot be combined with C(name).
    type: str
    required: false
  name:
    description:
      - Used to filter list response by Droplet name returning only exact matches
      - It is case-insensitive and can not be combined with C(tag_name).
    type: str
    required: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get Droplets
  community.digitalocean.droplets_info:
    token: "{{ token }}"
"""


RETURN = r"""
droplets:
  description: Droplets.
  returned: always
  type: list
  elements: dict
  sample:
    - backup_ids: []
      created_at: '2022-11-30T03:15:17Z'
      disk: 25
      features:
        - droplet_agent
        - private_networking
      id: 328912829
      image:
        created_at: '2022-07-18T19:40:04Z'
        description: Ubuntu 20.04 x86
        distribution: Ubuntu
        id: 112929454
        min_disk_size: 7
        name: 20.04 (LTS) x64
        public: true
        regions:
        - nyc3
        - ...
        size_gigabytes: 0.63
        slug: ubuntu-20-04-x64
        status: available
        tags: []
        type: base
      kernel: null
      locked: false
      memory: 8192
      name: test-droplet-1
      networks:
        v4:
        - gateway: 10.108.0.1
          ip_address: 10.108.0.2
          netmask: 255.255.240.0
          type: private
        - gateway: 159.65.240.1
          ip_address: 159.65.142.211
          netmask: 255.255.240.0
          type: public
        v6: []
      next_backup_window: null
      region:
        available: true
        features:
          - backups
          - ipv6
          - metadata
          - install_agent
          - storage
          - image_transfer
        name: New York 3
        sizes:
          - s-1vcpu-1gb
          - ...
        slug: nyc3
      size:
        available: true
        description: General Purpose
        disk: 25
        memory: 8192
        price_hourly: 0.09375
        price_monthly: 63.0
        regions:
          - ams3
          - ...
        slug: g-2vcpu-8gb
        transfer: 4.0
        vcpus: 2
      size_slug: g-2vcpu-8gb
      snapshot_ids: []
      status: active
      tags: []
      vcpus: 2
      volume_ids: []
      vpc_uuid: 30f86d25-414e-434f-852d-993ed8d6815e
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Droplets result information.
  returned: always
  type: str
  sample:
    - Current Droplets
    - No Droplets
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.six.moves.urllib.parse import urlparse, parse_qs
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


class CertificatesInformation:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.tag_name = module.params.get("tag_name")
        self.name = module.params.get("name")
        self.params = None
        if self.tag_name:
            self.params = dict(tag_name=self.tag_name)
        elif self.name:
            self.params = dict(name=self.name)
        if self.state == "present":
            self.present()

    def present(self):
        droplets = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.droplets,
            meth="list",
            key="droplets",
            params=self.params,
            exc=HttpResponseError,
        )
        if droplets:
            self.module.exit_json(
                changed=False,
                msg="Current Droplets",
                droplets=droplets,
            )
        self.module.exit_json(changed=False, msg="No Droplets", droplets=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        tag_name=dict(type="str", required=False),
        name=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[("tag_name", "name")],
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

    CertificatesInformation(module)


if __name__ == "__main__":
    main()
