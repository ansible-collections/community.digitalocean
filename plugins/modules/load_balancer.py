#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: load_balancer

short_description: Create or delete load balancers

version_added: 2.0.0

description:
  - Create or delete load balancers.
  - DigitalOcean Load Balancers provide a way to distribute traffic across multiple Droplets.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Load-Balancers).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  droplet_ids:
    description:
      - An array containing the IDs of the Droplets assigned to the load balancer.
    type: list
    elements: int
    required: false
  region:
    description:
      - The slug identifier for the region where the resource will initially be available.
    choices: ["ams1", "ams2", "ams3", "blr1", "fra1", "lon1", "nyc1", "nyc2", "nyc3", "sfo1", "sfo2", "sfo3", "sgp1", "tor1"]
    type: str
    required: true
  name:
    description:
      - A human-readable name for a load balancer instance.
    type: str
    required: false
  project_id:
    description:
      - The ID of the project that the load balancer is associated with.
      - |
        If no ID is provided at creation, the load balancer associates with the user's default
        project.
      - If an invalid project ID is provided, the load balancer will not be created.
    type: str
    required: false
  size_unit:
    description:
      - How many nodes the load balancer contains.
      - Each additional node increases the load balancer's ability to manage more connections.
      - |
        Load balancers can be scaled up or down, and you can change the number of nodes after creation up to once
        per hour.
      - This field is currently not available in the AMS2, NYC2, or SFO1 regions.
      - Use the size field to scale load balancers that reside in these regions.
    type: int
    default: 1
    required: false
  size:
    description:
      - Deprecated.
      - |
        This field has been replaced by the size_unit field for all regions except in AMS2, NYC2,
        and SFO1.
      - Each available load balancer size now equates to the load balancer having a set number of nodes.
      - C(lb-small) = 1 node, C(lb-medium) = 3 nodes, C(lb-large) = 6 nodes.
    type: str
    default: lb-small
    choices: ["lb-small", "lb-medium", "lb-large"]
    required: false
  forwarding_rules:
    description:
      - An array of objects specifying the forwarding rules for a load balancer.
    type: list
    elements: dict
    required: false
  health_checks:
    description:
      - An object specifying health check settings for the load balancer.
    type: dict
    required: false
  sticky_sessions:
    description:
      - An object specifying sticky sessions settings for the load balancer.
    type: dict
    required: false
  redirect_http_to_https:
    description:
      - |
        A boolean value indicating whether HTTP requests to the load balancer on port 80 will
        be redirected to HTTPS on port 443.
    type: bool
    default: false
    required: false
  enable_proxy_protocol:
    description:
      - A boolean value indicating whether PROXY Protocol is in use.
    type: bool
    default: false
    required: false
  enable_backend_keepalive:
    description:
      - |
        A boolean value indicating whether HTTP keepalive connections are maintained to target
        Droplets.
    type: bool
    default: false
    required: false
  http_idle_timeout_seconds:
    description:
      - An integer value which configures the idle timeout for HTTP requests to the target droplets.
    type: int
    default: 60
    required: false
  vpc_uuid:
    description:
      - A string specifying the UUID of the VPC to which the load balancer is assigned.
    type: str
    required: false
  disable_lets_encrypt_dns_records:
    description:
      - |
        A boolean value indicating whether to disable automatic DNS record creation for
        Let's Encrypt certificates that are added to the load balancer.
    type: bool
    default: false
    required: false
  firewall:
    description:
      - An object specifying allow and deny rules to control traffic to the load balancer.
    type: dict
    required: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create load balancer
  community.digitalocean.load_balancer:
    token: "{{ token }}"
    state: present
    name: example-lb1
    region: nyc3
    forwarding_rules:
      - entry_protocol: http
        entry_port: 80
        target_protocol: http
        target_port: 80
      - entry_protocol: https
        entry_port: 443
        target_protocol: https
        target_port: 443
        tls_passthrough: true
    droplet_ids:
      - 11223344
    disable_lets_encrypt_dns_records: true
    http_idle_timeout_seconds: 60
    firewall:
      deny:
        - cidr:1.2.0.0/16
        - ip:2.3.4.5
      allow:
        - ip:1.2.3.4
        - cidr:2.3.4.0/24
"""


RETURN = r"""
load_balancer:
  description: Load balancer information.
  returned: always
  type: dict
  sample:
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Droplet result information.
  returned: always
  type: str
  sample:
    - Created load balancer example-lb-01 (e23647ff-4b57-4da0-8f31-72616d932c0d)
    - Deleted load balancer example-lb-01 (e23647ff-4b57-4da0-8f31-72616d932c0d)
    - Load balancer example-lb-01 would be created
    - Load balancer example-lb-01 (e23647ff-4b57-4da0-8f31-72616d932c0d) exists
    - Load balancer example-lb-01 does not exist
    - Load balancer example-lb-01 (e23647ff-4b57-4da0-8f31-72616d932c0d) would be deleted
