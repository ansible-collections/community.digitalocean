#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Mark Mercado <mamercad@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: digital_ocean_load_balancer
short_description: Manage DigitalOcean Load Balancers
description:
    - Manage DigitalOcean Load Balancers
author: "Mark Mercado (@mamercad)"
options:
  oauth_token:
    description:
      - DigitalOcean OAuth token; can be specified in C(DO_API_KEY), C(DO_API_TOKEN), or C(DO_OAUTH_TOKEN) environment variables
    type: str
    aliases: ["API_TOKEN"]
    required: true
  state:
    description:
      - The usual, C(present) to create, C(absent) to destroy
    type: str
    choices: ["present", "absent"]
    default: present
  name:
    description:
      - A human-readable name for a load balancer instance.
      - Required and must be unique (current API documentation is not up-to-date for this parameter).
    type: str
    required: true
  size:
    description:
      - The size of the load balancer.
      - The available sizes are C(lb-small), C(lb-medium), or C(lb-large).
      - You can resize load balancers after creation up to once per hour.
      - You cannot resize a load balancer within the first hour of its creation.
    required: false
    type: str
    choices: ["lb-small", "lb-medium", "lb-large"]
    default: lb-small
  algorithm:
    description:
      - The load balancing algorithm used to determine which backend Droplet will be selected by a client.
      - It must be either C(round_robin) or C(least_connections).
    required: false
    choices: ["round_robin", "least_connections"]
    default: round_robin
  droplet_ids:
    description:
      - An array containing the IDs of the Droplets assigned to the load balancer.
      - Required when creating load balancers.
    required: false
    type: list
    elements: int
  region:
    description:
      - The slug identifier for the region where the resource will initially be available.
    type: str
    aliases: ["region_id"]
    default: nyc1
  forwarding_rules:
    description:
      - An array of objects specifying the forwarding rules for a load balancer.
      - Required when creating load balancers.
    required: false
    type: list
    elements: dict
    suboptions:
      entry_protocol:
        type: str
        description: Entry protocol
      entry_port:
        type: int
        description: Entry port
      target_protocol:
        type: str
        description: Target protocol
      target_port:
        type: int
        description: Target port
      certificate_id:
        type: str
        description: Certificate ID
      tls_passthrough:
        type: bool
        description: TLS passthrough
  health_check:
    description:
      - An object specifying health check settings for the load balancer.
    required: false
    type: dict
    suboptions:
      protocol:
        description: Protocol
        type: str
        required: false
        default: http
      port:
        description: Port
        type: int
        required: false
        default: 80
      path:
        description: Path
        type: str
        required: false
        default: /
      check_interval_seconds:
        description: Check interval seconds
        type: int
        required: false
        default: 10
      response_timeout_seconds:
        description: Response timeout seconds
        type: int
        required: false
        default: 5
      unhealthy_threshold:
        description: Unhealthy threshold
        type: int
        required: false
        default: 3
  sticky_sessions:
    description:
      - An object specifying sticky sessions settings for the load balancer.
    required: false
    type: dict
    suboptions:
      type:
        description: Type
        type: str
        required: false
        default: none
  redirect_http_to_https:
    description:
      - A boolean value indicating whether HTTP requests to the load balancer on port 80 will be redirected to HTTPS on port 443.
    type: bool
    required: false
    default: false
  enable_proxy_protocol:
    description:
      - A boolean value indicating whether PROXY Protocol is in use.
    type: bool
    required: false
    default: false
  enable_backend_keepalive:
    description:
      - A boolean value indicating whether HTTP keepalive connections are maintained to target Droplets.
    type: bool
    required: false
    default: false
  vpc_uuid:
    description:
      - A string specifying the UUID of the VPC to which the load balancer is assigned.
      - If unspecified, uses the default VPC in the region.
    type: str
    required: false
  wait:
    description:
      - Wait for the Load Balancer to be running before returning.
    type: bool
    required: false
    default: true
  wait_timeout:
    description:
      - How long before wait gives up, in seconds, when creating a Load Balancer.
    type: int
    default: 600
