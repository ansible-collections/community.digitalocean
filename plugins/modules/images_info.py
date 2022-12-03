#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: images_info

short_description: List all of the images available on your account

version_added: 2.0.0

description:
  - List all of the images available on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/images_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  type:
    description: Filters results based on image type.
    type: str
    required: false
    choices: [ application, distribution ]
  private:
    description: Used to filter only user images.
    type: bool
    required: false
  tag_name:
    description: Used to filter images by a specific tag.
    type: str
    required: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Get images
  community.digitalocean.images_info:
    token: "{{ token }}"
"""


RETURN = r"""
images:
  description: Images.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 7555620
      name: Nifty New Snapshot
      distribution: Ubuntu
      slug: null
      public: false
      regions: []
      created_at: '2014-11-04T22:23:02Z'
      type: snapshot
      min_disk_size: 20
      size_gigabytes: 2.34
      description: ''
      tags: []
      status: available
      error_message: ''
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: User cannot enable a cdn for a space they do not own.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Images result information.
  returned: always
  type: str
  sample:
    - Current Droplets
    - No Droplets
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.six.moves.urllib.parse import urlparse, parse_qs
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


class ImagesInformation:
    def __init__(self, module):
        """Class constructor."""
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.type = module.params.get("type")
        self.private = module.params.get("private")
        self.tag_name = module.params.get("tag_name")
        self.params = {}
        if self.type:
            self.params.update(dict(type=self.type))
        if self.private:
            self.params.update(dict(private=self.private))
        if self.tag_name:
            self.params.update(dict(tag_name=self.tag_name))
        if self.state == "present":
            self.present()

    def present(self):
        images = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.images,
            meth="list",
            key="images",
            exc=HttpResponseError,
            params=self.params,
        )
        if images:
            self.module.exit_json(
                changed=False,
                msg="Current images",
                images=images,
            )
        self.module.exit_json(changed=False, msg="No images", images=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        type=dict(type="str", choices=["application", "distribution"], required=False),
        private=dict(type="bool", required=False),
        tag_name=dict(type="str", required=False),
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

    ImagesInformation(module)


if __name__ == "__main__":
    main()
