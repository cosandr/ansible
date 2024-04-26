# Ansible

## Network changes

Change general network stuff (VLANs, changing CIDRs) using the [templates](./files/inventory).

Change `host_net`, `host_num` and/or `ansible_host` in [hosts](./inventory/hosts).

When changes are made, [generate_inventory.yml](./playbooks/generate_inventory.yml) MUST be run.
If both were changed, it must be run **TWICE**.

## Wireguard

Generate keys on the command line with `wg genkey | tee /dev/stderr | wg pubkey`, private is the first string.

Store the private key with gopass, i.e.

```sh
gopass edit -c network/<inventory_hostname>_wg_pk
```

If using preshared keys, generate it with

```sh
wg genpsk
gopass edit -c network/<inventory_hostname>_wg_psk
```

## sshjail

```sh
mkdir -p ~/.ansible/plugins/connection
# use fork until PR is merged
# wget -O ~/.ansible/plugins/connection/sshjail.py https://raw.githubusercontent.com/austinhyde/ansible-sshjail/master/sshjail.py
wget -O ~/.ansible/plugins/connection/sshjail.py https://raw.githubusercontent.com/nerzhul/ansible-sshjail/patch-1/sshjail.py
```

## iocage

```sh
wget -O library/iocage.py https://raw.githubusercontent.com/fractalcells/ansible-iocage/master/iocage.py
```

## S3

```sh
sudo pacman -S python-botocore python-boto3

```

3. Add init/shutdown script in UI

## GCP

See [Ansible guide](https://docs.ansible.com/ansible/latest/scenario_guides/guide_gce.html) for more details.
Requires `requests google-auth` to be installed for the Python interpreter.

Create service account with DNS Administrator role.

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

## MikroTik

### Dump firewall rules

```yml
- name: Get FW rules
  community.routeros.api_info:
    path: ip firewall filter
    handle_disabled: omit
  register: __fw

- name: Write to file
  delegate_to: localhost
  ansible.builtin.copy:
    content: "{{ __fw.result | to_nice_yaml(indent=2) }}"
    dest: "/tmp/{{ inventory_hostname }}.yml"
```

Cleanup

```sh
yq -iy 'map(del(.".id"))' /tmp/rb5009.yml
sed -i -E "/^  (log|disabled): false.*/d;/^  log-prefix: ''/d;/^-.*/i\\ " /tmp/rb5009.yml
sed -i 's/^ $//g' /tmp/rb5009.yml
```

## Kubernetes

### Remove Intel GPU stuff

https://kubernetes-sigs.github.io/node-feature-discovery/v0.15/deployment/uninstallation.html

```sh
kubectl delete ns inteldeviceplugins-system
kubectl delete ns node-feature-discovery

kubectl apply -k 'https://github.com/kubernetes-sigs/node-feature-discovery/deployment/overlays/prune?ref=v0.15.4'
kubectl -n node-feature-discovery wait job.batch/nfd-master --for=condition=complete
kubectl delete -k 'https://github.com/kubernetes-sigs/node-feature-discovery/deployment/overlays/prune?ref=v0.15.4'

kubectl delete nodefeaturerules.nfd.k8s-sigs.io intel-dp-devices
kubectl delete nodefeaturerules.nfd.k8s-sigs.io intel-gpu-platform-labeling
kubectl delete crd nodefeatures.nfd.k8s-sigs.io
kubectl delete crd nodefeaturerules.nfd.k8s-sigs.io
```

### kubespray

Run kube playbook first

```sh
./playbooks/kube.yml -t system
```

If IPs were changed or hosts were added/removed, BGP peers must also be updated

```sh
./playbooks/mikrotik.yml -l rb5009 -t bgp
```

Run Ansible from the kubespray submodule

```sh
ansible-playbook -i ../inventory --vault-password-file ../gopass-vault.sh cluster.yml
```

### Talos

Setup config

```sh
./playbooks/talos.yml -t config,host -e force=true
cd /tmp/talos-config
export TALOSCONFIG=$(realpath ./talosconfig)
```
