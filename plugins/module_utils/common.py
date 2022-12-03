# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import env_fallback
from ansible.module_utils.six.moves.urllib.parse import urlparse, parse_qs


class DigitalOceanFunctions:
    @staticmethod
    def get_paginated(module, obj, meth, key, exc):
        results = []
        page = 1
        paginated = True
        while paginated:
            try:
                fn = getattr(obj, meth)
                resp = fn(per_page=DigitalOceanConstants.PAGE_SIZE, page=page)
                if key:
                    results.extend(resp.get(key))
                else:
                    results.extend(resp)
                links = resp.get("links")
                if links:
                    pages = links.get("pages")
                    if pages:
                        next_page = pages.get("next")
                        if next_page:
                            parsed_url = urlparse(pages["next"])
                            page = parse_qs(parsed_url.query)["page"][0]
                        else:
                            paginated = False
                    else:
                        paginated = False
                else:
                    paginated = False
            except exc as err:
                error = {
                    "Message": err.error.message,
                    "Status Code": err.status_code,
                    "Reason": err.reason,
                }
                module.fail_json(changed=False, msg=error.get("Message"), error=error)
        return results


class DigitalOceanConstants:
    PAGE_SIZE = 10


class DigitalOceanOptions:
    @staticmethod
    def argument_spec():
        return dict(
            state=dict(
                type="str",
                choices=["present", "absent"],
                default="present",
            ),
            token=dict(
                type="str",
                fallback=(
                    env_fallback,
                    [
                        "DIGITALOCEAN_TOKEN",
                        "DO_API_TOKEN",
                        "DO_API_KEY",
                        "DO_OAUTH_TOKEN",
                        "OAUTH_TOKEN",
                    ],
                ),
                no_log=True,
                required=False,
                aliases=["oauth_token", "api_token"],
            ),
        )
