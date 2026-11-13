# Quirks

## localgw

First time provisioning is a bit finnicky. If it crashes due to low memory, create swapfile first with `-t swap`.

Afterwards the inter-dependencies should work if the playbook is run twice.

First with `--skip-tags pg_cert,nginx,nginx_exporter` followed by `-t pg_cert,nginx,nginx_exporter`

Need to request certificates manually the first time.

```sh
cd /etc/lego
sudo -u lego env LEGO_PATH=/etc/lego /usr/local/bin/lego

```
Push certs if needed
```sh
ansible localgw -m shell -a "{% for d in lego_certificates.keys() %}echo /usr/local/bin/pg-cert-push --name {{ d }} --public-key /etc/lego/certificates/{{ d }}.crt --private-key /etc/lego/certificates/{{ d }}.key --chain /etc/lego/certificates/{{ d }}.issuer.crt; {% endfor %}"
```

## cloudgw

After deploy, install pre-reqs

```sh
apt-get purge -y ifupdown ufw cloud-init resolvconf && rm -rf /etc/network /etc/cloud/
echo -e "[Match]\nType=ether\n\n[Network]\nDHCP=yes\n" > /etc/systemd/network/dhcp.network
systemctl enable systemd-networkd
echo -e "nameserver 1.1.1.1\nnameserver 8.8.8.8" > /etc/resolv.conf
apt update
apt install -y firewalld vim net-tools apparmor-utils apt-file auditd systemd-resolved
apt full-upgrade -y
apt autoremove -y
```

```sh
# comment out ansible_ssh_host first
./playbooks/webgw.yml -l cloudgw -t user
./playbooks/webgw.yml -l cloudgw -t networkd
./playbooks/common-all.yml -t wireguard -l cloudgw
./playbooks/webgw.yml -l cloudgw -t firewall
./playbooks/webgw.yml -l cloudgw -t sshd
# add back ansible_ssh_host
./playbooks/webgw.yml -l cloudgw
./playbooks/prom.yml -l cloudgw
```

If restoring SSH host keys

```sh
chmod 600 /etc/ssh/ssh_host_{ecdsa,ed25519,rsa}_key
systemctl restart sshd
```
