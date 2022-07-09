#!/bin/bash

logfile=/root/esxi/shutdown.log

echo "$(date)" > $logfile

source /root/esxi/hosts

if [[ "${#esxi_hosts[@]}" -eq 0 ]]; then
    echo "No ESXi hosts configured" >> $logfile
    exit 0
fi

for h in "${esxi_hosts[@]}"; do
    if ! ping -c 3 -W 1 "$h" > /dev/null; then
        echo "$h unreachable, skipping" >> $logfile
        continue
    fi
    if ! ssh root@"$h" /bin/true; then
        echo "$h ssh failed, skipping" >> $logfile
        continue
    fi

   # Get list of TrueNAS datastores and store them in an array
    readarray -t host_datastores <<< "$(ssh root@"$h" esxcli storage nfs41 list | grep TrueNAS)"
    if [[ "${#host_datastores[@]}" -eq 0 ]]; then
        echo "$h has no TrueNAS datastores configured"
        exit 0
    fi

    for hd in "${host_datastores[@]}"; do
        /root/esxi/stop-all-datastore-vms.sh root "$h" "$hd" >> $logfile
    done
done
