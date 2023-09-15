#!/usr/bin/env python3

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.mt_utils import make_vid_map


def main():
    argument_spec = dict(
        networks=dict(type="dict", required=True),
        all_ports=dict(type="list", elements="str", required=True),
        trunk_ports=dict(type="list", elements="str", default=[]),
        access_ports=dict(type="list", elements="dict", default=[]),
        bridge_name=dict(type="str", default="bridge1"),
        port_params=dict(type="dict", default={}),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    networks = module.params["networks"]
    all_ports = module.params["all_ports"]
    trunk_ports = module.params["trunk_ports"]
    access_ports = module.params["access_ports"]
    bridge_name = module.params["bridge_name"]
    port_params = module.params["port_params"]

    vid_map = make_vid_map(networks)

    # Mapping to make processing easier
    new_data = {}
    # Add all ports
    for p in all_ports:
        new_data[p] = {
            "bridge": bridge_name,
            "interface": p,
        }
        for k,v in port_params.items():
            new_data[p][k] = v
    # Configure access ports
    for cfg in access_ports:
        vid = vid_map.get(cfg['vlan'])
        if not vid:
            module.fail_json("Cannot find VID for '{}'".format(cfg['vlan']))
        for p in cfg['ports']:
            if p not in new_data:
                module.fail_json("'{}' is not a bridge port".format(p))
            new_data[p]["pvid"] = vid

    # Configure trunk ports
    for p in trunk_ports:
        if p not in new_data:
            module.fail_json("'{}' is not a bridge port".format(p))
        new_data[p]["frame-types"] = "admit-only-vlan-tagged"

    ## Expected output:
    # new_data = [
    #     {
    #         "bridge": "bridge1",
    #         "interface": "ether1",
    #         "pvid": 100
    #     },
    #     {
    #         "bridge": "bridge1",
    #         "frame-types": "admit-only-vlan-tagged",
    #         "interface": "sfp-sfpplus1"
    #     },
    # ]

    result = dict(changed=False, new_data=list(new_data.values()))

    module.exit_json(**result)

if __name__ == "__main__":
    main()
