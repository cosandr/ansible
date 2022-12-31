cd /
# Set snapshots RW so we can delete nested ones
for p in "${snap_subvols[@]}"; do
    btrfs property set -ts "$snap_dir/$p" ro false
done

for (( idx=${#snap_subvols[@]}-1 ; idx>=0 ; idx-- )) ; do
    btrfs subvolume delete "$snap_dir/${snap_subvols[idx]}"
done

rmdir "$snap_dir"