extends_documentation_fragment:
- community.digitalocean.digital_ocean.documentation
"""


EXAMPLES = r"""
- name: Create a Load Balancer
  community.digitalocean.digital_ocean_load_balancer:
    state: present
    name: test-loadbalancer-1
    droplet_ids:
      - 12345678
    region: nyc1
    forwarding_rules:
      - entry_protocol: http
        entry_port: 8080
        target_protocol: http
        target_port: 8080
        certificate_id: ""
        tls_passthrough: false
"""


RETURN = r"""
data:
  description: A DigitalOcean Load Balancer
  return: changed
  type: dict
  sample:
  data:
    load_balancer:
      algorithm: round_robin
      created_at: '2021-08-22T14:23:41Z'
      droplet_ids:
      - 261172461
      enable_backend_keepalive: false
      enable_proxy_protocol: false
      forwarding_rules:
      - certificate_id: ''
        entry_port: 8080
        entry_protocol: http
        target_port: 8080
        target_protocol: http
        tls_passthrough: false
      health_check:
        check_interval_seconds: 10
        healthy_threshold: 5
        path: /
        port: 80
        protocol: http
        response_timeout_seconds: 5
        unhealthy_threshold: 3
      id: b4fdb507-70e8-4325-a89e-d02271b93618
      ip: 159.203.150.113
      name: test-loadbalancer-1
      redirect_http_to_https: false
      region:
        available: true
        features:
        - backups
        - ipv6
        - metadata
        - install_agent
        - storage
        - image_transfer
        name: New York 3
        sizes:
        - s-1vcpu-1gb
        - s-1vcpu-1gb-amd
        - s-1vcpu-1gb-intel
        - s-1vcpu-2gb
        - s-1vcpu-2gb-amd
        - s-1vcpu-2gb-intel
        - s-2vcpu-2gb
        - s-2vcpu-2gb-amd
        - s-2vcpu-2gb-intel
        - s-2vcpu-4gb
        - s-2vcpu-4gb-amd
        - s-2vcpu-4gb-intel
        - s-4vcpu-8gb
        - c-2
        - c2-2vcpu-4gb
        - s-4vcpu-8gb-amd
        - s-4vcpu-8gb-intel
        - g-2vcpu-8gb
        - gd-2vcpu-8gb
        - s-8vcpu-16gb
        - m-2vcpu-16gb
        - c-4
        - c2-4vcpu-8gb
        - s-8vcpu-16gb-amd
        - s-8vcpu-16gb-intel
        - m3-2vcpu-16gb
        - g-4vcpu-16gb
        - so-2vcpu-16gb
        - m6-2vcpu-16gb
        - gd-4vcpu-16gb
        - so1_5-2vcpu-16gb
        - m-4vcpu-32gb
        - c-8
        - c2-8vcpu-16gb
        - m3-4vcpu-32gb
        - g-8vcpu-32gb
        - so-4vcpu-32gb
        - m6-4vcpu-32gb
        - gd-8vcpu-32gb
        - so1_5-4vcpu-32gb
        - m-8vcpu-64gb
        - c-16
        - c2-16vcpu-32gb
        - m3-8vcpu-64gb
        - g-16vcpu-64gb
        - so-8vcpu-64gb
        - m6-8vcpu-64gb
        - gd-16vcpu-64gb
        - so1_5-8vcpu-64gb
        - m-16vcpu-128gb
        - c-32
        - c2-32vcpu-64gb
        - m3-16vcpu-128gb
        - m-24vcpu-192gb
        - g-32vcpu-128gb
        - so-16vcpu-128gb
        - m6-16vcpu-128gb
        - gd-32vcpu-128gb
        - m3-24vcpu-192gb
        - g-40vcpu-160gb
        - so1_5-16vcpu-128gb
        - m-32vcpu-256gb
        - gd-40vcpu-160gb
        - so-24vcpu-192gb
        - m6-24vcpu-192gb
        - m3-32vcpu-256gb
        - so1_5-24vcpu-192gb
        - m6-32vcpu-256gb
        slug: nyc3
      size: lb-small
      status: active
      sticky_sessions:
        type: none
      tag: ''
      vpc_uuid: b8fd9a58-d93d-4329-b54a-78a397d64855
