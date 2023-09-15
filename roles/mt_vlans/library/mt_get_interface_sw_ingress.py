#!/usr/bin/env python3

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.mt_utils import make_add_update_remove, make_vid_map


def main():
    argument_spec = dict(
        existing=dict(type="list", elements="dict", required=True),
        networks=dict(type="dict", required=True),
        access_ports=dict(type="list", elements="dict", default=[]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    existing = module.params["existing"]
    networks = module.params["networks"]
    access_ports = module.params["access_ports"]

    vid_map = make_vid_map(networks)
    new_data = []

    # Configure access ports
    for cfg in access_ports:
        vlan = cfg['vlan']
        vid = vid_map.get(vlan)
        if not vid:
            module.fail_json("Cannot find VLAN or its VID '{}'".format(vlan))

        new_data.append({
            "customer-vid": 0,
            "new-customer-vid": vid,
            "ports": ','.join(cfg['ports']),
        })

    to_add, to_update, to_remove = make_add_update_remove(existing, new_data, 'new-customer-vid')

    ## Expected output:
    # [
    #     {
    #         ".id": "*F",
    #         "customer-vid": 0,
    #         "new-customer-vid": 50,
    #         "ports": "ether1,ether2,ether3,ether4"
    #     },
    # ]

    result = dict(changed=False, to_add=to_add, to_update=to_update, to_remove=to_remove)

    module.exit_json(**result)

if __name__ == "__main__":
    main()
