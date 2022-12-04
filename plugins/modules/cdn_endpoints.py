#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cdn_endpoints

short_description: Manage CDN endpoints

version_added: 2.0.0

description:
  - "Manage CDN endpoints: create, update, delete, purge cache."
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/cdn_create_endpoint).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  origin:
    description:
      - The fully qualified domain name (FQDN) for the origin server which provides the content for the CDN.
      - This is currently restricted to a Space.
    type: str
    required: true
  ttl:
    description:
      - The amount of time the content is cached by the CDN's edge servers in seconds.
      - TTL must be one of 60, 600, 3600, 86400, or 604800.
      - Defaults to 3600 (one hour) when excluded.
    type: int
    choices: [60, 600, 3600, 86400, 604800]
    default: 3600
    required: false
  certificate_id:
    description:
      - The ID of a DigitalOcean managed TLS certificate used for SSL when a custom subdomain is provided.
    type: str
    required: false
  custom_domain:
    description:
      - The fully qualified domain name (FQDN) of the custom subdomain used with the CDN endpoint.
    type: str
    required: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create DigitalOcean CDN endpoint
  community.digitalocean.cdn_endpoints:
    token: "{{ token }}"
    origin: ansible-gh-ci-space-0.nyc3.digitaloceanspaces.com
"""


RETURN = r"""
endpoint:
  description: DigitalOcean CDN endpoint.
  returned: always
  type: dict
  sample:
    created_at: '2022-12-01T15:05:42Z'
    endpoint: ansible-gh-ci-space-0.nyc3.cdn.digitaloceanspaces.com
    id: e6893ada-0fd7-48c2-88af-7c2784f404f2
    origin: ansible-gh-ci-space-0.nyc3.digitaloceanspaces.com
    ttl: 3600
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: CDN endpoints result information.
  returned: always
  type: str
  sample:
    - CDN endpoint not found
    - CDN endpoint ansible-gh-ci-space-0.nyc3.digitaloceanspaces.com created
    - CDN endpoint ansible-gh-ci-space-0.nyc3.digitaloceanspaces.com deleted
    - CDN endpoint ansible-gh-ci-space-0.nyc3.digitaloceanspaces.com exists
    - CDN endpoint ansible-gh-ci-space-0.nyc3.digitaloceanspaces.com updated
    - CDN endpoint ansible-gh-ci-space-0.nyc3.digitaloceanspaces.com not updated
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.digitalocean.plugins.module_utils.common import (
    DigitalOceanOptions,
)

import traceback

HAS_AZURE_LIBRARY = False
AZURE_LIBRARY_IMPORT_ERROR = None
try:
    from azure.core.exceptions import HttpResponseError
except ImportError:
    AZURE_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_AZURE_LIBRARY = True

HAS_PYDO_LIBRARY = False
PYDO_LIBRARY_IMPORT_ERROR = None
try:
    from pydo import Client
except ImportError:
    PYDO_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_PYDO_LIBRARY = True


