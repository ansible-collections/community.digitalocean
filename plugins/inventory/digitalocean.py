# -*- coding: utf-8 -*-

# Copyright: (c), Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
name: digitalocean
author:
  - Janos Gerzson (@grzs)
  - Tadej Borovšak (@tadeboro)
short_description: DigitalOcean Inventory Plugin
version_added: "1.1.0"
description:
  - DigitalOcean (DO) inventory plugin.
  - Acquires droplet list from DO API.
  - Uses configuration file that ends with '(do_hosts|digitalocean|digital_ocean).(yaml|yml)'.
extends_documentation_fragment:
  - community.digitalocean.digital_ocean.documentation
  - constructed
  - inventory_cache
options:
  plugin:
    description:
      - The name of the DigitalOcean Inventory Plugin,
        this should always be C(community.digitalocean.digitalocean).
    required: true
    choices: ['community.digitalocean.digitalocean']
  api_token:
    description:
     - DigitalOcean OAuth token.
    required: true
    type: str
    aliases: [ oauth_token ]
    env:
      - name: DO_API_TOKEN
  attributes:
    description: >-
      Droplet attributes to add as host vars to each inventory host.
      Check out the DO API docs for full list of attributes at
      U(https://developers.digitalocean.com/documentation/v2/#list-all-droplets).
    type: list
    elements: str
    default:
      - id
      - name
      - networks
      - region
      - size_slug
  var_prefix:
    description:
      - Prefix of generated varible names (e.g. C(tags) -> C(do_tags))
    type: str
    default: 'do_'
  pagination:
    description:
      - Maximum droplet objects per response page.
      - If the number of droplets related to the account exceeds this value,
        the query will be broken to multiple requests (pages).
      - DigitalOcean currently allows a maximum of 200.
    type: int
    default: 200
'''

EXAMPLES = r'''
# Using keyed groups and compose for hostvars
plugin: community.digitalocean.digitalocean
api_token: "{{ api_token }}"
attributes:
  - id
  - name
  - memory
  - vcpus
  - disk
  - size
  - image
  - networks
  - volume_ids
  - tags
  - region
keyed_groups:
  - key: do_region.slug
    prefix: 'region'
    separator: '_'
  - key: do_tags | lower
    prefix: ''
    separator: ''
compose:
  ansible_host: do_networks.v4 | selectattr('type','eq','public')
    | map(attribute='ip_address') | first
  class: do_size.description | lower
  distro: do_image.distribution | lower
'''

import re
import json
from ansible.errors import AnsibleParserError
from ansible.module_utils.urls import Request
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = 'community.digitalocean.digitalocean'

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(
                    ('do_hosts.yaml', 'do_hosts.yml',
                     'digitalocean.yaml', 'digitalocean.yml',
                     'digital_ocean.yaml', 'digital_ocean.yml')
            ):
                valid = True
            else:
                self.display.vvv(
                    'Skipping due to inventory source file name mismatch. '
                    'The file name has to end with one of the following: '
                    'do_hosts.yaml, do_hosts.yml '
                    'digitalocean.yaml, digitalocean.yml, '
                    'digital_ocean.yaml, digital_ocean.yml.')
        return valid

    def _get_payload(self):
        # request parameters
        api_token = self.get_option('api_token')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(api_token)
        }

        # build url
        pagination = self.get_option('pagination')
        url = 'https://api.digitalocean.com/v2/droplets?per_page=' + str(pagination)

        # send request(s)
        self.req = Request(headers=headers)
        payload = []
        try:
            while url:
                self.display.vvv('Sending request to {0}'.format(url))
                response = json.load(self.req.get(url))
                payload.extend(response['droplets'])
                url = response.get('links', {}).get('pages', {}).get('next')
        except ValueError:
            raise AnsibleParserError("something went wrong with JSON loading")
        except (URLError, HTTPError) as error:
            raise AnsibleParserError(error)

        return payload

    def _populate(self):
        attributes = self.get_option('attributes')
        var_prefix = self.get_option('var_prefix')
        strict = self.get_option('strict')
        for record in self._get_payload():

            # add host to inventory
            if record.get('name'):
                host_name = self.inventory.add_host(record.get('name'))
            else:
                continue

            # set variables for host
            for k, v in record.items():
                if k in attributes:
                    self.inventory.set_variable(host_name, var_prefix + k, v)

            self._set_composite_vars(
                self.get_option('compose'),
                self.inventory.get_host(host_name).get_vars(), host_name, strict)

            # set composed and keyed groups
            self._add_host_to_composed_groups(self.get_option('groups'),
                                              dict(), host_name, strict)
            self._add_host_to_keyed_groups(self.get_option('keyed_groups'),
                                           dict(), host_name, strict)

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)

        # cache settings
        self._read_config_data(path)
        self.cache_key = self.get_cache_key(path)

        self.use_cache = self.get_option('cache') and cache
        self.update_cache = self.get_option('cache') and not cache

        results = []
        if not self.update_cache:
            try:
                results = self._cache[self.cache_key]['digitalocean']
            except KeyError:
                pass

        if not results:
            if self.cache_key not in self._cache:
                self._cache[self.cache_key] = {'digitalocean': ''}

        self._populate()
