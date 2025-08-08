# Quirks

## localgw

First time provisioning is a bit finnicky. If it crashes due to low memory, create swapfile first with `-t swap`.

Afterwards the inter-dependencies should work if the playbook is run twice.

First with `--skip-tags pg_cert,nginx,nginx_exporter` followed by `-t pg_cert,nginx,nginx_exporter`

Need to request certificates manually the first time.

```sh
sudo -u lego env FORCE=1 /usr/local/bin/lego-wrapper run

```
Push certs if needed
```sh
ansible localgw01 -m shell -a "{% for d in lego_domain_keys %}/usr/local/bin/pg-cert-push --name {{ domains[d] }} --public-key /etc/lego/certificates/{{ domains[d] }}.crt --private-key /etc/lego/certificates/{{ domains[d] }}.key --chain /etc/lego/certificates/{{ domains[d] }}.issuer.crt; {% endfor %}"
```

Pull on other nodes and fix services

```sh
ansible localgw -a '/usr/local/bin/pg-cert-pull-systemd'
ansible localgw -a 'systemctl restart nginx'
ansible localgw -a 'systemctl restart nginx_exporter'
```

## withings-sync

Need to sign in manually the first time

```sh
sudo -u withings-sync -i
source /etc/default/withings-sync && export GARMIN_USERNAME GARMIN_PASSWORD
/opt/withings-sync/venv/bin/withings-sync -f 2023-09-26 -v
```

## webgw

After deploy, install pre-reqs

```sh
dnf install -y firewalld vim net-tools
```

```sh
./playbooks/webgw.yml -l webgw01 -t user -e ansible_port=22
./playbooks/webgw.yml -l webgw01 -t sshd
./playbooks/webgw.yml -l webgw01
ansible webgw01 -m dnf -a 'name=NetworkManager state=absent'
ansible webgw01 -m dnf -a 'name=cloud-init state=absent'
./playbooks/prom.yml -l webgw01
```

If restoring SSH host keys

```sh
restorecon -rv /etc/ssh
chmod 600 /etc/ssh/ssh_host_{ecdsa,ed25519,rsa}_key
systemctl restart sshd
```
