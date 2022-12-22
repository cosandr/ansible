#!/bin/bash

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
    if git -C "$dir" remote -v | grep -q upstream; then
        echo "$dir already has upstream defined"
        continue
    fi
    git -C "$dir" remote add upstream "${remote_map[$dir]}"
    git -C "$dir" remote set-url upstream --push DISABLED
done
