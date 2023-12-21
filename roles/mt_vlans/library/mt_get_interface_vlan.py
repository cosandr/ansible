#!/usr/bin/env python3

from ansible.module_utils.basic import AnsibleModule


def main():
    argument_spec = dict(
        networks=dict(type="dict", required=True),
        bridge_name=dict(type="str", default="bridge1"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    networks = module.params["networks"]
    bridge_name = module.params["bridge_name"]

    new_data = []
    for net_name, net_config in networks.items():
        if "vlan" not in net_config:
            continue
        comment = []
        if "cidr" in net_config:
            comment.append(net_config["cidr"])
        if "cidr6" in net_config:
            comment.append(net_config["cidr6"])
        comment = "; ".join(comment)
        new_data.append(
            {
                "interface": bridge_name,
                "name": net_name.upper(),
                "vlan-id": net_config["vlan"],
                "mtu": net_config.get("mtu", 1500),
                "comment": comment or None,
            }
        )

    ## Expected output:
    # new_data = [
    #     {
    #         "interface": "bridge1",
    #         "name": "GENERAL",
    #         "vlan-id": 50
    #     },
    # ]

    result = dict(changed=False, new_data=new_data)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
