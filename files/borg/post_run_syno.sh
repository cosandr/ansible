# shellcheck shell=bash

syno_is_down() {
    local attempt=0
    local retries=$1
    while [[ $attempt -lt $retries ]]; do
        # ping should exit with 0 if any of the 5 packets received a reply
        if ! ping -q -n -c5 -W1 "$syno_ip" &>/dev/null; then
            echo "Synology is down after $attempt attempts"
            return 0
        fi
        attempt=$(( attempt + 1 ))
    done
    return 1
}

if ! ssh -q -o "BatchMode=yes" -i "$synoctl_key" "$syno_ssh_cmd" poweroff; then
    # poweroff command exists with non-zero, only fail if the system really wasn't powered off
    if ! syno_is_down 50; then
        echo "Failed to poweroff synology"
        exit 1
    fi
fi
