#!/bin/bash

set -ex

# Ensure CephFS is mounted
mountpoint -q /mnt/ceph
mountpoint -q /mnt/tank

# Ensure SMB is running
nc -vz localhost 445
