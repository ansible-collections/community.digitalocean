#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2018, Ansible Project
# Copyright: (c) 2020, Tyler Auerbeck <tauerbec@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: digital_ocean_droplet_info
short_description: Gather information about DigitalOcean Droplets
description:
    - This module can be used to gather information about Droplets.
author: "Tyler Auerbeck (@tylerauerbeck)"
version_added: 1.6.0

options:
  id:
    description:
      - Project ID that can be used to identify and reference a project.
    type: str
  name:
    description:
      - Project name that can be used to identify and reference a project.
    type: str

extends_documentation_fragment:
- community.digitalocean.digital_ocean
'''


EXAMPLES = r'''
TODO: Add examples
'''

RETURN = r'''
data:
  description: "DigitalOcean droplet information"
  elements: dict
  returned: success
  sample:
    TODO: Add sample
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.digitalocean.plugins.module_utils.digital_ocean import DigitalOceanHelper


def run(module):
    rest = DigitalOceanHelper(module)

    if module.params["id"]:
        response = rest.get('projects/{0}'.format(module.params["id"]))
        if response.status_code != 200:
            module.fail_json(msg="Failed to fetch 'projects' information due to error: %s" % response.json["message"])
    else:
        response = rest.get_paginated_data(base_url='projects?', data_key_name='projects')

    if module.params["id"]:
        data = [response.json["project"]]
    elif module.params["name"]:
        data = [d for d in response if d["name"] == module.params["name"]]
        if not data:
            module.fail_json(msg="Failed to fetch 'projects' information due to error: Unable to find project with name %s" % module.params["name"])
    else:
        data = response

    module.exit_json(changed=False, data=data)


def main():
    argument_spec = DigitalOceanHelper.digital_ocean_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=False, default=None),
        id=dict(type='str', required=False, default=None)
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[('id', 'name')])
    run(module)


if __name__ == '__main__':
    main()
