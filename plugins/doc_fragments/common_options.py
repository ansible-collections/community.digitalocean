# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r"""
options:
  state:
    description:
      - State of the resource, C(present) to create, C(absent) to destroy.
    type: str
    required: true
    default: present
  token:
    description:
      - DigitalOcean API token.
      - There are several environment variables which can be used to provide this value.
      - C(DIGITALOCEAN_TOKEN), C(DO_API_TOKEN), C(DO_API_KEY), C(DO_OAUTH_TOKEN) and C(OAUTH_TOKEN)
    type: str
    aliases: [ oauth_token, api_token ]
    required: false
"""