"""

import time
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.digitalocean.plugins.module_utils.common import (
    DigitalOceanOptions,
    DigitalOceanConstants,
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


class LoadBalancer:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.timeout = module.params.get("timeout")
        self.droplet_ids = module.params.get("droplet_ids")
        self.region = module.params.get("region")
        self.name = module.params.get("name")
        self.project_id = module.params.get("project_id")
        self.size_unit = module.params.get("size_unit")
        self.size = module.params.get("size")
        self.forwarding_rules = module.params.get("forwarding_rules")
        self.health_check = module.params.get("health_check")
        self.sticky_sessions = module.params.get("sticky_sessions")
        self.redirect_http_to_https = module.params.get("redirect_http_to_https")
        self.enable_proxy_protocol = module.params.get("enable_proxy_protocol")
        self.enable_backend_keepalive = module.params.get("enable_backend_keepalive")
        self.http_idle_timeout_seconds = module.params.get("http_idle_timeout_seconds")
        self.vpc_uuid = module.params.get("vpc_uuid")
        self.disable_lets_encrypt_dns_records = module.params.get(
            "disable_lets_encrypt_dns_records"
        )
        self.firewall = module.params.get("firewall")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_load_balancers(self):
        try:
            load_balancers = self.client.load_balancers.list()["load_balancers"]
            found_load_balancers = []
            for load_balancer in load_balancers:
                if self.name == load_balancer["name"]:
                    if self.region == load_balancer["region"]["slug"]:
                        found_load_balancers.append(load_balancer)
            return found_load_balancers
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                load_balancer=[],
            )

    def get_load_balancer_by_id(self, id):
        try:
            load_balancer = self.client.load_balancers.get(lb_id=id)["load_balancer"]
            return load_balancer
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                load_balancer=[],
            )

    def create_load_balancer(self):
        try:
            body = {
                "droplet_ids": self.droplet_ids,
                "region": self.region,
                "name": self.name,
                "project_id": self.project_id,
                "forwarding_rules": self.forwarding_rules,
                "health_check": self.health_check,
                "sticky_sessions": self.sticky_sessions,
                "redirect_http_to_https": self.redirect_http_to_https,
                "enable_proxy_protocol": self.enable_proxy_protocol,
                "enable_backend_keepalive": self.enable_backend_keepalive,
                "http_idle_timeout_seconds": self.http_idle_timeout_seconds,
                "vpc_uuid": self.vpc_uuid,
                "disable_lets_encrypt_dns_records": self.disable_lets_encrypt_dns_records,
                "firewall": self.firewall,
            }

            if self.region in ("ams2", "nyc2", "sfo1"):
                body.update(dict(size=self.size))
            else:
                body.update(dict(size_unit=self.size_unit))

            load_balancer = self.client.load_balancers.create(body=body)[
                "load_balancer"
            ]

            status = load_balancer["status"]
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time and (
                status != "active" or status != "new"
            ):
                time.sleep(DigitalOceanConstants.SLEEP)
                status = self.get_load_balancer_by_id(load_balancer["id"])["status"]

            self.module.exit_json(
                changed=True,
                msg=f"Created load balancer {self.name} ({load_balancer['id']})",
                load_balancer=load_balancer,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, load_balancer=[]
            )

    def delete_load_balancer(self, load_balancer):
        try:
            self.client.load_balancers.delete(lb_id=load_balancer["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted load balancer {self.name} ({load_balancer['id']})",
                load_balancer=load_balancer,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                load_balancer=[],
            )

    def present(self):
        load_balancers = self.get_load_balancers()
        if len(load_balancers) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Load balancer {self.name} would be created",
                    load_balancer=[],
                )
            else:
                self.create_load_balancer()
        elif len(load_balancers) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Load balance {self.name} ({load_balancers[0]['id']}) exists",
                load_balancer=load_balancers[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(load_balancers)} load balancers named {self.name}",
                load_balancer=[],
            )

    def absent(self):
        load_balancers = self.get_load_balancers()
        if len(load_balancers) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"Load balancer {self.name} does not exist",
                load_balancer=[],
            )
        elif len(load_balancers) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Load balancer {self.name} ({load_balancers[0]['id']}) would be deleted",
                    load_balancer=load_balancers[0],
                )
            else:
                self.delete_load_balancer(load_balancer=load_balancers[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(load_balancers)} load balancers named {self.name}",
                load_balancer=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        droplet_ids=dict(type="list", elements="int", required=False),
        region=dict(
            type="str",
            choices=[
                "ams1",
                "ams2",
                "ams3",
                "blr1",
                "fra1",
                "lon1",
                "nyc1",
                "nyc2",
                "nyc3",
                "sfo1",
                "sfo2",
                "sfo3",
                "sgp1",
                "tor1",
            ],
            required=True,
        ),
        name=dict(type="str", required=False),
        project_id=dict(type="str", required=False),
        size_unit=dict(type="int", default=1, required=False),
        size=dict(
            type="str",
            choices=["lb-small", "lb-medium", "lb-large"],
            default="lb-small",
            required=False,
        ),
        forwarding_rules=dict(type="list", elements="dict", required=False),
        health_checks=dict(type="dict", required=False),
        sticky_sessions=dict(type="dict", required=False),
        redirect_http_to_https=dict(type="bool", default=False, required=False),
        enable_proxy_protocol=dict(type="bool", default=False, required=False),
        enable_backend_keepalive=dict(type="bool", default=False, required=False),
        http_idle_timeout_seconds=dict(type="int", default=60, required=False),
        vpc_uuid=dict(type="str", required=False),
        disable_lets_encrypt_dns_records=dict(
            type="bool", default=False, required=False
        ),
        firewall=dict(type="dict", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "present", ("droplet_ids", "forwarding_rules")),
        ],
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

    LoadBalancer(module)


if __name__ == "__main__":
    main()
