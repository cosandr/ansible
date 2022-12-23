#!/usr/bin/env bash

set -euo pipefail

# Based on https://github.com/jam82/ansible-role-skeleton#usage

if [ -z "$1" ]; then
    echo "Please specify a role name that will be appended to ansible-role-<rolename>"
    exit 1
fi

ansible-galaxy role init --role-skeleton=../ansible-role-skeleton roles/ansible-role-"$1"
sh roles/ansible-role-"$1"/init.sh

mv roles/ansible-role-"$1" roles/"$1"

echo "Adding submodule"
git -C roles/"$1" commit -m "Initial commit"

url=$(git -C roles/"$1" remote -v | head -n1 | awk '{ print $2 }')
git submodule add "$url" roles/"$1"
git submodule absorbgitdirs roles/"$1"

echo "To edit the first commit: git rebase -i --root"
