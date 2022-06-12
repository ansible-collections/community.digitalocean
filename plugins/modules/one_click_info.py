#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright: (c) Ansible Project 2022
# Copyright: (c) DigitalOcean 2022
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
from random import choices

__metaclass__ = type


DOCUMENTATION = r"""
---
module: one_click_info
short_description: List all available 1-Click Applications
description:
  - List all available 1-Click Applications
  - 1-Click applications are pre-built Droplet images or Kubernetes apps with software, features, and configuration details already set up for you
  - They can be found in the in the DigitalOcean Marketplace U(https://docs.digitalocean.com/products/marketplace/)
author: Mark Mercado (@mamercad)
extends_documentation_fragment:
  - community.digitalocean.base_args.documentation
"""


EXAMPLES = r"""
- name: Gather information about user account
  community.digitalocean.digital_ocean_account_info:
    oauth_token: "{{ oauth_token }}"
"""


RETURN = r"""
data:
    description: DigitalOcean account information
    returned: success
    type: dict
    sample: {
        "droplet_limit": 10,
        "email": "testuser1@gmail.com",
        "email_verified": true,
        "floating_ip_limit": 3,
        "status": "active",
        "status_message": "",
        "uuid": "aaaaaaaaaaaaaa"
    }
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.digitalocean.plugins.module_utils.base_module import (
    DigitalOceanBaseModule,
)


class DOOneClick(DigitalOceanBaseModule):
    def __init__(self, module):
        super().__init__(module)
        self.module = module
        self.type = self.module.params.get("type")

    def get(self):
        if self.type:
            response = self.api.get("1-clicks?type={0}".format(self.type))
        else:
            response = self.api.get("1-clicks")
        status_code = response.status_code

        if status_code == 200:
            one_clicks = response.json.get("1_clicks")
            if not one_clicks:
                self.module.fail_json(
                    changed=False,
                    msg="Failed to get any 1-Click applications",
                    status_code=status_code,
                )
            else:
                self.module.exit_json(
                    changed=False,
                    msg="All available 1-Click applications",
                    data=one_clicks,
                    status_code=status_code,
                )
        elif status_code == 401:
            self.module.fail_json(
                changed=False, msg="Unauthorized", status_code=status_code
            )
        elif status_code == 500:
            self.module.fail_json(
                changed=False, msg="Server error", status_code=status_code
            )
        else:
            self.module.fail_json(
                changed=False, msg="Unexpected error", status_code=status_code
            )


def run(module):
    state = module.params.pop("state")
    one_click = DOOneClick(module)
    if state == "present":
        one_click.get()


def main():
    argument_spec = DigitalOceanBaseModule.argument_spec()
    argument_spec.update(
        state=dict(type="str", choices=["present"], default="present"),
        type=dict(type="str", choices=["droplet", "kubernetes"], required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
    )
    run(module)


if __name__ == "__main__":
    main()
