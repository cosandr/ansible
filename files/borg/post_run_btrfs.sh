cd /
for (( idx=${#snap_subvols[@]}-1 ; idx>=0 ; idx-- )) ; do
    btrfs subvolume delete "$snap_dir/${snap_subvols[idx]}"
done

rmdir "$snap_dir"