"""


import time
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.community.digitalocean.plugins.module_utils.digital_ocean import (
    DigitalOceanHelper,
)


class DOLoadBalancer(object):
    def __init__(self, module):
        self.rest = DigitalOceanHelper(module)
        self.module = module
        self.id = None
        self.name = self.module.params.get("name")
        self.updates = []
        # Pop these values so we don't include them in the POST data
        self.module.params.pop("oauth_token")
        self.wait = self.module.params.pop("wait", True)
        self.wait_timeout = self.module.params.pop("wait_timeout", 600)

    def get_by_id(self):
        """Fetch an existing DigitalOcean Load Balancer (by id)
        API reference: https://docs.digitalocean.com/reference/api/api-reference/#operation/get_load_balancer
        """
        response = self.rest.get("load_balancers/{0}".format(self.id))
        json_data = response.json
        if response.status_code == 200:
            # Found one with the given id:
            lb = json_data.get("load_balancer", None)
            if lb is not None:
                self.lb = lb
                return lb
            else:
                self.module.fail_json(msg="Unexpected error, please file a bug: get_by_id")
        return None

    def get_by_name(self):
        """Fetch all existing DigitalOcean Load Balancers
        API reference: https://docs.digitalocean.com/reference/api/api-reference/#operation/list_all_load_balancers
        """
        page = 1
        while page is not None:
            response = self.rest.get("load_balancers?page={0}".format(page))
            json_data = response.json
            if response.status_code == 200:
                for lb in json_data["load_balancers"]:
                    # Found one with the same name:
                    if lb.get("name", None) == self.name:
                        if lb is not None:
                            self.lb = lb
                            return lb
                        else:
                            self.module.fail_json(msg="Unexpected error, please file a bug: get_by_name")
                if (
                    "links" in json_data
                    and "pages" in json_data["links"]
                    and "next" in json_data["links"]["pages"]
                ):
                    page += 1
                else:
                    page = None
        return None

    def ensure_active(self):
        """Wait for the existing Load Balancer to be active"""
        end_time = time.monotonic() + self.wait_timeout
        while time.monotonic() < end_time:
            lb = self.get_by_id()
            if lb is not None:
                if lb["load_balancer"]["status"] == "active":
                    return lb
            else:
                self.module.fail_json(msg="Load Balancer {} not found".format(self.id))
            time.sleep(min(10, end_time - time.monotonic()))
        self.module.fail_json(
            msg="Timed out waiting for Load Balancer {} to be active".format(self.id)
        )

    def is_same(self, found_lb):
        """Checks if exising Load Balancer is the same as requested"""
        if self.module.params.get("droplet_ids", []) != found_lb.get("droplet_ids", []):
            self.updates.append("droplet_ids")
        found_lb_region = found_lb.get("region", None)
        if found_lb_region is not None:
            if self.module.params.get("region", None) != found_lb_region.get("slug", None):
                self.updates.append("region")
        else:
            self.module.fail_json(msg="Unexpected error, please file a bug: is_same")
        if self.module.params.get("size", None) != found_lb.get("size", None):
            self.updates.append("size")
        if self.module.params.get("algorithm", None) != found_lb.get("algorithm", None):
            self.updates.append("algorithm")

        if len(self.updates):
            return False
        else:
          return True

    def update(self):
        """Updates a DigitalOcean Load Balancer
        API reference: https://docs.digitalocean.com/reference/api/api-reference/#operation/update_load_balancer
        """
        request_params = dict(self.module.params)
        self.id = self.lb.get("id", None)
        self.name = self.lb.get("name", None)
        if self.id is not None and self.name is not None:
            response = self.rest.put("load_balancers/{0}".format(self.id), data=request_params)
            json_data = response.json
            if response.status_code == 200:
                self.module.exit_json(changed=True, msg="Load Balancer {0} ({1}) updated: {2}".format(self.name, self.id, ", ".join(self.updates)))
            else:
                self.module.fail_json(changed=False, msg="Error updating Load Balancer {0} ({1}): {2}".format(self.name, self.id, json_data["message"]))
        else:
            self.module.fail_json(msg="Unexpected error, please file a bug: update")

    def create(self):
        """Creates a DigitalOcean Load Balancer
        API reference: https://docs.digitalocean.com/reference/api/api-reference/#operation/create_load_balancer
        """

        # Check if it exists already (the API docs aren't up-to-date right now,
        # "name" is required and must be unique across the account.
        found_lb = self.get_by_name()
        if found_lb is not None:
            self.lb = found_lb
            # Do we need to update it?
            if not self.is_same(found_lb):
                self.update()
            else:
                self.module.exit_json(
                    changed=False,
                    msg="Load Balancer name {0} already exists (and needs no changes)".format(self.name)
                )

        # Create it.
        request_params = dict(self.module.params)
        response = self.rest.post("load_balancers", data=request_params)
        json_data = response.json
        if response.status_code != 202:
            self.module.fail_json(
                msg="Failed creating Load Balancer {0}: {1}".format(
                    self.name, response["message"]
                )
            )

        lb = json_data.get("load_balancer", None)
        if lb is None:
            self.module.fail_json(msg="Unexpected error, please file a bug")

        self.id = lb.get("id", None)
        if self.id is None:
            self.module.fail_json(msg="Unexpected error, please file a bug")

        if self.wait:
            json_data = self.ensure_active()

        self.module.exit_json(changed=True, data=json_data)

    def delete(self):
        """Deletes a DigitalOcean Load Balancer
        API reference: https://docs.digitalocean.com/reference/api/api-reference/#operation/delete_load_balancer
        """

        lb = self.get_by_name()
        if lb is not None:
            id = lb["id"]
            response = self.rest.delete("load_balancers/{0}".format(id))
            json_data = response.json
            if response.status_code == 204:
                self.module.exit_json(
                    changed=True,
                    msg="Load Balancer {0} ({1}) deleted".format(self.name, id),
                )
            else:
                self.module.fail_json(
                    changed=False,
                    msg="Failed to delete Load Balancer {0} ({1}) deleted: {2}".format(
                        self.name, id, json_data["message"]
                    ),
                )
        else:
            self.module.fail_json(
                changed=False, msg="Load Balancer {0} not found".format(self.name)
            )


def run(module):
    state = module.params.pop("state")
    lb = DOLoadBalancer(module)
    if state == "present":
        lb.create()
    elif state == "absent":
        lb.delete()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=["present", "absent"], default="present"),
            oauth_token=dict(
                aliases=["API_TOKEN"],
                no_log=True,
                fallback=(
                    env_fallback,
                    ["DO_API_TOKEN", "DO_API_KEY", "DO_OAUTH_TOKEN"],
                ),
                required=True,
            ),
            name=dict(type="str", required=True),
            size=dict(
                type="str",
                choices=["lb-small", "lb-medium", "lb-large"],
                required=False,
                default="lb-small",
            ),
            algorithm=dict(
                type="str",
                choices=["round_robin", "least_connections"],
                required=False,
                default="round_robin",
            ),
            droplet_ids=dict(type="list", elements="int", required=False),
            region=dict(aliases=["region_id"], default="nyc1"),
            forwarding_rules=dict(type="list", elements="dict", required=False),
            health_check=dict(type="dict", required=False),
            sticky_sessions=dict(type="dict", required=False),
            redirect_http_to_https=dict(type="bool", required=False, default=False),
            enable_proxy_protocol=dict(type="bool", required=False, default=False),
            enable_backend_keepalive=dict(type="bool", required=False, default=False),
            vpc_uuid=dict(type="str", required=False),
            wait=dict(type="bool", default=True),
            wait_timeout=dict(type="int", default=600),
        ),
        required_if=(
            [
                ("state", "present", ["droplet_ids", "forwarding_rules"]),
            ]
        ),
        supports_check_mode=True,
    )

    run(module)


if __name__ == "__main__":
    main()
