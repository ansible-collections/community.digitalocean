#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2018, Ansible Project
# Copyright: (c) 2021, Mark Mercado <mamercad@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: digital_ocean_vpc_info
short_description: Gather information about DigitalOcean VPCs
version_added: 1.7.0
description:
  - This module can be used to gather information about DigitalOcean VPCs.
author: "Mark Mercado (@mamercad)"
extends_documentation_fragment:
- community.digitalocean.digital_ocean.documentation
"""


EXAMPLES = r"""
- name: Fetch all VPCs
  community.digitalocean.digital_ocean_vpc_info:
  register: my_vpcs
"""


RETURN = r"""
data:
  description: All DigitalOcean VPCs.
  returned: success
  type: dict
  sample:
    - created_at: '2021-02-06T17:57:22Z'
      default: true
      description: ''
      id: 0db3519b-9efc-414a-8868-8f2e6934688c
      ip_range: 10.116.0.0/20
      name: default-nyc1
      region: nyc1
      urn: do:vpc:0db3519b-9efc-414a-8868-8f2e6934688c
"""


import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.digitalocean.plugins.module_utils.digital_ocean import (
    DigitalOceanHelper,
)


class DOVPCInfo(object):
    def __init__(self, module):
        self.rest = DigitalOceanHelper(module)
        self.module = module
        # pop the oauth token so we don't include it in the POST data
        self.module.params.pop("oauth_token")

    def get(self):
        if self.module.check_mode:
            return self.module.exit_json(changed=False)
        base_url = "vpcs?"
        vpcs = self.rest.get_paginated_data(base_url=base_url, data_key_name="vpcs")
        self.module.exit_json(changed=False, data=vpcs)


def run(module):
    vpcs = DOVPCInfo(module)
    vpcs.get()


def main():
    argument_spec = DigitalOceanHelper.digital_ocean_argument_spec()
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    run(module)


if __name__ == "__main__":
    main()
