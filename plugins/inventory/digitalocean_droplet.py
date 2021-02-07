# -*- coding: utf-8 -*
# Copyright (c) 2021 Ansible Project
# Copyright (c) 2021 Mark Mercado (mamercad@gmail.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: digitalocean_droplet
    plugin_type: inventory
    short_description: DigitalOcean Droplet inventory.
    version_added: "2.10"
    requirements:
        - requests
    description:
        - Get inventory hosts from DigitalOcean Droplets.
        - Uses a YAML configuration file ending with C(digitalocean_droplet.(yml|yaml)).
        - Droplet public IPs are set as C(ansible_host).
        - Username C(root) is set as C(ansible_user).
        - Hosts are grouped by region slug, for example, C(nyc1).
    notes:
        - Ensure that the environment variable C($DO_TOKEN) is set.
    author:
        - Mark Mercado (@mamercad)
    options:
        plugin:
            description: Token that ensures this is a source file for the plugin.
            required: True
            choices: ['digitalocean_droplet']
'''
EXAMPLES = '''
'''

import os
import requests

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils.six import string_types
from ansible.module_utils._text import to_native, to_text
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.plugins.inventory import BaseFileInventoryPlugin

NoneType = type(None)


class InventoryModule(BaseFileInventoryPlugin):

    NAME = 'digitalocean'

    def __init__(self):
        super(InventoryModule, self).__init__()
        if os.getenv('DO_TOKEN') is None:
            raise AnsibleError("digitalocean_droplet inventory requires environment variable $DO_TOKEN to be set")

    def verify_file(self, path):
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('digitalocean_droplet.yml', 'digitalocean_droplet.yaml')):
                return True
        self.display.debug("digitalocean_droplet inventory filename must end with 'digitalocean_droplet.yml' or 'digitalocean_droplet.yaml'")
        return False

    def _get_droplets(self, *args, **kwargs):

        if 'start' in kwargs:
            u = kwargs['start']
        else:
            u = 'https://api.digitalocean.com/v2/droplets?page=1&per_page=1'

        try:

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(os.getenv('DO_TOKEN')),
            }

            r = requests.get(u, headers=headers)
            j = r.json()

            # Get all Droplets (add if network type is public)
            for droplet in j['droplets']:
                for ipver in droplet['networks']:
                    for network in droplet['networks'][ipver]:
                        if network['type'] == 'public':
                            # Group by region
                            self.inventory.add_group(droplet['region']['slug'])
                            self.inventory.add_host(droplet['name'], droplet['region']['slug'])
                            # Set ansible_host and ansible_user
                            self.inventory.set_variable(droplet['name'], 'ansible_host', network['ip_address'])
                            self.inventory.set_variable(droplet['name'], 'ansible_user', 'root')

            # Recurse through links['pages']['next']
            if 'pages' in j['links'].keys():
                if 'next' in j['links']['pages'].keys():
                    self._get_droplets(start=j['links']['pages']['next'])

        except Exception as e:
            raise AnsibleError(e)

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)
        self._read_config_data(path)
        self._get_droplets()
