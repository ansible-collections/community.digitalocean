#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: monitoring_alert_policy

short_description: Create or delete monitoring alert policy

version_added: 2.0.0

description:
  - Create or delete monitoring alert policy.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Monitoring).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  alerts:
    description:
      - Alert object.
    type: dict
    required: true
  compare:
    description:
      - Comparision.
    type: str
    required: true
    choices: ["GreaterThan", "LessThan"]
  description:
    description:
      - Description.
    type: str
    required: true
  enabled:
    description:
      - Enabled.
    type: bool
    required: true
  entities:
    description:
      - Entities.
    type: list
    elements: str
    required: true
  tags:
    description:
      - Tags.
    type: list
    elements: str
    required: true
  type:
    description:
      - Type.
    type: str
    required: true
    choices:
      - "v1/insights/droplet/load_1"
      - "v1/insights/droplet/load_5"
      - "v1/insights/droplet/load_15"
      - "v1/insights/droplet/memory_utilization_percent"
      - "v1/insights/droplet/disk_utilization_percent"
      - "v1/insights/droplet/cpu"
      - "v1/insights/droplet/disk_read"
      - "v1/insights/droplet/disk_write"
      - "v1/insights/droplet/public_outbound_bandwidth"
      - "v1/insights/droplet/public_inbound_bandwidth"
      - "v1/insights/droplet/private_outbound_bandwidth"
      - "v1/insights/droplet/private_inbound_bandwidth"
      - "v1/insights/lbaas/avg_cpu_utilization_percent"
      - "v1/insights/lbaas/connection_utilization_percent"
      - "v1/insights/lbaas/droplet_health"
      - "v1/insights/lbaas/tls_connections_per_second_utilization_percent"
      - "v1/insights/lbaas/increase_in_http_error_rate_percentage_5xx"
      - "v1/insights/lbaas/increase_in_http_error_rate_percentage_4xx"
      - "v1/insights/lbaas/increase_in_http_error_rate_count_5xx"
      - "v1/insights/lbaas/increase_in_http_error_rate_count_4xx"
      - "v1/insights/lbaas/high_http_request_response_time"
      - "v1/insights/lbaas/high_http_request_response_time_50p"
      - "v1/insights/lbaas/high_http_request_response_time_95p"
      - "v1/insights/lbaas/high_http_request_response_time_99p"
      - "v1/dbaas/alerts/load_15_alerts"
      - "v1/dbaas/alerts/memory_utilization_alerts"
      - "v1/dbaas/alerts/disk_utilization_alerts"
      - "v1/dbaas/alerts/cpu_alerts"
  value:
    description:
      - Value.
    type: float
    required: true
  window:
    description:
      - Window.
    type: str
    required: true
    choices: ["5m", "10m", "30m", "1h"]

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create monitoring alert policy
  community.digitalocean.monitoring_alert_policy:
    token: "{{ token }}"
    state: present
    alerts:
      email:
        - bob@example.com
      slack:
        - channel: Production Alerts
          url: https://hooks.slack.com/services/T1234567/AAAAAAAA/ZZZZZZ
    compare: GreaterThan
    description: CPU Alert
    enabled: true
    entities:
      - 192018292
    tags:
      - droplet_tag
    type: v1/insights/droplet/cpu
    value: 80
    window: 5m
"""


RETURN = r"""
alerts:
  description: Monitoring alert policy information.
  returned: always
  type: dict
  sample:
    alerts:
      email:
        - bob@exmaple.com
      slack:
        - channel: Production Alerts
          url: https://hooks.slack.com/services/T1234567/AAAAAAAA/ZZZZZZ
    compare: GreaterThan
    description: CPU Alert
    enabled: true
    entities:
      - '192018292'
    tags:
      - droplet_tag
    type: v1/insights/droplet/cpu
    value: 80
    window: 5m
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Monitoring alert policy result information.
  returned: always
  type: str
  sample:
    - Created redis database cluster backend (9cc10173-e9ea-4176-9dbc-a4cee4c4ff30) in nyc3
    - Deleted redis database cluster backend (9cc10173-e9ea-4176-9dbc-a4cee4c4ff30) in nyc3
    - redis database cluster backend in nyc3 would be created
    - redis database cluster backend (9cc10173-e9ea-4176-9dbc-a4cee4c4ff30) in nyc3 exists
    - redis database cluster backend in nyc3 does not exist
    - redis database cluster backend (9cc10173-e9ea-4176-9dbc-a4cee4c4ff30) would be deleted
