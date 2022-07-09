#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Missing ESXi host"
    exit 1
fi

h=$1

# Get list of TrueNAS datastores and store them in an array
readarray -t host_datastores <<< "$(ssh root@"$h" esxcli storage nfs41 list | grep TrueNAS)"
if [[ "${#host_datastores[@]}" -eq 0 ]]; then
    echo "$h has no TrueNAS datastores configured"
    exit 0
fi

for hd in "${host_datastores[@]}"; do
    vol_name="$(awk '{print $1}' <<< "$hd")"
    vol_host="$(awk '{print $2}' <<< "$hd")"
    vol_share="$(awk '{print $3}' <<< "$hd")"
    vol_accessible="$(awk '{print $4}' <<< "$hd")"
    echo
    echo "$h - $vol_name Host: $vol_host Share: $vol_share Accessible: $vol_accessible"
    # Sanity check
    if [[ -z $vol_name || -z $vol_host || -z $vol_share || -z $vol_accessible ]]; then
        echo "$h: Parse failure"
        continue
    fi
    # Remount if volume is inaccessible
    if [[ $vol_accessible == 'false' ]]; then
        if ssh root@"$h" esxcli storage nfs41 remove -v "$vol_name"; then
            echo "$h - $vol_name removed"
            if ssh root@"$h" esxcli storage nfs41 add -H "$vol_host" -s "$vol_share" -v "$vol_name"; then
                echo "$h - $vol_name added"
            else
                echo "$h - $vol_name cannot add"
            fi
        else
            echo "$h - $vol_name cannot remove"
        fi
    else
        echo "$h - $vol_name is accessible"
    fi
done
