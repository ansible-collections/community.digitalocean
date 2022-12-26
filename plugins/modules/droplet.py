#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: droplet

short_description: Create or delete Droplets

version_added: 2.0.0

description:
  - Creates or deletes Droplets.
  - View the create API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/droplets_create).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - The human-readable string you wish to use when displaying the Droplet name.
      - |
        The name, if set to a domain name managed in the DigitalOcean DNS management system,
        will configure a PTR record for the Droplet.
      - |
        The name set during creation will also determine the hostname for the Droplet
        in its internal configuration.
    type: str
    required: false
  droplet_id:
    description:
      - |
        The Droplet ID which can be used for C(state=absent) when there are more than
        one Droplet with the same name within the same region
    type: int
    required: false
  region:
    description:
      - The slug identifier for the region that you wish to deploy the Droplet in.
      - |
        If the specific datacenter is not important, a slug prefix (e.g. C(nyc)) can be
        used to deploy the Droplet in any of the that region's locations (C(nyc1), C(nyc2),
        or nyc3).
      - If the region is omitted from the create request completely, the Droplet may
        deploy in any region.
    type: str
    required: false
  size:
    description:
      - The slug identifier for the size that you wish to select for this Droplet.
    type: str
    required: false
  image:
    description:
      - The image ID of a public or private image or the slug identifier for a public image.
      - This image will be the base image for your Droplet.
    type: str
    required: false
  ssh_keys:
    description:
      - |
        An array containing the IDs or fingerprints of the SSH keys that you wish to embed
        in the Droplet's root account upon creation.
    type: list
    required: false
    default: []
  backups:
    description:
      - A boolean indicating whether automated backups should be enabled for the Droplet.
    type: bool
    required: false
    default: false
  ipv6:
    description:
      - A boolean indicating whether to enable IPv6 on the Droplet.
    type: bool
    required: false
    default: false
  monitoring:
    description:
      - A boolean indicating whether to install the DigitalOcean agent for monitoring.
    type: bool
    required: false
    default: false
  tags:
    description:
      - A flat array of tag names as strings to apply to the Droplet after it is created.
      - Tag names can either be existing or new tags.
    type: list
    required: false
    default: []
  volumes:
    description:
      - |
        An array of IDs for block storage volumes that will be attached to the Droplet
        once created.
      - The volumes must not already be attached to an existing Droplet.
    type: list
    required: false
    default: []
  vpc_uuid:
    description:
      - A string specifying the UUID of the VPC to which the Droplet will be assigned.
      - If excluded, the Droplet will be assigned to your account's default VPC for the region.
    type: str
    required: false
  with_droplet_agent:
    description:
      - |
        A boolean indicating whether to install the DigitalOcean agent used for providing
        access to the Droplet web console in the control panel.
      - By default, the agent is installed on new Droplets but installation errors
        (i.e. OS not supported) are ignored.
      - To prevent it from being installed, set to C(false).
      - To make installation errors fatal, explicitly set it to C(true).
  unique_name:
    description:
      - |
        When C(true) for C(state=present) the Droplet will only be created if it is uniquely
        named in the region and the region is specified.
      - |
        When C(true) for C(state=absent) the Droplet will only be destroyed if it is uniquely
        named in the region and the region is specified.
    type: bool
    required: false
    default: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create Droplet
  community.digitalocean.droplet:
    token: "{{ token }}"
    state: present
    name: example.com
    region: nyc3
    size: s-1vcpu-1gb
    image: ubuntu-20-04-x64
