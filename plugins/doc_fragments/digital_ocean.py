# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Ansible Project
# Copyright: (c) 2018, Abhijeet Kasurde (akasurde@redhat.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    # Parameters for DigitalOcean modules
    DOCUMENTATION = r"""
options:
  baseurl:
    description:
      - DigitalOcean API base url.
    type: str
    default: https://api.digitalocean.com/v2
  oauth_token:
    description:
      - DigitalOcean OAuth token.
      - "There are several other environment variables which can be used to provide this value."
    type: str
    aliases: [ api_token ]
    env:
      - name: DO_API_TOKEN
      - name: DO_API_KEY
      - name: DO_OAUTH_TOKEN
      - name: OAUTH_TOKEN
  timeout:
    description:
    - The timeout in seconds used for polling DigitalOcean's API.
    type: int
    default: 30
  validate_certs:
    description:
    - If set to C(no), the SSL certificates will not be validated.
    - This should only set to C(no) used on personally controlled sites using self-signed certificates.
    type: bool
    default: true
"""
