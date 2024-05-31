# Quirks

## localgw

First time provisioning is a bit finnicky. If it crashes due to low memory, create swapfile first with `-t swapfile`.

Afterwards the inter-dependencies should work if the playbook is run twice.

First with `--skip-tags pg_cert_store,nginx,nginx_exporter` followed by `-t pg_cert_store,nginx,nginx_exporter`

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
