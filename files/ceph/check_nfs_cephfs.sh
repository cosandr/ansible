#!/bin/bash

set -ex

# Ensure CephFS is mounted
mountpoint -q /mnt/ceph
mountpoint -q /mnt/ceph_tank

# Ensure NFS is running
nc -vz localhost 2049
