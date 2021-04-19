====================================
Community DigitalOcean Release Notes
====================================

.. contents:: Topics


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