"""


RETURN = r"""
droplet:
  description: Droplet information.
  returned: always
  type: dict
  sample:
    droplet:
      id: 3164444
      name: example.com
      memory: 1024
      vcpus: 1
      disk: 25
      locked: false
      status: new
      kernel:
      created_at: '2020-07-21T18:37:44Z'
      features:
      - backups
      - private_networking
      - ipv6
      - monitoring
      backup_ids: []
      next_backup_window:
      snapshot_ids: []
      image:
        id: 63663980
        name: 20.04 (LTS) x64
        distribution: Ubuntu
        slug: ubuntu-20-04-x64
        public: true
        regions:
        - ams2
        - ams3
        - blr1
        - fra1
        - lon1
        - nyc1
        - nyc2
        - nyc3
        - sfo1
        - sfo2
        - sfo3
        - sgp1
        - tor1
        created_at: '2020-05-15T05:47:50Z'
        type: snapshot
        min_disk_size: 20
        size_gigabytes: 2.36
        description: ''
        tags: []
        status: available
        error_message: ''
      volume_ids: []
      size:
        slug: s-1vcpu-1gb
        memory: 1024
        vcpus: 1
        disk: 25
        transfer: 1
        price_monthly: 5
        price_hourly: 0.00743999984115362
        regions:
        - ams2
        - ams3
        - blr1
        - fra1
        - lon1
        - nyc1
        - nyc2
        - nyc3
        - sfo1
        - sfo2
        - sfo3
        - sgp1
        - tor1
        available: true
        description: Basic
      size_slug: s-1vcpu-1gb
      networks:
        v4: []
        v6: []
      region:
        name: New York 3
        slug: nyc3
        features:
        - private_networking
        - backups
        - ipv6
        - metadata
        - install_agent
        - storage
        - image_transfer
        available: true
        sizes:
        - s-1vcpu-1gb
        - s-1vcpu-2gb
        - s-1vcpu-3gb
        - s-2vcpu-2gb
        - s-3vcpu-1gb
        - s-2vcpu-4gb
        - s-4vcpu-8gb
        - s-6vcpu-16gb
        - s-8vcpu-32gb
        - s-12vcpu-48gb
        - s-16vcpu-64gb
        - s-20vcpu-96gb
        - s-24vcpu-128gb
        - s-32vcpu-192g
      tags:
      - web
      - env:prod
    links:
      actions:
      - id: 7515
        rel: create
        href: https://api.digitalocean.com/v2/actions/7515
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
    - Created Droplet example.com (11223344) in nyc3
    - Deleted Droplet example.com (11223344) in nyc3
    - Droplet example.com in nyc3 would be created
    - Droplet example.com (11223344) in nyc3 exists
    - 'There are currently 2 Droplets named example.com in nyc3: 11223344, 55667788'
    - Droplet example.com in nyc3 would be created
    - Droplet example.com not found
    - Droplet example.com (11223344) in nyc3 would be deleted
    - Must provide droplet_id when deleting Droplets without unique_name
    - Droplet with ID 11223344 not found
    - Droplet with ID 11223344 would be deleted
