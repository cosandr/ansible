#!/bin/bash

declare -A file_map
file_map[".secrets/all_vault.yml"]="group_vars/all/vault.yml"
file_map[".secrets/server_vault.yml"]="host_vars/server/vault.yml"
# file_map[".secrets/ca.crt"]="roles/prometheus/files/ca.crt"
# file_map[".secrets/dresrv.crt"]="roles/prometheus/files/dresrv.crt"
# file_map[".secrets/dresrv.key"]="roles/prometheus/files/dresrv.key"

for i in "${!file_map[@]}"
do
    echo "Encrypting $i"
    if [[ ! -f "$i" ]]; then
        echo "$i no such file"
        continue
    fi
    ansible-vault encrypt "$i" --output "${file_map[$i]}"
done
