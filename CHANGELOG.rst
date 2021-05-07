====================================
Community DigitalOcean Release Notes
====================================

.. contents:: Topics


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
