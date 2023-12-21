#!/usr/bin/env python3


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.mt_utils import (
    make_add_update_remove,
    make_vid_map,
    sort_trunks,
)


def main():
    argument_spec = dict(
        existing=dict(type="list", elements="dict", required=True),
        networks=dict(type="dict", required=True),
        trunk_ports=dict(type="list", elements="str", default=[]),
        access_ports=dict(type="list", elements="dict", default=[]),
        switch_cpu=dict(type="str", default="switch1-cpu"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    existing = module.params["existing"]
    networks = module.params["networks"]
    trunk_ports = module.params["trunk_ports"]
    access_ports = module.params["access_ports"]
    switch_cpu = module.params["switch_cpu"]

    vid_map = make_vid_map(networks)
    vlan_ports = {name: [] for name in vid_map.keys()}
    new_data = []

    # Add access ports
    for cfg in access_ports:
        vlan = cfg["vlan"]
        if vlan not in vlan_ports:
            module.fail_json("Cannot find VLAN '{}'".format(vlan))
        vlan_ports[vlan] = cfg["ports"]

    # Add trunk ports
    if trunk_ports:
        for vlan in vlan_ports.keys():
            vlan_ports[vlan].extend(trunk_ports)

    # Create new data list
    for vlan, ports in vlan_ports.items():
        if not ports:
            continue
        new_data.append(
            {
                "ports": ",".join(sort_trunks(ports, switch_cpu)),
                "vlan-id": vid_map[vlan],
            }
        )

    to_add, to_update, to_remove = make_add_update_remove(existing, new_data, "vlan-id")

    ## Expected output:
    # new_data = [
    #     {
    #         ".id": "*C",
    #         "ports": "switch1-cpu,ether12,ether13,ether14,ether15,ether16,ether17,ether18,sfpplus2,sfp-sfpplus1",
    #         "vlan-id": 10,
    #     },
    # ]

    result = dict(
        changed=False, to_add=to_add, to_update=to_update, to_remove=to_remove
    )

    module.exit_json(**result)


if __name__ == "__main__":
    main()
