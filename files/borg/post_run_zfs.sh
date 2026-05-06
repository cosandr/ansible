# shellcheck shell=bash
while read -r mntpt; do
    if [[ "$mntpt" == "none" || "$mntpt" == "legacy" ]]; then
        continue
    fi

    target_dir="${TMP_ROOT}${mntpt}"
    if mountpoint -q "$target_dir"; then
        umount "$target_dir"
    fi
done < <(zfs list -H -o mountpoint -t filesystem -r "$POOL" | tac)

find "$TMP_ROOT" -type d -print -delete
zfs destroy -rv "$POOL@$SNAP_NAME"
