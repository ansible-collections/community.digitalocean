# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c), Ansible Project 2017
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import os
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback


class Response(object):
    def __init__(self, resp, info):
        self.body = None
        if resp:
            self.body = resp.read()
        self.info = info

    @property
    def json(self):
        if not self.body:
            if "body" in self.info:
                return json.loads(to_text(self.info["body"]))
            return None
        try:
            return json.loads(to_text(self.body))
        except ValueError:
            return None

    @property
    def status_code(self):
        return self.info["status"]


class DigitalOceanHelper:
    def __init__(self, module):
        self.module = module
        self.baseurl = "https://api.digitalocean.com/v2"
        self.timeout = module.params.get("timeout", 30)
        self.oauth_token = module.params.get("oauth_token")
        self.headers = {
            "Authorization": "Bearer {0}".format(self.oauth_token),
            "Content-type": "application/json",
        }

        # Check if api_token is valid or not
        response = self.get("account")
        if response.status_code == 401:
            self.module.fail_json(
                msg="Failed to login using API token, please verify validity of API token."
            )

    def _url_builder(self, path):
        if path[0] == "/":
            path = path[1:]
        return "%s/%s" % (self.baseurl, path)

    def send(self, method, path, data=None):
        url = self._url_builder(path)
        data = self.module.jsonify(data)

        if method == "DELETE":
            if data == "null":
                data = None

        resp, info = fetch_url(
            self.module,
            url,
            data=data,
            headers=self.headers,
            method=method,
            timeout=self.timeout,
        )

        return Response(resp, info)

    def get(self, path, data=None):
        return self.send("GET", path, data)

    def put(self, path, data=None):
        return self.send("PUT", path, data)

    def post(self, path, data=None):
        return self.send("POST", path, data)

    def delete(self, path, data=None):
        return self.send("DELETE", path, data)

    @staticmethod
    def digital_ocean_argument_spec():
        return dict(
            validate_certs=dict(type="bool", required=False, default=True),
            oauth_token=dict(
                no_log=True,
                # Support environment variable for DigitalOcean OAuth Token
                fallback=(
                    env_fallback,
                    ["DO_API_TOKEN", "DO_API_KEY", "DO_OAUTH_TOKEN", "OAUTH_TOKEN"],
                ),
                required=False,
                aliases=["api_token"],
            ),
            timeout=dict(type="int", default=30),
        )

    def get_paginated_data(
        self,
        base_url=None,
        data_key_name=None,
        data_per_page=40,
        expected_status_code=200,
    ):
        """
        Function to get all paginated data from given URL
        Args:
            base_url: Base URL to get data from
            data_key_name: Name of data key value
            data_per_page: Number results per page (Default: 40)
            expected_status_code: Expected returned code from DigitalOcean (Default: 200)
        Returns: List of data

        """
        page = 1
        has_next = True
        ret_data = []
        status_code = None
        response = None
        while has_next or status_code != expected_status_code:
            required_url = "{0}page={1}&per_page={2}".format(
                base_url, page, data_per_page
            )
            response = self.get(required_url)
            status_code = response.status_code
            # stop if any error during pagination
            if status_code != expected_status_code:
                break
            page += 1
            ret_data.extend(response.json[data_key_name])
            try:
                has_next = (
                    "pages" in response.json["links"]
                    and "next" in response.json["links"]["pages"]
                )
            except KeyError:
                # There's a bug in the API docs: GET v2/cdn/endpoints doesn't return a "links" key
                has_next = False

        if status_code != expected_status_code:
            msg = "Failed to fetch %s from %s" % (data_key_name, base_url)
            if response:
                msg += " due to error : %s" % response.json["message"]
            self.module.fail_json(msg=msg)

        return ret_data


class DigitalOceanProjects:

    def __init__(self, module, rest):
        self.module = module
        self.rest = rest
        self.get_all_projects()
        # self.projects = self.rest.get_paginated_data(base_url="projects?", data_key_name="projects")
        # [{'id': 'c296b5ec-fb4d-423a-bcb2-20362a3e64f5', 'owner_uuid': '6559a5d2646ac0956dec5379d04fec698b6ea13a', 'owner_id': 3097135, 'name': 'mamercad', 'description': 'Update your project information under Settings', 'purpose': '', 'environment': '', 'is_default': True, 'created_at': '2019-07-28T20:43:15Z', 'updated_at': '2019-07-28T20:43:15Z'}]
        # raise Exception("got here")

    def get_all_projects(self):
        self.projects = self.rest.get_paginated_data(base_url="projects?", data_key_name="projects")

    def get_default(self):
        project = [project for project in self.projects if project.get("is_default", False)]
        if len(project) == 0:
            self.module.fail_json(msg="Unexpected error; no default project found")
        if len(project) > 1:
            self.module.fail_json(msg="Unexpected error; more than one default project")
        return project[0]

    def get_by_id(self, id):
        project = [project for project in self.projects if project.get("id") == id]
        if len(project) == 0:
            self.module.fail_json(msg="No project with id {0} found".format(id))
        elif len(project) > 1:
            self.module.fail_json(msg="Unexpected error; more than one project with the same id")
        return project[0]

    def get_by_name(self, name):
        project = [project for project in self.projects if project.get("name") == name]
        if len(project) == 0:
            self.module.fail_json(msg="No project with name {0} found".format(name))
        elif len(project) > 1:
            self.module.fail_json(msg="Unexpected error; more than one project with the same name")
        return project[0]

    def assign_to_project(self, project_name, urn):
        # urn e.g. do:volume:volume-id

        project = self.get_by_name(project_name)
        if project == {}:
            self.module.fail_json(msg="No project named {0} found".format(project_name))

        project_id = project.get("id", None)
        if project_id is None:
            self.module.fail_json(msg="Unexpected error; missing project id for {0}".format(project_name))

        data = { "resources": [urn] }
        response = self.rest.post("projects/{0}/resources".format(project_id), data=data)
        status = response.status_code
        json = response.json
        if status != 200:
            self.module.fail_json(msg="Unable to assign resource to project: {0}".format(json["message"]))
