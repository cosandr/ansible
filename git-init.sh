#!/usr/bin/env bash
# sets up a pre-commit hook to ensure that vault.yaml is encrypted
#
# extended from https://github.com/IronicBadger/compose-secret-mgt/blob/master/git-init.sh

hook_path="$(git rev-parse --git-path hooks)/pre-commit"

cat <<EOT > "$hook_path"
#!/usr/bin/env bash

set -e

./vault-check.py
EOT

chmod +x "$hook_path"

declare -A remote_map=(
    ["roles/alertmanager"]="https://github.com/cloudalchemy/ansible-alertmanager.git"
    ["roles/blackbox_exporter"]="https://github.com/cloudalchemy/ansible-blackbox-exporter.git"
    ["roles/grafana"]="https://github.com/cloudalchemy/ansible-grafana.git"
    ["roles/libvirt_vm"]="https://github.com/stackhpc/ansible-role-libvirt-vm.git"
    ["roles/postgresql"]="https://github.com/geerlingguy/ansible-role-postgresql.git"
    ["roles/prometheus"]="https://github.com/cloudalchemy/ansible-prometheus.git"
    ["roles/wireguard"]="https://github.com/githubixx/ansible-role-wireguard.git"
    ## DEPRECATED
    # ["roles/unattended-upgrades"]="https://github.com/jnv/ansible-role-unattended-upgrades"
)

for dir in "${!remote_map[@]}"; do
    if git -C "$dir" remote show | grep -q upstream; then
        echo "$dir already has upstream defined"
        continue
    fi
    git -C "$dir" remote add upstream "${remote_map[$dir]}"
    git -C "$dir" remote set-url upstream --push DISABLED
    echo "$dir added ${remote_map[$dir]} as upstream"
done
