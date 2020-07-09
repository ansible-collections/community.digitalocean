# -*- coding: utf-8 -*-
# Copyright (c) 2020, Per-Arne <per@sysx.no>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json

from ansible.module_utils.urls import open_url

DOCUMENTATION = r'''
    name: digitalocean
    plugin_type: inventory
    author:
        - Per-Arne Andersen
    short_description: Digital ocean inventory source
    extends_documentation_fragment:
        - constructed
    description:
        - Get inventory hosts from Digital Ocean public cloud.
        - Uses an YAML configuration file ending with either I(digital_ocean.yml) or I(digital_ocean.yaml) to set parameter values (also see examples).
        - Uses I(api_config), I(~/.digital_ocean.ini), I(./digital_ocean.ini) or C(DIGITALOCEAN_API_CONFIG) pointing to a Digitalocean credentials INI file
          (see U(https://docs.ansible.com/ansible/latest/scenario_guides/guide_digitalocean.html)).
    options:
        plugin:
            description: Token that ensures this is a source file for the 'digitalocean' plugin.
            type: string
            required: True
            choices: [ digitalocean ]
        api_account:
            description: Specify the account to be used.
            type: string
            default: default
        api_config:
            description: Path to the Digital Ocean configuration file. If not specified will be taken from regular Digital Ocean configuration.
            type: path
            env:
                - name: DIGITALOCEAN_API_CONFIG
        api_key:
            description: Digital Ocean API key. If not specified will be taken from regular Digital Ocean configuration.
            type: string
            env:
                - name: DIGITALOCEAN_API_KEY
        hostname:
            description: Field to match the hostname. Note v4_main_ip corresponds to the main_ip field returned from the API and name to label.
            type: string
            default: v4_main_ip
            choices:
                - v4_main_ip
                - v6_main_ip
                - name
        filter_by_tag:
            description: Only return servers filtered by this tag
            type: string
'''

EXAMPLES = r'''
# inventory_digitalocean.yml file in YAML format
# Example command line: ansible-inventory --list -i inventory_digitalocean.yml

# Group by a region as lower case and with prefix e.g. "digitalocean_region_ams3" and by OS without prefix e.g. "CentOS_7_x64"
plugin: digitalocean
keyed_groups:
  - prefix: ams3
    key: region['slug'] | lower


# Pass a tag filter to the API
plugin: digitalocean
filter_by_tag: server
'''


from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible.module_utils.six.moves import configparser
from ansible.module_utils._text import to_native
from ansible.module_utils.six.moves.urllib.parse import quote
import os

SCHEMA = {
    "id": dict(),
    "name": dict(),
    "memory": dict(),
    "vcpus": dict(),
    "disk": dict(),
    "locked": dict(convert_to='bool'),
    "status": dict(),
    "kernel": dict(),
    "created_at": dict(),
    "features": dict(),
    "backup_ids": dict(),
    "snapshot_ids": dict(),
    "image": dict(),
    "volume_ids": dict(),
    "size": dict(),
    "size_slug": dict(),
    "region": dict(),
    "tags": dict(),
    "vpc_uuid": dict(),
    "networks": dict(),
}

DIGITALOCEAN_API_ENDPOINT = "https://api.digitalocean.com/v2/"
DIGITALOCEAN_USER_AGENT = 'Ansible Digitalocean'


def _load_conf(path, account):

    if path:
        conf = configparser.ConfigParser()
        conf.read(path)

        if not conf._sections.get(account):
            return None

        return dict(conf.items(account))
    else:
        return InventoryModule.read_ini_config(account)


def _retrieve_servers(module, api_key, tag_filter=None):

    api_url = f"{DIGITALOCEAN_API_ENDPOINT}droplets{'' if tag_filter is None else '?tag_name=%s' % quote(tag_filter)}"
    try:
        response = open_url(
            api_url, headers={'Authorization': f"Bearer {api_key}"},
            http_agent=DIGITALOCEAN_USER_AGENT,
        )
        servers_list = json.loads(response.read())["droplets"]

        return servers_list if servers_list else []
    except ValueError as e:
        raise AnsibleError("Incorrect JSON payload %s" % (to_native(e), ))
    except Exception as e:
        raise AnsibleError("Error while fetching %s: %s" % (api_url, to_native(e)))


