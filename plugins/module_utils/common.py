# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import env_fallback
from ansible.module_utils.six.moves.urllib.parse import urlparse, parse_qs

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


class DigitalOceanFunctions:
    @staticmethod
    def get_paginated(module, obj, meth, key, exc, params=None):
        results = []
        page = 1
        paginated = True
        while paginated:
            try:
                fn = getattr(obj, meth)
                resp = fn(
                    per_page=DigitalOceanConstants.PAGE_SIZE, page=page, params=params
                )
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

    @staticmethod
    def get_volumes_by_region(module, client, region):
        volumes = DigitalOceanFunctions.get_paginated(
            module=module,
            obj=client.volumes,
            meth="list",
            key="volumes",
            params=None,
            exc=HttpResponseError,
        )
        found_volumes = []
        for volume in volumes:
            volume_region = volume["region"]["slug"]
            if volume_region == region:
                found_volumes.append(volume)
        return found_volumes

    @staticmethod
    def get_droplets_by_region(module, client, region):
        droplets = DigitalOceanFunctions.get_paginated(
            module=module,
            obj=client.droplets,
            meth="list",
            key="droplets",
            params=None,
            exc=HttpResponseError,
        )
        found_droplets = []
        for droplet in droplets:
            droplet_region = droplet["region"]["slug"]
            if droplet_region == region:
                found_droplets.append(droplet)
        return found_droplets

    @staticmethod
    def get_droplet_by_name_in_region(module, client, region, name):
        droplets = DigitalOceanFunctions.get_paginated(
            module=module,
            obj=client.droplets,
            meth="list",
            key="droplets",
            params=None,
            exc=HttpResponseError,
        )
        found_droplets = []
        for droplet in droplets:
            droplet_region = droplet["region"]["slug"]
            if droplet_region == region:
                if name == droplet["name"]:
                    found_droplets.append(droplet)
        return found_droplets

    @staticmethod
    def get_volume_by_name_in_region(module, client, region, name):
        volumes = DigitalOceanFunctions.get_paginated(
            module=module,
            obj=client.volumes,
            meth="list",
            key="volumes",
            params=None,
            exc=HttpResponseError,
        )
        found_volumes = []
        for volume in volumes:
            volume_region = volume["region"]["slug"]
            if volume_region == region:
                if name == volume["name"]:
                    found_volumes.append(volume)
        return found_volumes


class DigitalOceanConstants:
    PAGE_SIZE = 10
    SLEEP = 10


class DigitalOceanOptions:
    @staticmethod
    def argument_spec():
        return dict(
            state=dict(
                type="str",
                choices=["present", "absent"],
                default="present",
            ),
            timeout=dict(
                type="int",
                default=300,  # 5 minutes
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
