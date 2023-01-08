#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: database_cluster

short_description: Create or delete database clusters

version_added: 2.0.0

description:
  - Create or delete database clusters.
  - |
    DigitalOcean's managed database service simplifies the creation and management of highly
    javailable database clusters.
  - Currently, it offers support for PostgreSQL, Redis, MySQL, and MongoDB.
  - Database clusters may be deployed in a multi-node, high-availability configuration.
  - |
    If your machine type is above the basic nodes, your node plan is above the smallest option,
    or you are running MongoDB, you may additionally include up to two standby nodes in your
    cluster.
  - |
    The size of individual nodes in a database cluster is represented by a human-readable slug,
    which is used in some of the following requests.
  - Each slug denotes the node's identifier, CPU count, and amount of RAM, in that order.
  - View the create API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Databases).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - A unique, human-readable name referring to a database cluster.
    type: str
    required: true
  engine:
    description:
      - A slug representing the database engine used for the cluster.
      - |
        The possible values are "pg" for PostgreSQL, "mysql" for MySQL, "redis" for Redis,
        and "mongodb" for MongoDB.
    type: str
    choices: [pg, mysql, redis, mongodb]
    required: true
  version:
    description:
      - A string representing the version of the database engine in use for the cluster.
    type: str
    required: false
  num_nodes:
    description:
      - The number of nodes in the database cluster.
    type: int
    default: 1
  size:
    description:
      - The slug identifier representing the size of the nodes in the database cluster.
    type: str
    required: true
  region:
    description:
      - The slug identifier for the region where the database cluster is located.
    type: str
    required: true
  private_network_uuid:
    description:
      - A string specifying the UUID of the VPC to which the database cluster will be assigned.
      - |
        If excluded, the cluster when creating a new database cluster, it will be assigned to your
        account's default VPC for the region.
    type: str
    required: false
  tags:
    description:
      - An array of tags that have been applied to the database cluster.
    type: list
    elements: str
    required: false
  project_id:
    description:
      - The ID of the project that the database cluster is assigned to.
      - |
        If excluded when creating a new database cluster, it will be assigned to your default
        project.
    type: str
    required: false
  rules:
    description:
      - Array of objects (firewall_rule)
    type: list
    elements: dict
    required: false
  backup_restore:
    description:
      - Object (database_backup)
    type: dict
    required: false

extends_documentation_fragment:
  - community.digitalocean.common.documentation
"""


EXAMPLES = r"""
- name: Create Postgres database cluster
  community.digitalocean.database_cluster:
    token: "{{ token }}"
    state: present
    name: backend
    region: nyc3
    type: pg
    num_nodes: 2
    size: db-s-2vcpu-4gb
"""


RETURN = r"""
database:
  description: Database information.
  returned: always
  type: dict
  sample:
    id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    name: backend
    engine: pg
    version: '14'
    connection:
      uri: 'postgres://doadmin:wv78n3zpz42xezdk@backend-do-user-19081923-0.db.ondigitalocean.com:25060/defaultdb?sslmode=require'
      database: ''
      host: backend-do-user-19081923-0.db.ondigitalocean.com
      port: 25060
      user: doadmin
      password: wv78n3zpz42xezdk
      ssl: true
    private_connection:
      uri: 'postgres://doadmin:wv78n3zpz42xezdk@private-backend-do-user-19081923-0.db.ondigitalocean.com:25060/defaultdb?sslmode=require'
      database: ''
      host: private-backend-do-user-19081923-0.db.ondigitalocean.com
      port: 25060
      user: doadmin
      password: wv78n3zpz42xezdk
      ssl: true
    users:
      - name: doadmin
        role: primary
        password: wv78n3zpz42xezdk
    db_names:
      - defaultdb
    num_nodes: 2
    region: nyc3
    status: creating
    created_at: '2019-01-11T18:37:36Z'
    maintenance_window:
      day: saturday
      hour: '08:45:12'
      pending: true
      description:
        - Update TimescaleDB to version 1.2.1
        - Upgrade to PostgreSQL 11.2 and 10.7 bugfix releases
    size: db-s-2vcpu-4gb
    tags:
      - production
    private_network_uuid: d455e75d-4858-4eec-8c95-da2f0a5f93a7
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
    DigitalOceanConstants,
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


