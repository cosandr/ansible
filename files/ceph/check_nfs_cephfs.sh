#!/bin/bash

set -ex

# Ensure CephFS is mounted
mountpoint -q /mnt/ceph

# Ensure NFS is running
nc -vz localhost 2049
