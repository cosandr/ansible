# ansible-role-gitea

![GitHub](https://img.shields.io/github/license/cosandr/ansible-role-gitea) ![GitHub last commit](https://img.shields.io/github/last-commit/cosandr/ansible-role-gitea) ![GitHub issues](https://img.shields.io/github/issues-raw/cosandr/ansible-role-gitea)

**Ansible role for setting up gitea.**

## Supported Platforms

| OS Family | Distribution  | Latest | Supported Version(s) | Comment |
|-----------|---------------|--------|----------------------|---------|
| RedHat    | RHEL          | :heavy_check_mark: | 9 | |
|           | RockyLinux    | :heavy_check_mark: | 8, 9 | |
|           | AlmaLinux     | :heavy_check_mark: | 8, 9 | |
|           | Fedora        | :heavy_check_mark: | 36, 37, 38 | |

## Requirements

Ansible 2.12 or higher.

## Variables

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `example` | true | Can be set to false |


## Dependencies

None.

## Example Playbook

```yaml
---

- hosts: all
  become: true
  gather_facts: true
  roles:
    - role: ansible-role-gitea
```

## Author

[Andrei Costescu](https://github.com/cosandr/)