class InventoryModule(BaseInventoryPlugin, Constructable):

    NAME = 'community.digitalocean.digitalocean'

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('digital_ocean.yaml', 'digital_ocean.yml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)
        self._read_config_data(path=path)

        conf = _load_conf(self.get_option('api_config'), self.get_option('api_account'))
        try:
            api_key = self.get_option('api_key') or conf.get('key')
        except Exception:
            raise AnsibleError('Could not find an API key. Check inventory file and Digitalocean configuration files.')

        hostname_preference = self.get_option('hostname')

        # Add a top group 'digitalocean'
        self.inventory.add_group(group='digitalocean')

        # Filter by tag is supported by the api with a query
        filter_by_tag = self.get_option('filter_by_tag')

        self.params = dict(
            timeout=30,
            oauth_token=api_key
        )

        for server in _retrieve_servers(self, api_key, filter_by_tag):

            server = InventoryModule.normalize_result(server, SCHEMA)

            self.inventory.add_host(host=server['name'], group='digitalocean')

            for attribute, value in server.items():
                self.inventory.set_variable(server['name'], attribute, value)

            if hostname_preference != 'name':
                self.inventory.set_variable(server['name'], 'ansible_host', server[hostname_preference])

            # Use constructed if applicable
            strict = self.get_option('strict')

            # Composed variables
            self._set_composite_vars(self.get_option('compose'), server, server['name'], strict=strict)

            # Complex groups based on jinja2 conditionals, hosts that meet the conditional are added to group
            self._add_host_to_composed_groups(self.get_option('groups'), server, server['name'], strict=strict)

            # Create groups based on variable values and add the corresponding hosts to it
            self._add_host_to_keyed_groups(self.get_option('keyed_groups'), server, server['name'], strict=strict)

    @staticmethod
    def normalize_result(resource, schema, remove_missing_keys=True):
        if remove_missing_keys:
            fields_to_remove = set(resource.keys()) - set(schema.keys())
            for field in fields_to_remove:
                resource.pop(field)

        for search_key, config in schema.items():
            if search_key in resource:
                if 'convert_to' in config:
                    if config['convert_to'] == 'int':
                        resource[search_key] = int(resource[search_key])
                    elif config['convert_to'] == 'float':
                        resource[search_key] = float(resource[search_key])
                    elif config['convert_to'] == 'bool':
                        resource[search_key] = True if resource[search_key] == 'yes' else False

                if 'transform' in config:
                    resource[search_key] = config['transform'](resource[search_key])

                if 'key' in config:
                    resource[config['key']] = resource[search_key]
                    del resource[search_key]

        counters = ["main", "secondary", "third", "fourth", "fifth"]
        for version, network in resource["networks"].items():
            for idx, items in enumerate(network):
                prefix = f"{version}_{counters[idx]}"
                resource[f"{prefix}_ip"] = items["ip_address"]
                resource[f"{prefix}_netmask"] = items["netmask"]
                resource[f"{prefix}_gateway"] = items["gateway"]
                resource[f"{prefix}_type"] = items["type"]

        return resource

    @staticmethod
    def read_ini_config(ini_group):
        paths = (
            os.path.join(os.path.expanduser('~'), '.digital_ocean.ini'),
            os.path.join(os.getcwd(), 'digital_ocean.ini'),
        )
        if 'DIGITALOCEAN_API_CONFIG' in os.environ:
            paths += (os.path.expanduser(os.environ['DIGITALOCEAN_API_CONFIG']),)

        conf = configparser.ConfigParser()
        conf.read(paths)

        if not conf._sections.get(ini_group):
            return dict()

        return dict(conf.items(ini_group))
