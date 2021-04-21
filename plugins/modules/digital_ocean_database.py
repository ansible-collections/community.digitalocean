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
    wait:
        description:
            - Wait for the database to be active before returning.
        required: False
        default: True
        type: bool
    wait_timeout:
        description:
            - How long before wait gives up, in seconds, when creating a database.
        default: 120
        type: int
'''


import json
import time
from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.community.digitalocean.plugins.module_utils.digital_ocean import DigitalOceanHelper


class DODatabase(object):
    def __init__(self, module):
        self.module = module
        self.rest = DigitalOceanHelper(module)
        self.wait = self.module.params.pop('wait', True)
        self.wait_timeout = self.module.params.pop('wait_timeout', 120)
        # pop the oauth token so we don't include it in the POST data
        self.module.params.pop('oauth_token')
        self.id = None
        self.name = None
        self.engine = None
        self.version = None
        self.num_nodes = None
        self.region = None
        self.status = None
        self.size = None

    def get_by_id(self, database_id):
        if not database_id:
            return None
        response = self.rest.get('databases/{0}'.format(database_id))
        json_data = response.json
        if response.status_code == 200:
            database = json_data.get('database', None)
            if database is not None:
                self.id = database.get('id', None)
                self.name = database.get('name', None)
                self.engine = database.get('engine', None)
                self.version = database.get('version', None)
                self.version = database.get('num_nodes', None)
                self.version = database.get('region', None)
                self.version = database.get('status', None)
                self.version = database.get('size', None)
            return json_data
        return None

    def get_by_name(self, database_name):
        if not database_name:
            return None
        page = 1
        while page is not None:
            response = self.rest.get('databases?page={0}'.format(page))
            json_data = response.json
            if response.status_code == 200:
                for database in json_data['databases']:
                    if database.get('name', None) == database_name:
                        self.id = database.get('id', None)
                        self.name = database.get('name', None)
                        self.size = database.get('engine', None)
                        self.status = database.get('version', None)
                        self.version = database.get('num_nodes', None)
                        self.version = database.get('region', None)
                        self.version = database.get('status', None)
                        self.version = database.get('size', None)
                        return {'database': database}
                if 'links' in json_data and 'pages' in json_data['links'] and 'next' in json_data['links']['pages']:
                    page += 1
                else:
                    page = None
        return None

    def get_database(self):
        json_data = self.get_by_id(self.module.params['id'])
        if not json_data:
            json_data = self.get_by_name(self.module.params['name'])
        return json_data

    def ensure_online(self, database_id):
        end_time = time.time() + self.wait_timeout
        while time.time() < end_time:
            response = self.rest.get('databases/{0}'.format(database_id))
            json_data = response.json
            database = json_data.get('database', None)
            if database is not None:
                status = database.get('status', None)
                if status is not None:
                    if status == 'online':
                        return json_data
            time.sleep(10)
        self.module.fail_json(msg='Waiting for database online timeout')

    def create(self):
        json_data = self.get_database()

        if json_data is not None:
            database = json_data.get('database', None)
            if database is not None:
                self.module.exit_json(changed=False, data=json_data)
            else:
                self.module.fail_json(changed=False, msg='Unexpected error, please file a bug')

        if self.module.check_mode:
            self.module.exit_json(changed=True)

        request_params = dict(self.module.params)
        del request_params['id']

        response = self.rest.post('databases', data=request_params)
        json_data = response.json
        if response.status_code >= 400:
            self.module.fail_json(changed=False, msg=json_data['message'])
        database = json_data.get('database', None)
        if database is None:
            self.module.fail_json(changed=False, msg='Unexpected error, please file a bug')
        if self.wait:
            database_id = database.get('id', None)
            if database_id is None:
                self.module.fail_json(changed=False, msg='Unexpected error, please file a bug')
            json_data = self.ensure_online(database_id)
        self.module.exit_json(changed=True, data=json_data)

    def delete(self):
        json_data = self.get_database()
        if json_data is not None:
            if self.module.check_mode:
                self.module.exit_json(changed=True)
            database = json_data.get('database', None)
            database_id = database.get('id', None)
            database_name = database.get('name', None)
            database_region = database.get('region', None)
            if database_id is not None:
                response = self.rest.delete('databases/{0}'.format(database_id))
                json_data = response.json
                if response.status_code == 204:
                    self.module.exit_json(changed=True, msg='Deleted database {0} ({1}) in {2}'.format(database_name, database_id, database_region))
                self.module.fail_json(changed=False, msg='Failed to delete database {0} ({1}) in {2}: {3}'.format(database_name, database_id, database_region, json_data['message']))
            else:
                self.module.fail_json(changed=False, msg='Unexpected error, please file a bug')
        else:
            self.module.exit_json(changed=False, msg='Database {0} in {1} not found'.format(self.module.params['name'], self.module.params['region']))


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
            wait=dict(type='bool', default=True),
            wait_timeout=dict(default=120, type='int'),
        ),
        required_one_of=(
            ['id', 'name'],
        ),
        required_if=([
            ('state', 'present', ['name', 'size', 'engine', 'region']),
            ('state', 'absent', ['name', 'size', 'engine', 'region']),
        ]),
        supports_check_mode=True,
    )
    run(module)


if __name__ == '__main__':
    main()
