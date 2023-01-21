#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: project

short_description: Create or delete projects

version_added: 2.0.0

description:
  - Create or delete projects.
  - Projects allow you to organize your resources into groups that fit the way you work.
  - |
    You can group resources (like Droplets, Spaces, load balancers, domains, and floating IPs)
    in ways that align with the applications you host on DigitalOcean.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Projects).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - The human-readable name for the project.
      - The maximum length is 175 characters and the name must be unique.
    type: str
    required: true
  description:
    description:
      - The description of the project. The maximum length is 255 characters.
    type: str
    required: false
  purpose:
    description:
      - The purpose of the project.
      - The maximum length is 255 characters.
      - |
        It can have one of the following values: "Just trying out DigitalOcean",
        "Class project / Educational purposes", "Website or blog", "Web Application",
        "Service or API", "Mobile Application", "Machine learning / AI / Data processing",
        "IoT", "Operational / Developer tooling".
      - |
        If another value for purpose is specified, for example, "your custom purpose",
        your purpose will be stored as C(Other: your custom purpose).
    type: str
    required: false
  environment:
    description:
      - The environment of the project's resources.
    type: str
    required: false
    choices: ["Development", "Staging", "Production"]

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create a project
  community.digitalocean.project:
    token: "{{ token }}"
    state: present
    name: my-web-api
    description: My Website API
    purpose: Service or API
    environment: Production
"""


RETURN = r"""
project:
  description: Project information.
  returned: always
  type: dict
  sample:
    id: 4e1bfbc3-dc3e-41f2-a18f-1b4d7ba71679
    owner_uuid: 99525febec065ca37b2ffe4f852fd2b2581895e7
    owner_id: 258992
    name: my-web-api
    description: My website API
    purpose: Service or API
    environment: Production
    created_at: '2018-09-27T20:10:35Z'
    updated_at: '2018-09-27T20:10:35Z'
    is_default: false
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
    - Created project my-website-api (9cc10173-e9ea-4176-9dbc-a4cee4c4ff30)
    - Deleted project my-website-api (9cc10173-e9ea-4176-9dbc-a4cee4c4ff30)
    - Project my-website-api would be created
    - Project my-website-api (9cc10173-e9ea-4176-9dbc-a4cee4c4ff30) exists
    - Project my-website-api does not exist
    - Project my-website-api (9cc10173-e9ea-4176-9dbc-a4cee4c4ff30) would be deleted
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


class Project:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.name = module.params.get("name")
        self.description = module.params.get("description")
        self.purpose = module.params.get("purpose")
        self.environment = module.params.get("environment")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_projects(self):
        try:
            projects = self.client.projects.list()["projects"]
            found_projects = []
            for project in projects:
                if self.name == project["name"]:
                    found_projects.append(project)
            return found_projects
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
                project=[],
            )

    def create_project(self):
        try:
            body = {
                "name": self.name,
                "description": self.description,
                "purpose": self.purpose,
                "environment": self.environment,
            }
            project = self.client.projects.create(body=body)["project"]

            self.module.exit_json(
                changed=True,
                msg=f"Created project {self.name} ({project['id']})",
                project=project,
            )
        except HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, project=[]
            )

    def delete_project(self, project):
        try:
            self.client.projects.delete(project_id=project["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted project {self.name} ({project['id']})",
                project=project,
            )
        except HttpResponseError as err:
            # TODO: Not sure where to file this bug yet
            raise RuntimeError(err)
            # RuntimeError: Operation returned an invalid status 'Unsupported Media Type'
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                project=[],
            )

    def present(self):
        projects = self.get_projects()
        if len(projects) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Project {self.name} would be created",
                    project=[],
                )
            else:
                self.create_project()
        elif len(projects) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Project {self.name} ({projects[0]['id']}) exists",
                project=projects[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(projects)} projects named {self.name}",
                project=[],
            )

    def absent(self):
        projects = self.get_projects()
        if len(projects) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"Project {self.name} does not exist",
                project=[],
            )
        elif len(projects) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Project {self.name} ({projects[0]['id']}) would be deleted",
                    project=projects[0],
                )
            else:
                self.delete_project(project=projects[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(projects)} projects named {self.name}",
                project=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        purpose=dict(type="str", required=False),
        environment=dict(
            type="str", choices=["Development", "Staging", "Production"], required=False
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "present", ("purpose",)),
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

    Project(module)


if __name__ == "__main__":
    main()
