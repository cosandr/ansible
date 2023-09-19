#!/usr/bin/env python3

import glob

files = []
check_dirs = ["files", "inventory"]

patterns = []
with open('.gitattributes', 'r') as f:
    for line in f:
        if 'ansible-vault' in line:
            patterns.append(line.split()[0])

for d in check_dirs:
    for p in patterns:
        files.extend(glob.glob(f"{d}/**/{p}", recursive=True))

failed = []
for f in files:
    with open(f, 'r') as fr:
        line = fr.readline()
        if not line.startswith('$ANSIBLE_VAULT;'):
            failed.append(f)

if failed:
    print("\x1b[38;5;208m{} not encrypted!\x1b[0m".format(', '.join(failed)))
    exit(1)
