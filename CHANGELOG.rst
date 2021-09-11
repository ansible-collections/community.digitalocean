====================================
Community DigitalOcean Release Notes
====================================

.. contents:: Topics


v1.10.0
=======

Minor Changes
-------------

- digital_ocean_kubernetes - adding the C(taints), C(auto_scale), C(min_nodes) and C(max_nodes) parameters to the C(node_pools) definition (https://github.com/ansible-collections/community.digitalocean/issues/157).

Bugfixes
--------

- digital_ocean_block_storage - fix block volumes detach idempotency (https://github.com/ansible-collections/community.digitalocean/issues/149).
- digital_ocean_droplet - ensure "active" state before issuing "power on" action (https://github.com/ansible-collections/community.digitalocean/issues/150)
- digital_ocean_droplet - power on should poll/wait, resize should support "active" state (https://github.com/ansible-collections/community.digitalocean/pull/143).
- digital_ocean_load_balancer - C(droplet_ids) are not required when C(state=absent) is chosen (https://github.com/ansible-collections/community.digitalocean/pull/147).
- digital_ocean_load_balancer - when C(state=absent) is chosen the API returns an empty response (https://github.com/ansible-collections/community.digitalocean/pull/147).

New Modules
-----------

- digital_ocean_cdn_endpoints - Create and delete DigitalOcean CDN Endpoints
- digital_ocean_cdn_endpoints_info - Gather information about DigitalOcean CDN Endpoints
- digital_ocean_load_balancer - Manage DigitalOcean Load Balancers
- digital_ocean_monitoring_alerts - Create and delete DigitalOcean Monitoring alerts
- digital_ocean_monitoring_alerts_info - Gather information about DigitalOcean Monitoring alerts

v1.9.0
======

Minor Changes
-------------

- digital_ocean - running and enforcing psf/black in the codebase (https://github.com/ansible-collections/community.digitalocean/issues/136).
- digital_ocean_floating_ip_info - new integration test for the `digital_ocean_floating_ip_info` module (https://github.com/ansible-collections/community.digitalocean/issues/130).

Bugfixes
--------

- digital_ocean_database - increase the database creation integration test timeout (https://github.com/ansible-collections/community.digitalocean).
- digital_ocean_floating_ip - delete all Floating IPs initially during the integration test run (https://github.com/ansible-collections/community.digitalocean/issues/129).
- digitalocean inventory - respect the TRANSFORM_INVALID_GROUP_CHARS configuration setting (https://github.com/ansible-collections/community.digitalocean/pull/138).
- info modules - adding missing check mode support (https://github.com/ansible-collections/community.digitalocean/issues/139).

v1.8.0
======

Minor Changes
-------------

- digital_ocean_database - add support for MongoDB (https://github.com/ansible-collections/community.digitalocean/issues/124).

Bugfixes
--------

- digital_ocean - integration tests need community.general and jmespath (https://github.com/ansible-collections/community.digitalocean/issues/121).
- digital_ocean_firewall - fixed idempotence (https://github.com/ansible-collections/community.digitalocean/issues/122).

v1.7.0
======

Minor Changes
-------------

- digital_ocean_kubernetes - set "latest" as the default version for new clusters (https://github.com/ansible-collections/community.digitalocean/issues/114).

Bugfixes
--------

- digital_ocean_certificate - fixing integration test (https://github.com/ansible-collections/community.digitalocean/issues/114).
- digital_ocean_droplet - state `present` with `wait` was not waiting (https://github.com/ansible-collections/community.digitalocean/issues/116).
- digital_ocean_firewall - fixing integration test (https://github.com/ansible-collections/community.digitalocean/issues/114).
- digital_ocean_tag - fixing integration test (https://github.com/ansible-collections/community.digitalocean/issues/114).
- digitalocean - update README.md with project_info and project module (https://github.com/ansible-collections/community.digitalocean/pull/112).

New Modules
-----------

- digital_ocean_snapshot - Create and delete DigitalOcean snapshots
- digital_ocean_vpc - Create and delete DigitalOcean VPCs
- digital_ocean_vpc_info - Gather information about DigitalOcean VPCs

v1.6.0
======

Bugfixes
--------

- digital_ocean_certificate_info - ensure return type is a list (https://github.com/ansible-collections/community.digitalocean/issues/55).
- digital_ocean_domain_info - ensure return type is a list (https://github.com/ansible-collections/community.digitalocean/issues/55).
- digital_ocean_firewall_info - ensure return type is a list (https://github.com/ansible-collections/community.digitalocean/issues/55).
- digital_ocean_load_balancer_info - ensure return type is a list (https://github.com/ansible-collections/community.digitalocean/issues/55).
- digital_ocean_tag_info - ensure return type is a list (https://github.com/ansible-collections/community.digitalocean/issues/55).
- digitalocean inventory plugin - attributes available to filters are limited to explicitly required attributes and are prefixed with ``var_prefix`` (https://github.com/ansible-collections/community.digitalocean/pull/102).

New Modules
-----------

- digital_ocean_project - Manage a DigitalOcean project
- digital_ocean_project_info - Gather information about DigitalOcean Projects

v1.5.1
======

Bugfixes
--------

- digitalocean inventory plugin - Wire up advertised caching functionality (https://github.com/ansible-collections/community.digitalocean/pull/97).

v1.5.0
======

Minor Changes
-------------

- digitalocean - Filter droplets in dynamic inventory plugin using arbitrary. jinja2 expressions (https://github.com/ansible-collections/community.digitalocean/pull/96).
- digitalocean - Support templates in API tokens when using the dynamic inventory plugin (https://github.com/ansible-collections/community.digitalocean/pull/98).

Bugfixes
--------

- digital_ocean_database - Fixed DB attribute settings (https://github.com/ansible-collections/community.digitalocean/issues/94).
- digital_ocean_database_info - Cleanup unused attribs (https://github.com/ansible-collections/community.digitalocean/pulls/100).
- digital_ocean_snapshot_info - Fix lookup of snapshot_info by_id (https://github.com/ansible-collections/community.digitalocean/issues/92).
- digital_ocean_tag - Fix tag idempotency (https://github.com/ansible-collections/community.digitalocean/issues/61).

v1.4.2
======

Bugfixes
--------

- digital_ocean_droplet - Fixed Droplet inactive state (https://github.com/ansible-collections/community.digitalocean/pull/88).
- digital_ocean_sshkey - Fixed SSH Key Traceback Issue (https://github.com/ansible-collections/community.digitalocean/issues/68).

v1.4.1
======

Bugfixes
--------

- digital_ocean_droplet - Add integration tests for Droplet active and inactive states (https://github.com/ansible-collections/community.digitalocean/issues/66).
- digital_ocean_droplet - Fix Droplet inactive state (https://github.com/ansible-collections/community.digitalocean/issues/83).

v1.4.0
======

Bugfixes
--------

- digital_ocean_droplet_info - Fix documentation link for `digital_ocean_droplet_info` (https://github.com/ansible-collections/community.digitalocean/pull/81).
- digitalocean - Fix return docs for digital_ocean_sshkey_info (https://github.com/ansible-collections/community.digitalocean/issues/56).
- digitalocean - Update README.md for K8s and databases (https://github.com/ansible-collections/community.digitalocean/pull/80).

New Modules
-----------

- digital_ocean_droplet_info - Gather information about DigitalOcean Droplets

v1.3.0
======

New Modules
-----------

- digital_ocean_database - Create and delete a DigitalOcean database
- digital_ocean_database_info - Gather information about DigitalOcean databases
- digital_ocean_kubernetes - Create and delete a DigitalOcean Kubernetes cluster
- digital_ocean_kubernetes_info - Returns information about an existing DigitalOcean Kubernetes cluster

v1.2.0
======

Minor Changes
-------------

- digital_ocean - ``ssh_key_ids`` list entries are now validated to be strings (https://github.com/ansible-collections/community.digitalocean/issues/13).
- digital_ocean_droplet - ``ssh_keys``, ``tags``, and ``volumes`` list entries are now validated to be strings (https://github.com/ansible-collections/community.digitalocean/issues/13).
- digital_ocean_droplet - adding ``active`` and ``inactive`` states (https://github.com/ansible-collections/community.digitalocean/issues/23).
- digital_ocean_droplet - adds Droplet resize functionality (https://github.com/ansible-collections/community.digitalocean/issues/4).

Bugfixes
--------

- digital_ocean inventory script - fail cleaner on invalid ``HOST`` argument to ``--host`` option (https://github.com/ansible-collections/community.digitalocean/pull/44).
- digital_ocean inventory script - implement unimplemented ``use_private_network`` option and register missing ``do_ip_address``, ``do_private_ip_address`` host vars (https://github.com/ansible-collections/community.digitalocean/pull/45/files).
- digital_ocean inventory script - return JSON consistent with specification with ``--host`` (https://github.com/ansible-collections/community.digitalocean/pull/44).
- digital_ocean_domain - return zone records when creating a new zone (https://github.com/ansible-collections/community.digitalocean/issues/46).
- digital_ocean_droplet - add missing ``required=True`` on ``do_oauth_token`` in ``argument_spec`` (https://github.com/ansible-collections/community.digitalocean/issues/13).
- digital_ocean_floating_ip - fixes idempotence (https://github.com/ansible-collections/community.digitalocean/issues/5).

New Modules
-----------

- digital_ocean_balance_info - Display DigitalOcean customer balance

v1.1.1
======

Bugfixes
--------

- digitalocean - Drop collection version from README.md (https://github.com/ansible-collections/community.digitalocean/issues/63).

v1.1.0
======

Minor Changes
-------------

- digital_ocean_block_storage - included ability to resize Block Storage Volumes (https://github.com/ansible-collections/community.digitalocean/issues/38).

Bugfixes
--------

- digital_ocean_certificate_info - fix retrieving certificate by ID (https://github.com/ansible-collections/community.digitalocean/issues/35).
- digital_ocean_domain - module is now idempotent when called without IP (https://github.com/ansible-collections/community.digitalocean/issues/21).
- digital_ocean_load_balancer_info - fix retrieving load balancer by ID (https://github.com/ansible-collections/community.digitalocean/issues/35).

New Plugins
-----------

Inventory
~~~~~~~~~

- digitalocean - DigitalOcean Inventory Plugin

New Modules
-----------

- digital_ocean_domain_record - Manage DigitalOcean domain records
- digital_ocean_firewall - Manage cloud firewalls within DigitalOcean

v1.0.0
======

Bugfixes
--------

- Sanity test documentation fixes (https://github.com/ansible-collections/community.digitalocean/pull/3).
- Update docs examples to use FQCN (https://github.com/ansible-collections/community.digitalocean/issues/14).

v0.1.0
======

Release Summary
---------------

Initial release of the collection after extracing the modules from `community.general <https://github.com/ansible-collections/community.general/>`_.
