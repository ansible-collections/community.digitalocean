# DigitalOcean Community Collection
[![CI](https://github.com/ansible-collections/community.digitalocean/workflows/CI/badge.svg?event=push)](https://github.com/ansible-collections/community.digitalocean/actions) [![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/community.digitalocean)](https://codecov.io/gh/ansible-collections/community.digitalocean)

This collection contains modules and plugins to assist in automating [DigitalOcean](https://www.digitalocean.com) infrastructure and API interactions with Ansible.

## Tested with Ansible

Tested with the current Ansible 2.9 and 2.10 releases and the current development version of Ansible. Ansible versions before 2.9.10 are not supported.

## Included content

- [digitalocean](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/module.html) – Create/delete a droplet/SSH_key in DigitalOcean
- [account_facts](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/account_facts_module.html) – Gather information about DigitalOcean User account
- [account_info](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/account_info_module.html) – Gather information about DigitalOcean User account
- [block_storage](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/block_storage_module.html) – Create/destroy or attach/detach Block Storage volumes in DigitalOcean
- [certificate](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/certificate_module.html) – Manage certificates in DigitalOcean.
- [certificate_facts](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/certificate_facts_module.html) – Gather information about DigitalOcean certificates
- [certificate_info](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/certificate_info_module.html) – Gather information about DigitalOcean certificates
- [domain](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/domain_module.html) – Create/delete a DNS domain in DigitalOcean
- [domain_facts](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/domain_facts_module.html) – Gather information about DigitalOcean Domains
- [domain_info](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/domain_info_module.html) – Gather information about DigitalOcean Domains
- [droplet](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/droplet_module.html) – Create and delete a DigitalOcean droplet
- [firewall_facts](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/firewall_facts_module.html) – Gather information about DigitalOcean firewalls
- [firewall_info](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/firewall_info_module.html) – Gather information about DigitalOcean firewalls
- [floating_ip](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/floating_ip_module.html) – Manage DigitalOcean Floating IPs
- [floating_ip_facts](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/floating_ip_facts_module.html) – DigitalOcean Floating IPs information
- [floating_ip_info](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/floating_ip_info_module.html) – DigitalOcean Floating IPs information
- [image_facts](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/image_facts_module.html) – Gather information about DigitalOcean images
- [image_info](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/image_info_module.html) – Gather information about DigitalOcean images
- [load_balancer_facts](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/load_balancer_facts_module.html) – Gather information about DigitalOcean load balancers
- [load_balancer_info](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/load_balancer_info_module.html) – Gather information about DigitalOcean load balancers
- [region_facts](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/region_facts_module.html) – Gather information about DigitalOcean regions
- [region_info](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/region_info_module.html) – Gather information about DigitalOcean regions
- [size_facts](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/size_facts_module.html) – Gather information about DigitalOcean Droplet sizes
- [size_info](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/size_info_module.html) – Gather information about DigitalOcean Droplet sizes
- [snapshot_facts](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/snapshot_facts_module.html) – Gather information about DigitalOcean Snapshot
- [snapshot_info](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/snapshot_info_module.html) – Gather information about DigitalOcean Snapshot
- [sshkey](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/sshkey_module.html) – Manage DigitalOcean SSH keys
- [sshkey_facts](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/sshkey_facts_module.html) – DigitalOcean SSH keys facts
- [sshkey_info](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/sshkey_info_module.html) – Gather information about DigitalOcean SSH keys
- [tag](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/tag_module.html) – Create and remove tag(s) to DigitalOcean resource.
- [tag_facts](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/tag_facts_module.html) – Gather information about DigitalOcean tags
- [tag_info](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/tag_info_module.html) – Gather information about DigitalOcean tags
- [volume_facts](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/volume_facts_module.html) – Gather information about DigitalOcean volumes
- [volume_info](https://docs.ansible.com/ansible/2.10/collections/community/digitalocean/volume_info_module.html) – Gather information about DigitalOcean volumes

## Installation and Usage

### Installing the Collection from Ansible Galaxy

Before using the DigitalOcean collection, you need to install it with the Ansible Galaxy CLI:

    ansible-galaxy collection install community.digitalocean

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: community.digitalocean
    version: 1.0.0
```

### Using modules from the DigitalOcean Collection in your playbooks

It's preferable to use content in this collection using their Fully Qualified Collection Namespace (FQCN), for example `community.digitalocean.droplet`:

```yaml
---
- hosts: localhost
  gather_facts: false
  connection: local

  tasks:
    - name: Create ssh key
      community.digitalocean.sshkey:
        oauth_token: "{{ oauth_token }}"
        name: mykey
        ssh_pub_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAQQDDHr/jh2Jy4yALcK4JyWbVkPRaWmhck3IgCoeOO3z1e2dBowLh64QAM+Qb72pxekALga2oi4GvT+TlWNhzPH4V example"
        state: present
      register: result

    - name: Create a new droplet
      community.digitalocean.droplet:
        state: present
        name: mydroplet
        oauth_token: "{{ oauth_token }}"
        size: 2gb
        region: sfo1
        image: ubuntu-20-04-x64
        wait_timeout: 500
        ssh_keys:
          - mykey
      register: my_droplet

    - debug:
        msg: "ID is {{ my_droplet.data.droplet.id }}, IP is {{ my_droplet.data.ip_address }}"

    - name: Tag a resource; creating the tag if it does not exist
      tag:
        name: "{{ item }}"
        resource_id: "{{ my_droplet.data.droplet.id }}"
        state: present
      loop:
        - staging
        - dbserver
```

If upgrading older playbooks which were built prior to Ansible 2.10 and this collection's existence, you can also define `collections` in your play and refer to this collection's modules as you did in Ansible 2.9 and below, as in this example:

```yaml
---
- hosts: localhost
  gather_facts: false
  connection: local

  collections:
    - community.digitalocean

  tasks:
    - name: Create ssh key
      sshkey:
        oauth_token: "{{ oauth_token }}"
        ...
```

## Testing and Development

If you want to develop new content for this collection or improve what's already here, the easiest way to work on the collection is to clone it into one of the configured [`COLLECTIONS_PATHS`](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#collections-paths), and work on it there.

### Testing with `ansible-test`

The `tests` directory contains configuration for running sanity and integration tests using [`ansible-test`](https://docs.ansible.com/ansible/latest/dev_guide/testing_integration.html).

You can run the collection's test suites with the commands:

    ansible-test sanity --docker -v --color
    ansible-test integration --docker -v --color

Note: To run integration tests, you must add an [`integration_config.yml`](https://docs.ansible.com/ansible/latest/dev_guide/testing_integration.html#integration-config-yml) file with a valid DigitalOcean API key (using variable `do_api_key`).

## Release notes

See the [changelog](https://github.com/ansible-collections/community.digitalocean/blob/main/CHANGELOG.rst).

### Release process

Releases are automatically built and pushed to Ansible Galaxy for any new tag. Before tagging a release, make sure to do the following:

  1. Update `galaxy.yml` and this README's `requirements.yml` example with the new `version` for the collection.
  1. Update the CHANGELOG:
    1. Make sure you have [`antsibull-changelog`](https://pypi.org/project/antsibull-changelog/) installed.
    1. Make sure there are fragments for all known changes in `changelogs/fragments`.
    1. Run `antsibull-changelog release`.
  1. Commit the changes and create a PR with the changes. Wait for tests to pass, then merge it once they have.
  1. Tag the version in Git and push to GitHub.

After the version is published, verify it exists on the [DigitalOcean Collection Galaxy page](https://galaxy.ansible.com/community/digitalocean).

## More information

  - [DigitalOcean Working Group](https://github.com/ansible/community/wiki/Digital-Ocean)
  - [Ansible Collection overview](https://github.com/ansible-collections/overview)
  - [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
  - [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
  - [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0 or later.

See [COPYING](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
