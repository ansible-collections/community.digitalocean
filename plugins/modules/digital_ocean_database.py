#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: digital_ocean_database
short_description: Create and delete a DigitalOcean database
description:
    - Create and delete a database in DigitalOcean and optionally wait for it to be active.
author: "Mark Mercado (@mamercad)"
options:
    state:
        description:
            - Indicate desired state of the target.
        default: present
        choices: ['present', 'active']
        type: str
    id:
        description:
            - ID of the database.
        type: int
        aliases: ['database_id']
    name:
        description:
            - Name of the database.
        type: str
        required: true
    engine:
        description:
            - Database engine.
        type: str
        required: true
        choices: ['pg', 'mysql', 'redis']
    version:
        description:
            - Database version.
            - For Postgres (pg), versions are 10, 11 and 12.
            - For MySQL, version is 8.
            - For Redis, version is 5.
        type: str
    size:
        description:
            - Database size.
        type: str
        required: true
        aliases: ['size_id']
    region:
        description:
            - Database region.
        type: str
        required: true
        aliases: ['region_id']
    num_nodes:
        description:
            - Database nodes.
        type: int
        default: 1
    tags:
        description:
            - List of tags.
        type: list
        elements: str
    private_network_uuid:
        description:
            - VPC UUID to place in.
        type: str
'''


from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.community.digitalocean.plugins.module_utils.digital_ocean import DigitalOceanHelper


class DODatabase(object):
    def __init__(self, module):
        self.module = module
        self.rest = DigitalOceanHelper(module)
        # pop the oauth token so we don't include it in the POST data
        self.module.params.pop('oauth_token')

    def get_by_id(self):
        pass

    def get_database(self):
        json_data = self.get_by_id(self.module.params['id'])
        if not json_data and self.unique_name:
            json_data = self.get_by_name(self.module.params['name'])
        return json_data

    def create(self):
        self.module.exit_json(changed=True, msg="Create")

    def delete(self):
        self.module.exit_json(changed=True, msg="Delete")


def run(module):
    state = module.params.pop('state')
    database = DODatabase(module)
    if state == 'present':
        database.create()
    elif state == 'absent':
        database.delete()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=['present', 'absent'], default='present'),
            oauth_token=dict(
                aliases=['API_TOKEN'],
                no_log=True,
                fallback=(env_fallback, ['DO_API_TOKEN', 'DO_API_KEY', 'DO_OAUTH_TOKEN']),
                required=True,
            ),
            id=dict(type=int, aliases=['database_id']),
            name=dict(type='str', required=True),
            engine=dict(choices=['pg', 'mysql', 'redis'], required=True),
            version=dict(type='str'),
            size=dict(type='str', aliases=['size_id'], required=True),
            region=dict(type='str', aliases=['region_id'], required=True),
            num_nodes=dict(type=int, default=1),
            tags=dict(type='list', elements='str'),
            private_network_uuid=dict(type='str'),
        ),
        required_one_of=(
            ['id', 'name'],
        ),
        required_if=([
            ('state', 'present', ['name', 'size', 'engine', 'region']),
        ]),
        supports_check_mode=True,
    )
    run(module)


if __name__ == '__main__':
    main()
