# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright: (c) Ansible Project 2017
# Copyright: (c) DigitalOcean 2022
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
from logging import raiseExceptions

__metaclass__ = type

import json
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback


class DigitalOceanBaseModule(object):
    def __init__(self, module):
        self.api = DigitalOceanAPI(module)

    @staticmethod
    def argument_spec():
        return dict(
            state=dict(choices=["present", "absent"], default="present"),
            baseurl=dict(
                type="str",
                required=False,
                default=DigitalOceanAPI.baseurl,
            ),
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
                return json.loads(to_text(self.info.get("body")))
            return None
        try:
            return json.loads(to_text(self.body))
        except ValueError:
            return None

    @property
    def status_code(self):
        return self.info.get("status")


class DigitalOceanAPI(object):
    baseurl = "https://api.digitalocean.com/v2"

    def __init__(self, module):
        self.module = module
        self.baseurl = module.params.get("baseurl", DigitalOceanAPI.baseurl)
        self.timeout = module.params.get("timeout", 30)
        self.oauth_token = module.params.get("oauth_token")
        self.headers = {
            "Authorization": "Bearer {0}".format(self.oauth_token),
            "Content-type": "application/json",
        }

        # Verify OAuth token
        response = self.get("account")
        if response.status_code == 401:
            self.module.fail_json(
                changed=False,
                msg="Failed to login using OAuth token",
            )

    def _url_builder(self, path):
        if path[0] == "/":
            path = path[1:]
        return "{0}/{1}".format(self.baseurl, path)

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

            # Stop if any error during pagination
            if status_code != expected_status_code:
                break
            page += 1
            ret_data.extend(response.json[data_key_name])

            # Are there more pages?
            links = response.json.get("links")
            if links:
                pages = links.get("pages")
                if pages:
                    next = pages.get("next")
                    has_next = True
                else:
                    has_next = False
            else:
                has_next = False

        if status_code != expected_status_code:
            msg = "Failed to fetch {0} from {1}".format(data_key_name, base_url)
            if response:
                msg += " due to error: {0}".format(response.json.get("message"))
            self.module.fail_json(msg=msg)

        return ret_data
