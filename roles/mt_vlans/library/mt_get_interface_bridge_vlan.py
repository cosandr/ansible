#!/usr/bin/env python3


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.mt_utils import make_vid_map


def main():
    argument_spec = dict(
        networks=dict(type="dict", required=True),
        trunk_ports=dict(type="list", elements="str", default=[]),
        access_ports=dict(type="list", elements="dict", default=[]),
        bridge_name=dict(type="str", default="bridge1"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    networks = module.params["networks"]
    trunk_ports = module.params["trunk_ports"]
    access_ports = module.params["access_ports"]
    bridge_name = module.params["bridge_name"]

    vid_map = make_vid_map(networks)

    # Mapping to make processing easier
    new_data = {}
    # Add all VLANs
    for name, vid in vid_map.items():
        new_data[name] = {
            "bridge": bridge_name,
            "vlan-ids": vid,
        }

    # Configure access ports
    for cfg in access_ports:
        vlan = cfg['vlan']
        if vlan not in new_data:
            module.fail_json("Cannot find VLAN '{}'".format(vlan))
        vid = vid_map.get(vlan)
        if not vid:
            module.fail_json("Cannot find VID for '{}'".format(vlan))
        new_data[vlan]["untagged"] = ','.join(cfg['ports'])

    # Configure trunk ports
    if trunk_ports:
        for name, cfg in new_data.items():
            # Ensure bridge is part of tagged VLANs
            cfg['tagged'] = ','.join([bridge_name] + trunk_ports)

    ## Expected output:
    # new_data = [
    #     {
    #         "bridge": "bridge1",
    #         "tagged": "bridge1,sfp-sfpplus1,...",
    #         "vlan-ids": 2
    #     },
    #     {
    #         "bridge": "bridge1",
    #         "tagged": "bridge1,sfp-sfpplus1,...",
    #         "untagged": "ether1",
    #         "vlan-ids": 100
    #     }
    # ]

    result = dict(changed=False, new_data=list(new_data.values()))

    module.exit_json(**result)

if __name__ == "__main__":
    main()