class CDNEndpoints:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.origin = module.params.get("origin")
        self.ttl = module.params.get("ttl")
        self.certificate_id = module.params.get("certificate_id")
        self.custom_domain = module.params.get("custom_domain")
        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def find_by_origin(self):
        """Finds and returns existing CDN based on the "origin" FQDN."""
        try:
            cdns = self.client.cdn.list_endpoints()
            cdn_endpoints = cdns.get("endpoints")
            if not cdn_endpoints:
                return None
            for cdn in cdn_endpoints:
                origin = cdn.get("origin")
                if origin == self.origin:
                    return cdn
            return None
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, endpoint=[]
            )

    def is_same(self, found_cdn):
        if self.origin != found_cdn.get("origin"):
            return False
        if self.ttl != found_cdn.get("ttl"):
            return False
        return True

    def present(self):
        """Creates or updates a CDN endpoint."""

        found_cdn = self.find_by_origin()
        if found_cdn:
            if self.is_same(found_cdn=found_cdn):
                self.module.exit_json(
                    changed=False,
                    msg=f"CDN endpoint {self.origin} exists",
                    endpoint=found_cdn,
                )
            try:
                found_cdn_id = found_cdn.get("id")
                body = {
                    "ttl": self.ttl,
                    "certificate_id": self.certificate_id,
                    "custom_domain": self.custom_domain,
                }
                cdn = self.client.cdn.update_endpoints(cdn_id=found_cdn_id, body=body)
                if cdn:
                    self.module.exit_json(
                        changed=True,
                        msg=f"CDN endpoint {self.origin} updated",
                        endpoint=cdn.get("endpoint"),
                    )
                self.module.fail_json(
                    changed=False, msg=f"CDN endpoint {self.origin} not updated"
                )
            except HttpResponseError as err:
                error = {
                    "Message": err.error.message,
                    "Status Code": err.status_code,
                    "Reason": err.reason,
                }
                if err.status_code == 409:  # The CDN already exists
                    existing_cdn = self.find_by_origin()
                    if not existing_cdn:
                        self.module.fail_json(
                            changed=False,
                            msg=error.get("Message"),
                            error=error,
                            endpoint=[],
                        )
                    self.module.exit_json(changed=False, endpoint=existing_cdn)
                self.module.fail_json(
                    changed=False, msg=error.get("Message"), error=error, endpiont=[]
                )

        try:
            body = {
                "origin": self.origin,
                "ttl": self.ttl,
                "certificate_id": self.certificate_id,
                "custom_domain": self.custom_domain,
            }
            cdn = self.client.cdn.create_endpoint(body=body)
            if cdn:
                self.module.exit_json(
                    changed=True,
                    msg=f"CDN endpoint {self.origin} created",
                    endpoint=cdn.get("endpoint"),
                )
            self.module.fail_json(
                changed=False,
                msg=f"CDN endpoint {self.origin} not created",
                endpoint=[],
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            if err.status_code == 409:  # The CDN already exists
                existing_cdn = self.find_by_origin()
                if not existing_cdn:
                    self.module.fail_json(
                        changed=False,
                        msg=error.get("Message"),
                        error=error,
                        endpoint=[],
                    )
                self.module.exit_json(changed=False, endpoint=existing_cdn)
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, endpoint=[]
            )

    def absent(self):
        """Removes a CDN endpoint."""
        found_cdn = self.find_by_origin()
        if not found_cdn:
            self.module.exit_json(
                changed=False,
                msg=f"CDN endpoint {self.origin} not found",
                endpoint=[],
            )

        found_cdn_id = found_cdn.get("id")
        if not found_cdn_id:
            self.module.fail_json(
                changed=False,
                msg=f"CDN endpoint {self.origin} ID not found",
                endpoint=found_cdn,
            )

        try:
            self.client.cdn.delete_endpoint(cdn_id=found_cdn_id)
            self.module.exit_json(
                changed=True,
                msg=f"CDN endpoint {self.origin} deleted",
                endpoint=found_cdn,
            )
        except HttpResponseError as err:
            error_message = None
            if hasattr("err.error", "message"):
                error_message = err.error.message
            error = {
                "Message": error_message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error_message, error=error, endpoint=found_cdn
            )


def main():
    """The main function."""
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        origin=dict(type="str", required=True),
        ttl=dict(
            type="int",
            choices=[60, 600, 3600, 86400, 604800],
            default=3600,
            required=False,
        ),
        certificate_id=dict(type="str", required=False),
        custom_domain=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    if not HAS_AZURE_LIBRARY:
        module.fail_json(
            msg=missing_required_lib("azure.core.exceptions"),
            exception=AZURE_LIBRARY_IMPORT_ERROR,
        )
    if not HAS_PYDO_LIBRARY:
        module.fail_json(
            msg=missing_required_lib("pydo"),
            exception=PYDO_LIBRARY_IMPORT_ERROR,
        )

    CDNEndpoints(module)


if __name__ == "__main__":
    main()