"""

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


class Droplet:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.name = module.params.get("name")
        self.droplet_id = module.params.get("droplet_id")
        self.region = module.params.get("region")
        self.size = module.params.get("size")
        self.image = module.params.get("image")
        self.ssh_keys = module.params.get("ssh_keys")
        self.backups = module.params.get("backups")
        self.ipv6 = module.params.get("ipv6")
        self.monitoring = module.params.get("monitoring")
        self.tags = module.params.get("tags")
        self.volumes = module.params.get("volumes")
        self.vpc_uuid = module.params.get("vpc_uuid")
        self.with_droplet_agent = module.params.get("with_droplet_agent")
        self.unique_name = module.params.get("unique_name")
        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_droplets_by_name_and_region(self):
        droplets = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.droplets,
            meth="list",
            key="droplets",
            params=dict(name=self.name),
            exc=HttpResponseError,
        )
        # NOTE: DigitalOcean Droplet names are not unique!
        found_droplets = []
        for droplet in droplets:
            droplet_name = droplet.get("name")
            if droplet_name == self.name:
                droplet_region = droplet.get("region")
                if droplet_region:
                    droplet_region_slug = droplet_region.get("slug")
                    if droplet_region_slug == self.region:
                        found_droplets.append(droplet)
        return found_droplets

    def get_droplet_by_id(self):
        return self.client.droplets.get(droplet_id=self.droplet_id)

    def create_droplet(self):
        try:
            body = {
                "name": self.name,
                "region": self.region,
                "size": self.size,
                "image": self.image,
                "ssh_keys": self.ssh_keys,
                "backups": self.backups,
                "ipv6": self.ipv6,
                "monitoring": self.monitoring,
                "tags": self.tags,
                "volumes": self.volumes,
                "vpc_uuid": self.vpc_uuid,
                "with_droplet_agent": self.with_droplet_agent,
            }
            droplet = self.client.droplets.create(body=body)["droplet"]
            self.module.exit_json(
                changed=True,
                msg=f"Created Droplet {droplet['name']} ({droplet['id']}) in {droplet['region']['slug']}",
                droplet=droplet,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, droplet=[]
            )

    def delete_droplet(self, droplet):
        try:
            self.client.droplets.destroy(droplet_id=droplet["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted Droplet {droplet['name']} ({droplet['id']}) in {droplet['region']['slug']}",
                droplet=droplet,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, droplet=[]
            )

    def present(self):
        if self.unique_name:
            droplets = self.get_droplets_by_name_and_region()
            if len(droplets) == 0:
                if self.module.check_mode:
                    self.module.exit_json(
                        changed=True,
                        msg=f"Droplet {self.name} in {self.region} would be created",
                        droplet=[],
                    )
                else:
                    self.create_droplet()
            elif len(droplets) == 1:
                self.module.exit_json(
                    changed=False,
                    msg=f"Droplet {self.name} ({droplets[0]['id']}) in {self.region} exists",
                    droplet=droplets[0],
                )
            elif len(droplets) > 1:
                droplet_ids = ", ".join([str(droplet["id"]) for droplet in droplets])
                self.module.fail_json(
                    changed=False,
                    msg=f"There are currently {len(droplets)} Droplets named {self.name} in {self.region}: {droplet_ids}",
                    droplet=[],
                )
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Droplet {self.name} in {self.region} would be created",
                droplet=[],
            )
        else:
            self.create_droplet()

    def absent(self):
        if self.unique_name:
            droplets = self.get_droplets_by_name_and_region()
            if len(droplets) == 0:
                if self.module.check_mode:
                    self.module.exit_json(
                        changed=False,
                        msg=f"Droplet {self.name} in {self.region} not found",
                        droplet=[],
                    )
                else:
                    self.module.fail_json(
                        changed=False,
                        msg=f"Droplet {self.name} in {self.region} not found",
                        droplet=[],
                    )
            elif len(droplets) == 1:
                if self.module.check_mode:
                    self.module.exit_json(
                        changed=True,
                        msg=f"Droplet {self.name} ({droplets[0]['id']}) in {self.region} would be deleted",
                        droplet=droplets[0],
                    )
                else:
                    self.delete_droplet(droplets[0])
            elif len(droplets) > 1:
                droplet_ids = ", ".join([str(droplet["id"]) for droplet in droplets])
                self.module.fail_json(
                    changed=False,
                    msg=f"There are currently {len(droplets)} Droplets named {self.name} in {self.region}: {droplet_ids}",
                    droplet=[],
                )

        if not self.droplet_id:
            self.module.fail_json(
                changed=False,
                msg="Must provide droplet_id when deleting Droplets without unique_name",
                droplet=[],
            )

        droplet = self.get_droplet_by_id()
        if not droplet:
            self.module.fail_json(
                changed=False,
                msg=f"Droplet with ID {self.droplet_id} not found",
                droplet=[],
            )
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Droplet with ID {self.droplet_id} would be deleted",
                droplet=droplet,
            )
        else:
            self.delete_droplet(droplet)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        droplet_id=dict(type="int", required=False),
        region=dict(type="str", required=False),
        size=dict(type="str", required=False),
        image=dict(type="str", required=False),
        ssh_keys=dict(type="list", required=False, default=[]),
        backups=dict(type="bool", required=False, default=False),
        ipv6=dict(type="bool", required=False, default=False),
        monitoring=dict(type="bool", required=False, default=False),
        tags=dict(type="list", required=False, default=[]),
        volumes=dict(type="list", required=False, default=[]),
        vpc_uuid=dict(type="str", required=False),
        with_droplet_agent=dict(type="bool", required=False, default=False),
        unique_name=dict(type="bool", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "present", ("name", "size", "image")),
        ],
        required_by={
            "unique_name": "region",
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

    Droplet(module)


if __name__ == "__main__":
    main()
