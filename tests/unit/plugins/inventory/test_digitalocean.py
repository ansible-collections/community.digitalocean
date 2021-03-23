# Copyright (c) 2021 Ansible Project
# GNGeneral Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.errors import AnsibleParserError
from ansible.inventory.data import InventoryData
from ansible_collections.community.digitalocean.plugins.inventory.digitalocean import InventoryModule


@pytest.fixture()
def inventory():
    r = InventoryModule()
    r.inventory = InventoryData()
    return r


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('digitalocean_foobar.yml') is False


def get_payload():
    return [
        {
            "id": 3164444,
            "name": "foo",
            "memory": 1024,
            "vcpus": 1,
            "disk": 25,
            "locked": False,
            "status": "active",
            "kernel": {
                "id": 2233,
                "name": "Ubuntu 14.04 x64 vmlinuz-3.13.0-37-generic",
                "version": "3.13.0-37-generic"
            },
            "image": {
                "id": 6918990,
                "name": "14.04 x64",
                "distribution": "Ubuntu",
                "slug": "ubuntu-16-04-x64",
            },
            "size_slug": "s-1vcpu-1gb",
            "networks": {
                "v4": [
                    {
                        "ip_address": "104.236.32.182",
                        "netmask": "255.255.192.0",
                        "gateway": "104.236.0.1",
                        "type": "public"
                    }
                ],
                "v6": [
                    {
                        "ip_address": "2604:A880:0800:0010:0000:0000:02DD:4001",
                        "netmask": 64,
                        "gateway": "2604:A880:0800:0010:0000:0000:0000:0001",
                        "type": "public"
                    }
                ]
            },
            "region": {
                "name": "New York 3",
                "slug": "nyc3",
            },
            "tags": [

            ],
            "vpc_uuid": "f9b0769c-e118-42fb-a0c4-fed15ef69662"
        },
        {
            "id": 3164445,
            "name": "bar",
            "memory": 1024,
            "vcpus": 1,
            "disk": 25,
            "locked": False,
            "status": "active",
            "kernel": {
                "id": 2233,
                "name": "Ubuntu 14.04 x64 vmlinuz-3.13.0-37-generic",
                "version": "3.13.0-37-generic"
            },
            "image": {
                "id": 6918990,
                "name": "14.04 x64",
                "distribution": "Ubuntu",
                "slug": "ubuntu-16-04-x64",
            },
            "size_slug": "s-1vcpu-1gb",
            "networks": {
                "v4": [
                    {
                        "ip_address": "104.236.32.185",
                        "netmask": "255.255.192.0",
                        "gateway": "104.236.0.1",
                        "type": "public"
                    }
                ],
                "v6": [
                    {
                        "ip_address": "2604:A880:0800:0010:0000:0000:02DD:4004",
                        "netmask": 64,
                        "gateway": "2604:A880:0800:0010:0000:0000:0000:0001",
                        "type": "public"
                    }
                ]
            },
            "region": {
                "name": "Frankfurt 1",
                "slug": "fra1",
            },
            "tags": [

            ],
            "vpc_uuid": "f9b0769c-e118-42fb-a0c4-fed15ef69662"
        }
    ]


def get_option(option):
    options = {
        'attributes': ['id', 'size_slug'],
        'var_prefix': 'do_',
        'strict': False,
    }
    return options.get(option)


def test_populate_hostvars(inventory, mocker):
    inventory._get_payload = mocker.MagicMock(side_effect=get_payload)
    inventory.get_option = mocker.MagicMock(side_effect=get_option)
    inventory._populate()

    host_foo = inventory.inventory.get_host('foo')
    host_bar = inventory.inventory.get_host('bar')

    assert host_foo.vars['do_id'] == 3164444
    assert host_bar.vars['do_size_slug'] == "s-1vcpu-1gb"
