#!/bin/bash
# sets up a pre-commit hook to ensure that vault.yaml is encrypted
#
# extended from https://github.com/IronicBadger/compose-secret-mgt/blob/master/git-init.sh

cat <<EOT > .git/hooks/pre-commit
#!/bin/bash

find files host_vars group_vars -type f -regextype egrep -regex '.*(\.csr|\.key|vault\.yml)$' -print0 | while read -d $'\0' f
do
    if ! grep -q "\$ANSIBLE_VAULT;" "\$f"; then
        echo "[38;5;208m\$f not encrypted! [0m"
        exit 1
    fi
done
EOT

chmod +x .git/hooks/pre-commit
