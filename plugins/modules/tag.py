#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: tag

short_description: Create or delete tags

version_added: 2.0.0

description:
  - Create or delete tags.
  - |
    A tag is a label that can be applied to a resource (currently Droplets, Images, Volumes,
    Volume Snapshots, and Database clusters) in order to better organize or facilitate the
    lookups and actions on it.
  - View the create API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Tags).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - The name of the tag.
      - Tags may contain letters, numbers, colons, dashes, and underscores.
      - There is a limit of 255 characters per tag.
      - |
        Note: Tag names are case stable, which means the capitalization you use when you first
        create a tag is canonical.
      - When working with tags in the API, you must use the tag's canonical capitalization.
      - Tagged resources in the control panel will always display the canonical capitalization.
      - |
        For example, if you create a tag named "PROD", you can tag resources in the control panel
        by entering "prod". The tag will still display with its canonical capitalization, "PROD".
    type: str
    required: true

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create tag
  community.digitalocean.tag:
    token: "{{ token }}"
    state: present
    name: extra-awesome
"""


RETURN = r"""
tag:
  description: Tag information.
  returned: always
  type: dict
  sample:
    name: extra-awesome
    resources:
      count: 0
      databases:
        count: 0
      droplets:
        count: 0
      images:
        count: 0
      volume_snapshots:
        count: 0
      volumes:
        count: 0
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
    - Created tag extra-awesome
    - Deleted tag extra-awesome
    - Tag extra-awesome would be created
    - Tag extra-awesome exists
    - Tag extra-awesome does not exist
    - Tag extra-awesome deleted
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


class Tag:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.name = module.params.get("name")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_tags(self):
        try:
            tags = self.client.tags.list()["tags"]
            found_tags = []
            for tag in tags:
                if self.name == tag["name"]:
                    found_tags.append(tag)
            return found_tags
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
                tag=[],
            )

    def create_tag(self):
        try:
            body = {
                "name": self.name,
            }
            tag = self.client.tags.create(body=body)["tag"]

            self.module.exit_json(
                changed=True,
                msg=f"Created tag {self.name}",
                tag=tag,
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

    def delete_tag(self, tag):
        try:
            self.client.tags.delete(tag_id=tag["name"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted tag {self.name}",
                tag=tag,
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
                database=[],
            )

    def present(self):
        tags = self.get_tags()
        if len(tags) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Tag {self.name} would be created",
                    tag=[],
                )
            else:
                self.create_tag()
        elif len(tags) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Tag {self.name} exists",
                tag=tags[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(tags)} named {self.name}",
                tag=[],
            )

    def absent(self):
        tags = self.get_tags()
        if len(tags) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"Tag {self.name} does not exist",
                tag=[],
            )
        elif len(tags) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Tag {self.name} would be deleted",
                    tag=tags[0],
                )
            else:
                self.delete_tag(tag=tags[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(tags)} tags named {self.name}",
                database=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
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

    Tag(module)


if __name__ == "__main__":
    main()
