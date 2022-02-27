#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: digital_ocean_domain_record_info
author:
  "Adam Papai (@woohgit)"
  - Mark Mercado (@mamercad)
version_added: 1.16.0
short_description: Gather information about DigitalOcean domain records
description:
  - Gather information about DigitalOcean domain records
options:
  state:
    description:
     - Indicate desired state of the target.
    default: present
    choices: [ present ]
    type: str
  record_id:
    description:
      - Used to retrieve a specific record.
    type: int
  domain:
    description:
     - Name of the domain.
    required: true
    type: str
    aliases: [ name, domain_name ]
  type:
    description:
     - The type of record you would like to retrieve.
    choices: [ A, AAAA, CNAME, MX, TXT, SRV, NS, CAA ]
    type: str
  oauth_token:
    description:
     - DigitalOcean OAuth token. Can be specified in C(DO_API_KEY), C(DO_API_TOKEN), or C(DO_OAUTH_TOKEN) environment variables
    aliases: ['API_TOKEN']
    type: str

notes:
  - Version 2 of DigitalOcean API is used.
  - The number of requests that can be made through the API is currently limited to 5,000 per hour per OAuth token.
"""

EXAMPLES = """
- name: Retrieve all domain records for example.com
  community.digitalocean.digital_ocean_domain_record_info:
    state: present
    oauth_token: xxxx
    domain: example.com

- name: Get specific domain record by ID
  community.digitalocean.digital_ocean_domain_record_info:
    state: present
    oauth_token: xxxx
    record_id: 12345789
  register: result

- name: Retrieve all A domain records for example.com
  community.digitalocean.digital_ocean_domain_record_info:
    state: present
    oauth_token: xxxx
    domain: example.com
    type: A
"""

RETURN = r"""
data:
  description: list of DigitalOcean domain records
  returned: success
  type: list
  elements: dict
  sample:
    - data: ns1.digitalocean.com
      flags: null
      id: 296972269
      name: '@'
      port: null
      priority: null
      tag: null
      ttl: 1800
      type: NS
      weight: null
"""


from ansible.module_utils.basic import env_fallback
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.digitalocean.plugins.module_utils.digital_ocean import (
    DigitalOceanHelper,
)


class DigitalOceanDomainRecordManager(DigitalOceanHelper, object):
    def __init__(self, module):
        super(DigitalOceanDomainRecordManager, self).__init__(module)
        self.module = module
        self.domain = module.params.get("domain").lower()
        self.records = self.__get_all_records()
        self.payload = self.__build_payload()
        self.force_update = module.params.get("force_update", False)
        self.record_id = module.params.get("record_id", None)
        self.records_by_id = self.__find_record_by_id(self.record_id)

    def check_credentials(self):
        # Check if oauth_token is valid or not
        response = self.get("account")
        if response.status_code == 401:
            self.module.fail_json(
                msg="Failed to login using oauth_token, please verify validity of oauth_token"
            )

    def __get_all_records(self):

        records = []
        page = 1
        while True:
            # GET /v2/domains/$DOMAIN_NAME/records
            type = self.module.params.get("type")
            if type:
                response = self.get(
                    "domains/%(domain)s/records?type=%(type)s&page=%(page)s"
                    % {"domain": self.domain, "type": type, "page": page}
                )
            else:
                response = self.get(
                    "domains/%(domain)s/records?page=%(page)s"
                    % {"domain": self.domain, "page": page}
                )
            status_code = response.status_code
            json = response.json

            if status_code != 200:
                self.module.exit_json(
                    msg="Error getting domain records [%(status_code)s: %(json)s]"
                    % {"status_code": status_code, "json": json}
                )

            for record in json["domain_records"]:
                records.append(dict([(str(k), v) for k, v in record.items()]))

            if "pages" in json["links"] and "next" in json["links"]["pages"]:
                page += 1
            else:
                break

        return records

    def get_records(self):
        return False, self.records

    def get_records_by_id(self):
        if self.records_by_id:
            return False, [self.records_by_id]
        else:
            return False, []

    def __find_record_by_id(self, record_id):
        for record in self.records:
            if record["id"] == record_id:
                return record
        return None

    def __build_payload(self):

        payload = dict(
            data=self.module.params.get("data"),
            flags=self.module.params.get("flags"),
            name=self.module.params.get("name"),
            port=self.module.params.get("port"),
            priority=self.module.params.get("priority"),
            type=self.module.params.get("type"),
            tag=self.module.params.get("tag"),
            ttl=self.module.params.get("ttl"),
            weight=self.module.params.get("weight"),
        )

        # DigitalOcean stores every data in lowercase except TXT
        if payload["type"] != "TXT" and payload["data"]:
            payload["data"] = payload["data"].lower()

        # digitalocean stores data: '@' if the data=domain
        if payload["data"] == self.domain:
            payload["data"] = "@"

        return payload


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=["present"], default="present"),
            oauth_token=dict(
                aliases=["API_TOKEN"],
                no_log=True,
                fallback=(
                    env_fallback,
                    ["DO_API_TOKEN", "DO_API_KEY", "DO_OAUTH_TOKEN"],
                ),
            ),
            record_id=dict(type="int"),
            domain=dict(type="str", aliases=["name", "domain_name"], required=True),
            type=dict(
                type="str",
                choices=["A", "AAAA", "CNAME", "MX", "TXT", "SRV", "NS", "CAA"],
            ),
        ),
    )

    manager = DigitalOceanDomainRecordManager(module)

    # verify credentials and domain
    manager.check_credentials()

    state = module.params.get("state")
    record_id = module.params.get("record_id")

    if state == "present":
        if record_id:
            changed, result = manager.get_records_by_id()
        else:
            changed, result = manager.get_records()
    elif state == "absent":
        changed, result = manager.delete_record()

    module.exit_json(changed=changed, data={"records": result})


if __name__ == "__main__":
    main()
