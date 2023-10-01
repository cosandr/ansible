#!/usr/bin/env python3

import re

from netaddr import IPAddress

from ansible.module_utils.basic import AnsibleModule


def get_entry(data, entry):
    for d in data:
        name = entry.get('name')
        regexp = entry.get('regexp')
        self_address = d.get('address')
        other_address = entry.get('address')
        # Skip if it's the wrong family
        if self_address and other_address and IPAddress(self_address).version != IPAddress(other_address).version:
            continue
        if name and d.get('name') == name:
            return d
        if regexp and d.get('regexp') == regexp:
            return d
    return None


def entries_eq(old, new):
    for k, v in new.items():
        if k not in old:
            return False
        if old[k] != v:
            return False

    return True


def main():
    argument_spec = dict(
        existing=dict(type="list", elements="dict", required=True),
        data=dict(type="list", elements="dict", required=True),
        comment_regex=dict(type="str", default=''),
        exclude_comment_regex=dict(type="str", default=''),
        remove_without_comment=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    existing = module.params["existing"]
    data = module.params["data"]
    comment_regex = module.params["comment_regex"]
    exclude_comment_regex = module.params["exclude_comment_regex"]
    remove_without_comment = module.params["remove_without_comment"]

    if comment_regex:
        comment_regex = re.compile(comment_regex)

    if exclude_comment_regex:
        exclude_comment_regex = re.compile(exclude_comment_regex)

    to_add = []
    to_update = []
    to_remove = []

    existing_managed = []
    for d in existing:
        if d['comment']:
            if comment_regex and not comment_regex.match(d['comment']):
                continue
            if exclude_comment_regex and exclude_comment_regex.match(d['comment']):
                continue
        if not get_entry(data, d):
            if not d['comment'] and not remove_without_comment:
                continue
            to_remove.append(d)
        existing_managed.append(d)

    # Find entries to add or update
    for d in data:
        if 'name' not in d and 'regexp' not in d:
            module.warn("mt_get_dns_entries: Data missing 'name' and 'regexp', check for undefined variables.")
            continue
        old = get_entry(existing_managed, d)
        if not old:
            to_add.append(d)
        elif not entries_eq(old, d):
            # Add ID for faster editing
            d['.id'] = old['.id']
            to_update.append(d)

    result = dict(changed=False, to_add=to_add, to_update=to_update, to_remove=to_remove)

    module.exit_json(**result)

if __name__ == "__main__":
    main()
