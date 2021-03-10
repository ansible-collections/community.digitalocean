#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Christopher Becker <cbecker333@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: digital_ocean_vpc
short_description: Manage VPCs in DigitalOcean
description:
    - Create, Retrieve and remove VPCs DigitalOcean.
author: "Christopher Becker (@readysetawesome)"
options:
  name:
    description:
     - The name of the VPC.
    required: True
    type: str
  description:
    description:
    - A text description of the network
    type: str
  ip_range:
    description:
    - CIDR list of ips to cover
    type: str
  region:
    description:
    - Which hosting region to place the new VPC in
    type: str
    required: True
  state:
    description:
     - Whether the VPC should be present or absent.
    default: present
    choices: ['present', 'absent']
    type: str
extends_documentation_fragment:
- community.digitalocean.digital_ocean.documentation

notes:
  - Any of these environment variables can be used, DO_API_KEY, DO_OAUTH_TOKEN and DO_API_TOKEN.
    They refer to the v2 token.
'''


EXAMPLES = r'''
- name: Create a VPC
  community.digitalocean.digital_ocean_vpc:
    name: production-nyc3
    state: present
    description: The best VPC in our network
    ip_range: 10.10.10.0/20
    region: nyc3

- name: Remove a VPC
  community.digitalocean.digital_ocean_vpc:
    name: production-nyc3
    state: absent

'''


RETURN = r''' #
 '''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.digitalocean.plugins.module_utils.digital_ocean import DigitalOceanHelper
from ansible.module_utils._text import to_native


def core(module):
    state = module.params['state']
    name = module.params['name']

    rest = DigitalOceanHelper(module)

    results = dict(changed=False)

    response = rest.get('vpcs')
    status_code = response.status_code
    resp_json = response.json

    if status_code != 200:
        module.fail_json(msg="Failed to retrieve VPCs for DigitalOcean")

    if state == 'present':
        for vpc in resp_json['vpcs']:
            if vpc['name'] == name:
                results.update(changed=False, response=vpc)

        # VPC does not exist, let us create it
        vpc_data = dict(name=name,
                        description=module.params['description'],
                        region=module.params['region'],
                        ip_range=module.params['ip_range'])

        response = rest.post('vpcs', data=vpc_data)
        status_code = response.status_code
        if status_code == 500:
            module.fail_json(msg="Failed to create VPCs.")

        resp_json = response.json
        if status_code == 201:
            results.update(changed=True, response=resp_json)
        elif status_code == 422:
            results.update(changed=False, response=resp_json)

    elif state == 'absent':
        vpc_id_del = None
        for vpc in resp_json['vpcs']:
            if vpc['name'] == name:
                vpc_id_del = vpc['id']

        if vpc_id_del is not None:
            url = "vpcs/{0}".format(vpc_id_del)
            response = rest.delete(url)
            if response.status_code == 204:
                results.update(changed=True)
            elif response.status_code == 403:
                module.fail_json(msg="Can't delete VPC %s because it still contains resources" % name)
            else:
                results.update(changed=False)
        else:
            module.fail_json(msg="Failed to find VPC %s" % name)

    module.exit_json(**results)


def main():
    argument_spec = DigitalOceanHelper.digital_ocean_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True),
        description=dict(type='str'),
        region=dict(type='str', required=True),
        state=dict(choices=['present', 'absent'], default='present'),
        ip_range=dict(type='str')
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['name', 'region']),
        ],
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e))


if __name__ == '__main__':
    main()
