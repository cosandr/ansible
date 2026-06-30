# shellcheck shell=bash
cd /tmp
while read -r mntpt; do
    if [[ "$mntpt" == "none" || "$mntpt" == "legacy" ]]; then
        continue
    fi

    target_dir="${TMP_ROOT}${mntpt}"
    if mountpoint -q "$target_dir"; then
        umount -v "$target_dir"
        tmp_exit=$?
        global_exit=$(( tmp_exit > global_exit ? tmp_exit : global_exit ))
    fi
done < <(zfs list -H -o mountpoint -t filesystem -r "$POOL" | tac)

find "$TMP_ROOT" -type d -print -delete
tmp_exit=$?
global_exit=$(( tmp_exit > global_exit ? tmp_exit : global_exit ))
zfs destroy -rv "$POOL@$SNAP_NAME"
tmp_exit=$?
global_exit=$(( tmp_exit > global_exit ? tmp_exit : global_exit ))
