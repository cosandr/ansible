# Setup disk

Installs and configures LVM on data disks.


### Required parameters

- `provisioned_disks`
  - `dev` path to device, required

### Optional parameters

If none are specified, the device is formatted with ext4 without any mointpoints.

- `fstype` filesystem to use for raw disks, defaults to ext4
- `mkfs_opts` mkfs options
- `path` optional mountpoint
- `vols` list of logical volumes, at least one LV is required
  - `name` name of volume, can be found at `/dev/mapper/data-{{ name }}`
  - `path` optional mountpoint
  - `fstype` optional, defaults to ext4
  - `opts` filesystem mount options
  - `size` LVOL size, defaults to 100%VG
  - `shrink` whenever to shrink LVOL or not, must be set to false if using 100%FREE as size


### Example playbook

```yml
---

- hosts: azure
  roles:
    # With LVM
    - role: linux_setup_disk
      vars:
        provisioned_disks:
          - dev: "/dev/sdb"
            vols:
              - name: log
                path: "/var/log/elasticsearch"
                fstype: xfs
                size: "20g"
              - name: esdata
                path: "/var/lib/elasticsearch"
                shrink: no  # 100%FREE fails on re-runs if this is true (default)
                size: "100%FREE"
          # Raw
          - dev: "/dev/sdb"
            fstype: xfs
            path: "/var/lib/pgsql"
```
