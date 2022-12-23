#!/usr/bin/env bash

if [ -z "$1" ]; then
    echo "Missing path to submodule"
    exit 1
fi

if [ ! -f "$1"/.git ]; then
    echo "$1 doesn't exist or isn't a submodule"
    exit 1
fi

# https://stackoverflow.com/a/1260982

git rm -f "$1"
rm -rf "$(git rev-parse --git-path "$1")"
git config --remove-section submodule."$1"
