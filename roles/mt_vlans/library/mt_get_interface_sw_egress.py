#!/usr/bin/env python3

import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.mt_utils import make_add_update_remove, make_vid_map, sort_trunks


def main():
    argument_spec = dict(
        existing=dict(type="list", elements="dict", required=True),
        networks=dict(type="dict", required=True),
        trunk_ports=dict(type="list", elements="str", default=[]),
        switch_cpu=dict(type="str", default='switch1-cpu'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    existing = module.params["existing"]
    networks = module.params["networks"]
    trunk_ports = module.params["trunk_ports"]
    switch_cpu = module.params["switch_cpu"]

    vid_map = make_vid_map(networks)
    new_data = []

    # Add trunk ports
    if trunk_ports:
        for vid in vid_map.values():
            new_data.append({
                "tagged-ports": ','.join(sort_trunks(trunk_ports, switch_cpu)),
                "vlan-id": vid,
            })

    to_add, to_update, to_remove = make_add_update_remove(existing, new_data, 'vlan-id')

    ## Expected output:
    # [
    #     {
    #         ".id": "*1",
    #         "tagged-ports": "switch1-cpu,ether1,...",
    #         "vlan-id": 10
    #     },
    # ]

    result = dict(changed=False, to_add=to_add, to_update=to_update, to_remove=to_remove)

    module.exit_json(**result)

if __name__ == "__main__":
    main()
