#!/bin/bash

set -euo pipefail

# Disable globbing
set -f
# Set args
# shellcheck disable=SC2086
set -- $SSH_ORIGINAL_COMMAND

cmd="$1"

print_help() {
cat <<-END
Usage $0: COMMAND

Commands:
ping      Pong
sudo      Run command through sudo
help      Show this message
END
}

if [[ -z $cmd ]]; then
    print_help
    exit 1
fi

sudo_base_name="/usr/local/bin/sudo-runner"

case "$cmd" in
    help)
        print_help
        exit 0
        ;;
    ping)
        echo pong
        exit 0
        ;;
    sudo)
        sudo_cmd="$2"
        shift 2
        if [[ -z $sudo_cmd ]]; then
            echo "Missing sudo command"
            exit 1
        fi
        if ! [[ -x "${sudo_base_name}-${sudo_cmd}" ]]; then
            echo "Invalid sudo command: $sudo_cmd"
            exit 1
        fi
        exec sudo "${sudo_base_name}-${sudo_cmd}" "$@"
        ;;
    *)
        echo "Unknown command $cmd"
        exit 1
        ;;
esac
