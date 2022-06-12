#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright: (c) Ansible Project 2022
# Copyright: (c) DigitalOcean 2022
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: one_click_info
version_added: 2.0.0
short_description: List all available 1-Click Applications
description:
  - List all available 1-Click Applications.
  - 1-Click applications are pre-built Droplet images or Kubernetes apps with software, features, and configuration details already set up for you.
  - They can be found in the in the DigitalOcean Marketplace U(https://docs.digitalocean.com/products/marketplace/).
author: Mark Mercado (@mamercad)
options:
  type:
    description:
      - Restricts results to a certain type of 1-Click Appliction.
      - If unspecified, returns all available 1-Click Applications.
    required: false
    choices: ["droplet", "kubernetes"]
    type: str
    aliases: ["app", "app_type"]
extends_documentation_fragment:
  - community.digitalocean.base_args.documentation
"""


EXAMPLES = r"""
- name: List all available 1-Click Applications
  community.digitalocean.one_click_info:
    oauth_token: "{{ lookup('ansible.builtin.env', 'DO_API_TOKEN') }}"

- name: List Droplet 1-Click Applications
  community.digitalocean.one_click_info:
    oauth_token: "{{ lookup('ansible.builtin.env', 'DO_API_TOKEN') }}"
    type: droplet

- name: List Kubernetes 1-Click Applications
  community.digitalocean.one_click_info:
    oauth_token: "{{ lookup('ansible.builtin.env', 'DO_API_TOKEN') }}"
    type: kubernetes
"""


RETURN = r"""
data:
  description: List of 1-Click Applications
  returned: always
  type: list
  elements: dict
  sample:
    - slug: nibblecomm-spotipo-18-04
      type: droplet
    - slug: skaffolder-18-04
      type: droplet
    - slug: deadletter-18-04
      type: droplet
msg:
  description: An informational message
  returned: always
  type: str
  sample: All 1-Click Applications
status_code:
  description: Status code received from the DigitalOcean API
  returned: always
  type: int
  sample: 200
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
        if not self.type:
            response = self.api.get("1-clicks")
        else:
            response = self.api.get("1-clicks?type={0}".format(self.type))
        status_code = response.status_code

        if status_code == 200:
            one_clicks = response.json.get("1_clicks")
            if not one_clicks:
                self.module.fail_json(
                    changed=False,
                    msg="Failed to get 1-Click Applications",
                    status_code=status_code,
                )
            else:
                if not self.type:
                    self.module.exit_json(
                        changed=False,
                        msg="All 1-Click Applications",
                        data=one_clicks,
                        status_code=status_code,
                    )
                else:
                    self.module.exit_json(
                        changed=False,
                        msg="All {0} 1-Click Applications".format(self.type.capitalize()),
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
        type=dict(type="str", choices=["droplet", "kubernetes"], aliases=["app", "app_type"], required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
    )
    run(module)


if __name__ == "__main__":
    main()
