# Ansible

## Wireguard

Generate keys on the command line with `wg genkey | tee /dev/stderr | wg pubkey`, private is the first string.

## VMware

[Ansible docs](https://docs.ansible.com/ansible/latest/collections/community/vmware/vmware_vm_inventory_inventory.html)

```sh
pip install -U --user pyvmomi git+https://github.com/vmware/vsphere-automation-sdk-python.git
```

Run with ansible with `-i vcenter.vmware.yml`, e.g:

```sh
ansible-playbook -i hosts -i vcenter.vmware.yml playbooks/pg.yml
```

Power on/off managed VMs

```sh
# Power on
ansible-playbook -i hosts -i slb.vmware.yml playbooks/esxi.yml -t start
# Power off
ansible-playbook -i hosts -i slb.vmware.yml playbooks/esxi.yml -t stop
# Target all VMs
ansible-playbook -i hosts -i slb.vmware.yml playbooks/esxi.yml -t stop,all_guests
# All except TrueNAS
ansible-playbook -i hosts -i slb.vmware.yml playbooks/esxi.yml -t stop,all_guests -l '!TrueNAS'
```

(un)mount NFS

```sh
# targetting one host
ansible-playbook -i hosts -i slb.vmware.yml playbooks/esxi.yml -l slb -t mount
```

## sshjail

```sh
mkdir -p ~/.ansible/plugins/connection
# use fork until PR is merged
# wget -O ~/.ansible/plugins/connection/sshjail.py https://raw.githubusercontent.com/austinhyde/ansible-sshjail/master/sshjail.py
wget -O ~/.ansible/plugins/connection/sshjail.py https://raw.githubusercontent.com/nerzhul/ansible-sshjail/patch-1/sshjail.py
```

## TrueNAS node exporter

1. Install node_exporter in a jail
2. Create script on host `/root/start_node.sh`

```sh
#!/bin/bash

screen -d -m /mnt/ssd/iocage/jails/test/root/usr/local/bin/node_exporter --web.listen-address=10.0.10.2:9100
```

3. Add init/shutdown script in UI

## GCP

See [Ansible guide](https://docs.ansible.com/ansible/latest/scenario_guides/guide_gce.html) for more details.
Requires `requests google-auth` to be installed for the Python interpreter.

Create service account with DNS Administrator role.

## Vault

Encrypt stuff:

```sh
# Generate with bitwarden
bw generate --length 55 | ansible-vault encrypt_string --stdin-name 'gitea_secret_key'
# Password from file
ansible-vault encrypt_string --vault-password-file .vault_key --stdin-name 'gitea_secret_key'
# Encrypt secrets
ansible-vault encrypt .secrets/vars.yml --output roles/common/vars/vault.yml
```

Get vault key from bw:

```sh
# Must be unlocked already
bw get item ansible | jq -j '.fields[] | select(.name == "vault") | .value' > .vault_key
```

## Running

```sh
# If playbook needs vault, ask
ansible-playbook <playbook> --ask-vault-pass
# from file
ansible-playbook <playbook> --vault-password-file .vault_key
# Run only on server host (if hosts is all in playbook)
ansible-playbook -l server playbook.yml
# Run only one tag in playbook
ansible-playbook playbook.yml --tags grafana
# Run in vscode docker
ansible-playbook -i hosts_local server.yml --tags nginx
# Run with sudo remote user
ansible-playbook -i hosts -K -e 'ansible_user=andrei' playbooks/laptop.yml --diff --check --tags laptop
```

## Hosts file example
`/etc/ansible/hosts` on source machine (running playbook)
```
localhost ansible_connection=local ansible_python_interpreter=/usr/bin/python3

desktop ansible_connection=local ansible_become=yes ansible_python_interpreter=/usr/bin/python3

server ansible_host=10.1.0.2 ansible_user=root ansible_python_interpreter=/usr/bin/python3
```

## Docker ports example
`/etc/ansible/facts.d/docker.fact` on remote (target) machine
```
[ports]
bitwarden_notifications=3012
bitwarden=8343
nextcloud=25683
portainer=9000
radarr=7878
sonarr=8989
transmission=9091
vouch=9090
vscode=8443
```
