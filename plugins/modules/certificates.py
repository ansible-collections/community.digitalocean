#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: certificates

short_description: Manage certificates

version_added: 2.0.0

description:
  - "Manage CDN endpoints: create, update, delete, purge cache."
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/cdn_create_endpoint).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - A unique human-readable name referring to a certificate.
      - To create a certificate from Let's Encrypt, provide C(dns_names).
      - To create a custom certificate, provide C(private_key), C(leaf_certificate), and optionally C(certificate_chain).
      - View API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/certificates_create).
    required: true
    type: str
  dns_names:
    description:
      - An array of fully qualified domain names (FQDNs) for which the certificate was issued.
      - A certificate covering all subdomains can be issued using a wildcard (e.g. C(*.example.com)).
    type: list
    elements: str
    required: false
  private_key:
    description:
      - The contents of a PEM-formatted private-key corresponding to the SSL certificate.
    type: str
    required: false
  leaf_certificate:
    description:
      - The contents of a PEM-formatted public SSL certificate.
    type: str
    required: false
  certificate_chain:
    description:
      - The full PEM-formatted trust chain between the certificate authority's certificate and your domain's SSL certificate.
    type: str
    required: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create custom certificate
  community.digitalocean.cdn_endpoints:
    token: "{{ token }}"
    name: custom.example.com
    private_key: |
      -----BEGIN PRIVATE KEY-----
      MIIJQwIBADANBgkqhkiG9w0BAQEFAASCCS0wggkpAgEAAoICAQDE39Eyyp2QJIp6
      IvXELS4L+Wa8dAM4Uk0enV3PJKm2a674Ys0WSle2dzsd1EfpRXMNTt+iPZCyZQIS
      ...
    leaf_certificate: |
      -----BEGIN CERTIFICATE-----
      MIIF8jCCA9oCCQDHvZvzJneVuzANBgkqhkiG9w0BAQsFADCBujELMAkGA1UEBhMC
      VVMxETAPBgNVBAgMCE1pY2hpZ2FuMRQwEgYDVQQHDAtHcmFuZCBCbGFuYzETMBEG
      ...

- name: Create Let's Encrypt certificate
  community.digitalocean.cdn_endpoints:
    token: "{{ token }}"
    name: letsencrypt.example.com
    dns_names:
      - letsencrypt.example.com
"""


RETURN = r"""
certificate:
  description: Certificate.
  returned: always
  type: dict
  sample:
    id: 892071a0-bb95-49bc-8021-3afd67a210bf
    name: web-cert-01
    not_after: '2017-02-22T00:23:00Z'
    sha1_fingerprint: dfcc9f57d86bf58e321c2c6c31c7a971be244ac7
    created_at: '2017-02-08T16:02:37Z'
    dns_names: []
    state: verified
    type: custom
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Certificate result information.
  returned: always
  type: str
  sample:
    - Certificate web-cert-01 not found
    - Certificate web-cert-01 ID not found
    - Certificate web-cert-01 created
    - Certificate web-cert-01 created but not found yet
    - Certificate web-cert-01 not created
    - Certificate web-cert-01 deleted
    - Certificate web-cert-01 exists
"""

import time
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.digitalocean.plugins.module_utils.common import (
    DigitalOceanOptions,
    DigitalOceanFunctions,
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


class Certificates:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.name = module.params.get("name")
        self.dns_names = module.params.get("dns_names")
        self.private_key = module.params.get("private_key")
        self.leaf_certificate = module.params.get("leaf_certificate")
        self.certificate_chain = module.params.get("certificate_chain")
        self.type = None
        if self.dns_names:
            self.type = "lets_encrypt"
        elif self.private_key and self.leaf_certificate:
            self.type = "custom"
        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def find_by_name_and_type(self):
        """Finds and returns existing certificate based on the name."""
        certificates = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.certificates,
            meth="list",
            key="certificates",
            exc=HttpResponseError,
        )
        for certificate in certificates:
            if self.name == certificate.get("name"):
                if self.type == certificate.get("type"):
                    return certificate
        return None

    def present(self):
        """Creates or updates a certificate."""
        found_certificate = self.find_by_name_and_type()
        if found_certificate:
            self.module.exit_json(
                changed=False,
                msg=f"Certificate {self.name} found",
                certificate=found_certificate,
            )

        if self.type == "custom":
            try:
                body = {
                    "name": self.name,
                    "type": self.type,
                    "private_key": self.private_key,
                    "leaf_certificate": self.leaf_certificate,
                    "certificate_chain": self.certificate_chain,
                }
                certificate = self.client.certificates.create(body=body)
                if certificate:
                    self.module.exit_json(
                        changed=True,
                        msg=f"Certificate {self.name} created",
                        certificate=certificate.get("certificate"),
                    )
                self.module.fail_json(
                    changed=False, msg=f"Certificate {self.name} not created"
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
                self.module.fail_json(changed=False, msg=error_message, error=error)

        elif self.type == "lets_encrypt":
            try:
                body = {
                    "name": self.name,
                    "type": self.type,
                    "dns_names": self.dns_names,
                }
                certificate = self.client.certificates.create(body=body)
                if certificate:
                    self.module.exit_json(
                        changed=True,
                        msg=f"Certificate {self.name} created",
                        certificate=certificate,
                    )
                self.module.fail_json(
                    changed=False, msg=f"Certificate {self.name} not created"
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
                if err.status_code == 202:  # Accepted (not in the API documentation)
                    time.sleep(30)  # TODO: Put this in a loop or something
                    found_certificate = self.find_by_name_and_type()
                    if found_certificate:
                        self.module.exit_json(
                            changed=True,
                            msg=f"Certificate {self.name} created",
                            certificate=found_certificate,
                        )
                    self.module.exit_json(
                        changed=True,
                        msg=f"Certificate {self.name} created but not found yet",
                        certificate=[],
                    )
                self.module.fail_json(changed=False, msg=error_message, error=error)

    def absent(self):
        """Removes a certificate."""
        found_certificate = self.find_by_name_and_type()
        if not found_certificate:
            self.module.exit_json(
                changed=False,
                msg=f"Certificate {self.name} not found",
                certificate=[],
            )

        found_certificate_id = found_certificate.get("id")
        if not found_certificate_id:
            self.module.fail_json(
                changed=False, msg=f"Certificate {self.name} ID not found"
            )

        try:
            self.client.certificates.delete(certificate_id=found_certificate_id)
            self.module.exit_json(
                changed=True,
                msg=f"Certificate {self.name} deleted",
                certificate=found_certificate,
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
            self.module.fail_json(changed=False, msg=error_message, error=error)


def main():
    """The main function."""
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        dns_names=dict(type="list", elements="str", required=False),
        private_key=dict(type="str", required=False, no_log=True),
        leaf_certificate=dict(type="str", required=False),
        certificate_chain=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=(
            ("dns_names", "private_key"),
            ("dns_names", "leaf_certificate"),
            ("dns_names", "certificate_chain"),
        ),
        required_one_of=(("dns_names", "private_key"),),
        required_by={
            "private_key": "leaf_certificate",
        },
    )
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

    Certificates(module)


if __name__ == "__main__":
    main()
