# Ansible

## Vault

Encrypt stuff:

```sh
# Generate with bitwarden
bw generate --length 55 | ansible-vault encrypt_string --stdin-name 'gitea_secret_key'
# Password from file
ansible-vault encrypt_string --vault-password-file .vault_key --stdin-name 'gitea_secret_key'
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
ansible-playbook playbook.yml --tags "grafana"
```

## Hosts file example
```
localhost ansible_connection=local ansible_python_interpreter=/usr/bin/python3

desktop ansible_connection=local ansible_become=yes ansible_python_interpreter=/usr/bin/python3

server ansible_host=10.1.0.2 ansible_user=root ansible_python_interpreter=/usr/bin/python3
```
