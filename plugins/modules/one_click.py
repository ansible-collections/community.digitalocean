#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright: (c) Ansible Project 2022
# Copyright: (c) DigitalOcean 2022
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: one_click
short_description: Gather information about DigitalOcean User account
description:
    - This module can be used to gather information about User account.
    - This module was called C(digital_ocean_account_facts) before Ansible 2.9. The usage did not change.
author: "Abhijeet Kasurde (@Akasurde)"

requirements:
  - "python >= 2.6"

extends_documentation_fragment:
- community.digitalocean.digital_ocean.documentation

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

    def create(self):
        self.module.exit_json(changed=False, msg="Hello")

    def delete(self):
        self.module.exit_json(changed=False, msg="Goodbye")


def run(module):
    state = module.params.pop("state")
    one_click = DOOneClick(module)
    if state == "present":
        one_click.create()
    elif state == "absent":
        one_click.delete()


def main():
    argument_spec = DigitalOceanBaseModule.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        description=dict(type="str"),
        default=dict(type="bool", default=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    run(module)


if __name__ == "__main__":
    main()
