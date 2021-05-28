#!/bin/bash

declare -A file_map
file_map[".secrets/all_vault.yml"]="group_vars/all/vault.yml"
file_map[".secrets/dresrv_vault.yml"]="host_vars/dresrv/vault.yml"
file_map[".secrets/desktop_vault.yml"]="host_vars/desktop/vault.yml"
file_map[".secrets/laptop_vault.yml"]="host_vars/laptop/vault.yml"

for i in "${!file_map[@]}"; do
    enc="${file_map[$i]}"
    dec="$i"
    if [[ ! -f "$dec" ]]; then
        echo "$dec not found, decrypting"
        ansible-vault decrypt "$enc" --output "$dec"
        continue
    fi
    enc_content=$(ansible-vault decrypt "$enc" --output -)
    # Do the files differ?
    if ! echo "$enc_content" | diff -q "$dec" - > /dev/null; then
        encrypt=1
        enc_diff=1
        # Encrypted file is newer, do we replace decrypted file?
        if [[ $enc -nt $dec ]]; then
            echo "$enc_content" | diff --unified --color=always "$dec" -
            read -rp "Replace $dec with newer encrypted file? [yN] " yn
            case $yn in
                [Yy]* ) encrypt=0;;
                * ) enc_diff=0;;
            esac
        fi
        if [[ $encrypt -eq 1 ]]; then
            echo "Encrypting $dec"
            [[ $enc_diff -eq 1 ]] && echo "$enc_content" | diff --unified --color=always - "$dec"
            ansible-vault encrypt "$dec" --output "$enc"
        else
            echo "Decrypting $dec"
            ansible-vault decrypt "$enc" --output "$dec"
        fi
    else
        echo "$enc up to date"
    fi
done
