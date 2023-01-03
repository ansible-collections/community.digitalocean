#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: domain_record

short_description: Manage domain records

version_added: 2.0.0

description:
  - |
    Domain record resources are used to set or retrieve information about the individual DNS
    records configured for a domain.
  - |
    This allows you to build and manage DNS zone files by adding and modifying individual records
    for a domain.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Domain-Records).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  type:
    description:
      - The type of the DNS record.
    choices: [A, AAAA, CAA, CNAME, MX, NS, SOA, SRV, TXT]
    type: str
    required: true
  domain_name:
    description:
      - The domain name.
    type: str
    required: true
  name:
    description:
      - The host name, alias, or service being defined by the record.
    type: str
    required: true
  data:
    description:
      - Variable data depending on record type.
      - |
        For example, the "data" value for an A record would be the IPv4 address to which the
        domain will be mapped.
      - |
        For a CAA record, it would contain the domain name of the CA being granted permission to
        issue certificates.
    type: str
    required: true
  priority:
    description:
      - The priority for SRV and MX records.
    type: int
    required: false
  port:
    description:
      - The port for SRV records.
    type: int
    required: false
  ttl:
    description:
      - This value is the time to live for the record, in seconds.
      - |
        This defines the time frame that clients can cache queried information before a refresh
        kshould be requested.
    type: int
    required: false
  weight:
    description:
      - The weight for SRV records.
    type: int
    required: false
  flags:
    description:
      - An unsigned integer between 0-255 used for CAA records.
    type: int
    required: false
  tag:
    description:
      - The parameter tag for CAA records.
    choices: [issue, issuewild, iodef]
    type: str
    required: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create domain A record
  community.digitalocean.domain_record:
    token: "{{ token }}"
    domain_name: example.com
    type: A
    name: www
    data: 192.168.100.50
"""


RETURN = r"""
domain_record:
  description: Domain record.
  returned: always
  type: dict
  sample:
    domain_record:
      id: 28448433
      type: A
      name: www.example.com
      data: 192.168.100.50
      priority: null
      port: null
      ttl: 1800
      weight: null
      flags: null
      tag: null
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Domain record result information.
  returned: always
  type: str
  sample:
    - Created domain record www A in example.com
    - Deleted domain record www A in example.com
    - Domain record www A exists in example.com
    - Domain record www A would be created in example.com
    - Domain record www A would be deleted from example.com
    - Domain record www A does not exist in example.com
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


class DomainRecord:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.domain_name = module.params.get("domain_name")
        self.type = module.params.get("type")
        self.name = module.params.get("name")
        self.data = module.params.get("data")
        self.priority = module.params.get("priority")
        self.port = module.params.get("port")
        self.ttl = module.params.get("ttl")
        self.weight = module.params.get("weight")
        self.flags = module.params.get("flags")
        self.tag = module.params.get("tag")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_domain_record_by_name_and_type(self):
        try:
            domain_records = self.client.domains.list_records(
                domain_name=self.domain_name,
                type=self.type,
                name=f"{self.name}.{self.domain_name}",
            )
            for domain_record in domain_records["domain_records"]:
                if domain_record["data"] == self.data:
                    return domain_record
            return None
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, domain=[]
            )

    def create_domain_record(self):
        try:
            body = dict(
                type=self.type,
                name=self.name,
                data=self.data,
                priority=self.priority,
                port=self.port,
                ttl=self.ttl,
                weight=self.weight,
                flags=self.flags,
                tag=self.tag,
            )
            domain_record = self.client.domains.create_record(
                domain_name=self.domain_name, body=body
            ).get("domain_record", {})
            self.module.exit_json(
                changed=True,
                msg=f"Created domain record {self.name} {self.type} in {self.domain_name}",
                domain_record=domain_record,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, domain_record={}
            )

    def delete_domain_record(self, domain_record):
        try:
            self.client.domains.delete_record(
                domain_name=self.domain_name, domain_record_id=domain_record["id"],
            )
            self.module.exit_json(
                changed=True,
                msg=f"Deleted domain record {self.name} {self.type} ({domain_record['id']}) in {self.domain_name}",
                domain_record=domain_record,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, domain_record={}
            )

    def present(self):
        """Creates or updates a domain."""
        found_domain_record = self.get_domain_record_by_name_and_type()
        if self.module.check_mode:
            if found_domain_record:
                self.module.exit_json(
                    changed=False,
                    msg=f"Domain record {self.name} {self.type} exists in {self.domain_name}",
                    domain_record=found_domain_record,
                )
            else:
                self.module.exit_json(
                    changed=True,
                    msg=f"Domain record {self.name} {self.type} would be created in {self.domain_name}",
                    domain_record={},
                )
        if found_domain_record:
            self.module.exit_json(
                changed=False,
                msg=f"Domain record {self.name} {self.type} exists in {self.domain_name}",
                domain_record=found_domain_record,
            )
        else:
            self.create_domain_record()

    def absent(self):
        """Removes a domain."""
        found_domain_record = self.get_domain_record_by_name_and_type()
        if self.module.check_mode:
            if found_domain_record:
                self.module.exit_json(
                    changed=True,
                    msg=f"Domain record {self.name} {self.type} ({found_domain_record['id']}) would be deleted from {self.domain_name}",
                    domain_record=found_domain_record,
                )
            else:
                self.module.exit_json(
                    changed=False,
                    msg=f"Domain record {self.name} {self.type} does not exist in {self.domain_name}",
                    domain_record={},
                )
        if found_domain_record:
            self.delete_domain_record(found_domain_record)
        else:
            self.module.exit_json(
                changed=False,
                msg=f"Domain record {self.name} {self.type} does not exist in {self.domain_name}",
                domain_record=found_domain_record,
            )


def main():
    """The main function."""
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        domain_name=dict(type="str", required=True),
        type=dict(
            type="str",
            choices=["A", "AAAA", "CAA", "CNAME", "MX", "NS", "SOA", "SRV", "TXT"],
            required=True,
        ),
        name=dict(type="str", required=True),
        data=dict(type="str", required=True),
        priority=dict(type="int", required=False),
        port=dict(type="int", required=False),
        ttl=dict(type="int", required=False),
        weight=dict(type="int", required=False),
        flags=dict(type="int", required=False),
        tag=dict(type="str", choices=["issue", "issuewild", "iodef"], required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
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

    DomainRecord(module)


if __name__ == "__main__":
    main()
