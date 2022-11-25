# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import env_fallback


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