"""

import time
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


class MonitoringAlertPolicy:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.alerts = module.params.get("alerts")
        self.compare = module.params.get("compare")
        self.description = module.params.get("description")
        self.enabled = module.params.get("enabled")
        self.entities = module.params.get("entities")
        self.tags = module.params.get("tags")
        self.type = module.params.get("type")
        self.value = module.params.get("value")
        self.window = module.params.get("window")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_monitoring_alert_policies(self):
        try:
            monitoring_alert_policies = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.monitoring,
                meth="list_alert_policy",
                key="policies",
                exc=HttpResponseError,
            )
            # raise RuntimeError(monitoring_alert_policies)
            found_monitoring_alert_policies = []
            for monitoring_alert_policy in monitoring_alert_policies:
                if (
                    self.alerts == monitoring_alert_policy["alerts"]
                    and self.compare == monitoring_alert_policy["compare"]
                    # TODO: Description not being set
                    # and self.description == monitoring_alert_policy["description"]
                    and self.enabled == monitoring_alert_policy["enabled"]
                    and self.entities == monitoring_alert_policy["entities"]
                    and self.tags == monitoring_alert_policy["tags"]
                    and self.type == monitoring_alert_policy["type"]
                    and self.value == monitoring_alert_policy["value"]
                    and self.window == monitoring_alert_policy["window"]
                ):
                    found_monitoring_alert_policies.append(monitoring_alert_policy)
            return found_monitoring_alert_policies
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
                policy=[],
            )

    # def get_kubernetes_cluster_by_id(self, id):
    #     try:
    #         kubernetes_cluster = self.client.kubernetes.get_cluster(cluster_id=id)[
    #             "kubernetes_cluster"
    #         ]
    #         return kubernetes_cluster
    #     except HttpResponseError as err:
    #         error = {
    #             "Message": err.error.message,
    #             "Status Code": err.status_code,
    #             "Reason": err.reason,
    #         }
    #         self.module.fail_json(
    #             changed=False,
    #             msg=error.get("Message"),
    #             error=error,
    #             kubernetes_cluster=[],
    #         )

    def create_monitoring_alert_policy(self):
        try:
            body = {
                "alerts": self.alerts,
                "compare": self.compare,
                "desciption": self.description,
                "enabled": self.enabled,
                "entities": self.entities,
                "tags": self.tags,
                "type": self.type,
                "value": self.value,
                "window": self.window,
            }
            policy = self.client.monitoring.create_alert_policy(body=body)["policy"]
            self.module.exit_json(
                changed=True,
                msg=f"Created monitoring alert policy {self.description} ({policy['uuid']})",
                policy=policy,
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
                policy=[],
            )

    def delete_monitoring_alert_policy(self, policy):
        try:
            self.client.monitoring.delete_alert_policy(alert_uuid=policy["uuid"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted monitoring alert policy {self.description} ({policy['uuid']})",
                policy=policy,
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
                policy=[],
            )

    def present(self):
        monitoring_alert_policies = self.get_monitoring_alert_policies()
        if len(monitoring_alert_policies) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Monitoring alert policy {self.description} would be created",
                    policy=[],
                )
            else:
                self.create_monitoring_alert_policy()
        elif len(monitoring_alert_policies) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Monitoring alert policy {self.description} ({monitoring_alert_policies[0]['uuid']}) exists",
                policy=monitoring_alert_policies[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(monitoring_alert_policies)} monitoring alert policies described {self.description}",
                policy=[],
            )

    def absent(self):
        monitoring_alert_policies = self.get_monitoring_alert_policies()
        if len(monitoring_alert_policies) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"Monitoring alert policy {self.description} does not exist",
                policy=[],
            )
        elif len(monitoring_alert_policies) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Monitoring alert policy {self.description} ({monitoring_alert_policies[0]['uuid']}) would be deleted",
                    policy=monitoring_alert_policies[0],
                )
            else:
                self.delete_monitoring_alert_policy(policy=monitoring_alert_policies[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(monitoring_alert_policies)} monitoring alert policies described {self.description}",
                policy=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        alerts=dict(type="dict", required=True),
        compare=dict(type="str", choices=["GreaterThan", "LessThan"], required=True),
        description=dict(type="str", required=True),
        enabled=dict(type="bool", required=True),
        entities=dict(type="list", elements="str", required=True),
        tags=dict(type="list", elements="str", required=True),
        type=dict(
            type="str",
            choices=[
                "v1/insights/droplet/load_1",
                "v1/insights/droplet/load_5",
                "v1/insights/droplet/load_15",
                "v1/insights/droplet/memory_utilization_percent",
                "v1/insights/droplet/disk_utilization_percent",
                "v1/insights/droplet/cpu",
                "v1/insights/droplet/disk_read",
                "v1/insights/droplet/disk_write",
                "v1/insights/droplet/public_outbound_bandwidth",
                "v1/insights/droplet/public_inbound_bandwidth",
                "v1/insights/droplet/private_outbound_bandwidth",
                "v1/insights/droplet/private_inbound_bandwidth",
                "v1/insights/lbaas/avg_cpu_utilization_percent",
                "v1/insights/lbaas/connection_utilization_percent",
                "v1/insights/lbaas/droplet_health",
                "v1/insights/lbaas/tls_connections_per_second_utilization_percent",
                "v1/insights/lbaas/increase_in_http_error_rate_percentage_5xx",
                "v1/insights/lbaas/increase_in_http_error_rate_percentage_4xx",
                "v1/insights/lbaas/increase_in_http_error_rate_count_5xx",
                "v1/insights/lbaas/increase_in_http_error_rate_count_4xx",
                "v1/insights/lbaas/high_http_request_response_time",
                "v1/insights/lbaas/high_http_request_response_time_50p",
                "v1/insights/lbaas/high_http_request_response_time_95p",
                "v1/insights/lbaas/high_http_request_response_time_99p",
                "v1/dbaas/alerts/load_15_alerts",
                "v1/dbaas/alerts/memory_utilization_alerts",
                "v1/dbaas/alerts/disk_utilization_alerts",
                "v1/dbaas/alerts/cpu_alerts",
            ],
            required=True,
        ),
        value=dict(type="float", required=True),
        window=dict(type="str", choices=["5m", "10m", "30m", "1h"], required=True),
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

    MonitoringAlertPolicy(module)


if __name__ == "__main__":
    main()
