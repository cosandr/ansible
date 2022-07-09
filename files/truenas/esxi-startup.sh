#!/bin/bash

logfile=/root/esxi/startup.log

echo "$(date)" > $logfile

source /root/esxi/hosts

if [[ "${#esxi_hosts[@]}" -eq 0 ]]; then
    echo "No ESXi hosts configured" >> $logfile
    exit 0
fi

startup_vms=(
    "pg01"
    "localgw01"
    "prom01"
    "loki01"
    "VMware vCenter Server"
    "DreSRV"
    "nextcloud01"
)

started_vms=()

# https://stackoverflow.com/a/8574392
containsElement () {
  local e match="$1"
  shift
  for e; do [[ "$e" == "$match" ]] && return 0; done
  return 1
}

for h in "${esxi_hosts[@]}"; do
    if ! ping -c 3 -W 1 "$h" > /dev/null; then
        echo "$h unreachable, skipping" >> $logfile
        continue
    fi
    if ! ssh root@"$h" /bin/true; then
        echo "$h ssh failed, skipping" >> $logfile
        continue
    fi

    /root/esxi/remount-nfs.sh "$h" &>> $logfile

    for vm in "${startup_vms[@]}"; do
        if ! containsElement "$vm" "${started_vms[@]}"; then
            if /root/esxi/start-vm.sh root "$h" "$vm" | tee -a $logfile | grep -i power; then
                # Add to list if VM was on that host, either if it was powered on or if it's already running
                started_vms+=("$vm")
            else
                echo "$h has no VM '$vm'" >> $logfile
            fi
        fi
    done
done