class DatabaseCluster:
    def __init__(self, module):
        self.module = module
        self.client = Client(token=module.params.get("token"))
        self.state = module.params.get("state")
        self.timeout = module.params.get("timeout")
        self.name = module.params.get("name")
        self.engine = module.params.get("engine")
        self.version = module.params.get("version")
        self.num_nodes = module.params.get("num_nodes")
        self.size = module.params.get("size")
        self.region = module.params.get("region")
        self.private_network_uuid = module.params.get("private_network_uuid")
        self.tags = module.params.get("tags")
        self.project_id = module.params.get("project_id")
        self.rules = module.params.get("rules")
        self.backup_restore = module.params.get("backup_restore")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_database_clusters_by_name_and_region(self):
        try:
            databases = self.client.databases.list_clusters()["databases"]
            found_databases = []
            for database_cluster in databases:
                if self.name == database_cluster["name"]:
                    if self.engine == database_cluster["engine"]:
                        if self.region == database_cluster["region"]:
                            found_databases.append(database_cluster)
            return found_databases
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

    def get_database_cluster_by_id(self, id):
        try:
            database = self.client.databases.get_cluster(database_cluster_uuid=id)[
                "database"
            ]
            return database
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

    def create_database_cluster(self):
        try:
            body = {
                "name": self.name,
                "engine": self.engine,
                "version": self.version,
                "num_nodes": self.num_nodes,
                "size": self.size,
                "region": self.region,
                "private_network_uuid": self.private_network_uuid,
                "tags": self.tags,
                "project_id": self.project_id,
                "rules": self.rules,
                "backup_restore": self.backup_restore,
            }
            database = self.client.databases.create_cluster(body=body)["database"]

            status = database["status"]
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time and status != "online":
                time.sleep(DigitalOceanConstants.SLEEP)
                status = self.get_database_cluster_by_id(database["id"])["status"]

            self.module.exit_json(
                changed=True,
                msg=f"Created {self.engine} database cluster {self.name} ({database['id']}) in {self.region}",
                database=database,
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

    def delete_database_cluster(self, database):
        try:
            self.client.databases.destroy_cluster(database_cluster_uuid=database["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted {self.engine} database cluster {self.name} ({database['id']}) in {self.region}",
                database=database,
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
        database_clusters = self.get_database_clusters_by_name_and_region()
        if len(database_clusters) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"{self.engine} database cluster {self.name} in {self.region} would be created",
                    database=[],
                )
            else:
                self.create_database_cluster()
        elif len(database_clusters) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"{self.engine} database cluster {self.name} ({database_clusters[0]['id']}) in {self.region} exists",
                database=database_clusters[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(database_clusters)} {self.engine} database clusters named {self.name} in {self.region}",
                database=[],
            )

    def absent(self):
        database_clusters = self.get_database_clusters_by_name_and_region()
        if len(database_clusters) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"{self.engine} database cluster {self.name} in {self.region} does not exist",
                database=[],
            )
        elif len(database_clusters) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"{self.engine} database cluster {self.name} ({database_clusters[0]['id']}) in {self.region} would be deleted",
                    database=database_clusters[0],
                )
            else:
                self.delete_database_cluster(database=database_clusters[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(database_clusters)} {self.engine} database clusters named {self.name} in {self.region}",
                database=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        engine=dict(
            type="str", choices=["pg", "mysql", "redis", "mongodb"], required=True
        ),
        version=dict(type="str", required=False),
        num_nodes=dict(type="int", default=1),
        size=dict(type="str", required=True),
        region=dict(type="str", required=True),
        private_network_uuid=dict(type="str", required=False),
        tags=dict(type="list", elements="str", required=False),
        project_id=dict(type="str", required=False),
        rules=dict(type="list", elements="dict", required=False),
        backup_restore=dict(type="dict", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "present", ("size",))],
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

    DatabaseCluster(module)


if __name__ == "__main__":
    main()
