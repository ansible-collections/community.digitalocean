#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2018, Ansible Project
# Copyright: (c) 2018, Abhijeet Kasurde <akasurde@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: size_info
short_description: Gather information about DigitalOcean Droplet sizes
description:
    - This module can be used to gather information about droplet sizes.
    - This module was called C(size_facts) before Ansible 2.9. The usage did not change.
author: "Abhijeet Kasurde (@Akasurde)"
requirements:
  - "python >= 2.6"
extends_documentation_fragment:
- community.digitalocean.digitalocean.documentation

'''


EXAMPLES = r'''
- name: Gather information about all droplet sizes
  community.digitalocean.size_info:
    oauth_token: "{{ oauth_token }}"

- name: Get droplet Size Slug where vcpus is 1
  community.digitalocean.size_info:
    oauth_token: "{{ oauth_token }}"
  register: resp_out
- debug: var=resp_out
- set_fact:
    size_slug: "{{ item.slug }}"
  loop: "{{ resp_out.data | community.general.json_query(name) }}"
  vars:
    name: "[?vcpus==`1`]"
- debug:
    var: size_slug


'''


RETURN = r'''
data:
    description: DigitalOcean droplet size information
    returned: success
    type: list
    sample: [
        {
            "available": true,
            "disk": 20,
            "memory": 512,
            "price_hourly": 0.00744,
            "price_monthly": 5.0,
            "regions": [
                "ams2",
                "ams3",
                "blr1",
                "fra1",
                "lon1",
                "nyc1",
                "nyc2",
                "nyc3",
                "sfo1",
                "sfo2",
                "sgp1",
                "tor1"
            ],
            "slug": "512mb",
            "transfer": 1.0,
            "vcpus": 1
        },
    ]
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.digitalocean.plugins.module_utils.digitalocean import DigitalOceanHelper
from ansible.module_utils._text import to_native


def core(module):
    rest = DigitalOceanHelper(module)

    response = rest.get('sizes')
    if response.status_code != 200:
        module.fail_json(msg="Failed to fetch 'sizes' information due to error : %s" % response.json['message'])

    module.exit_json(changed=False, data=response.json['sizes'])


def main():
    argument_spec = DigitalOceanHelper.argument_spec()
    module = AnsibleModule(
        argument_spec=argument_spec,
    )
    if module._name in ('size_facts', 'community.digitalocean.size_facts'):
        module.deprecate("The 'size_facts' module has been renamed to 'size_info'",
                         version='2.0.0', collection_name='community.digitalocean')  # was Ansible 2.13

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == '__main__':
    main()