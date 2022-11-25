# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import env_fallback
from ansible.module_utils.six.moves.urllib.parse import urlparse, parse_qs


class DigitalOceanFunctions:
    @staticmethod
    def get_next_page(links):
        """
        "links": {
            "pages": {
                "last": "https://api.digitalocean.com/v2/images?page=2",
                "next": "https://api.digitalocean.com/v2/images?page=2"
            }
        }
        """
        pages = links.get("pages")
        if pages:
            next_page = pages.get("next")
            if next_page:
                parsed_url = urlparse(next_page)
                if parsed_url:
                    if hasattr(parsed_url, "query"):
                        query = parsed_url.query
                        if query:
                            page_list = parse_qs(parsed_url.query).get("page")
                            if type(page_list) is list:
                                if len(page_list) == 1:
                                    return page_list[0]
        return None


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
