from ansible.utils.display import Display
from netaddr import IPNetwork
from copy import deepcopy


def split_network_v4(n, no_clients):
    """Returns IPv4 subnets from a CIDR"""
    if n.prefixlen > 24:
        Display().warning("default_subnet: '{}' too small".format(str(n)))
        return {}
    tmp = {
        "switches": [
            str(list(n.subnet(28))[0]),
        ],
        "hosts": [
            str(list(n.subnet(28))[1]),
        ],
        "vips": [
            str(list(n.subnet(27))[1]),
        ],
    }
    if not no_clients:
        tmp["clients"] = [
            str(list(n.subnet(26))[1]),
            str(list(n.subnet(25))[1]),
        ]
    return tmp


def split_network_v6(n, no_clients):
    """Returns IPv6 subnets from a CIDR"""
    if n.prefixlen != 64:
        Display().warning("default_subnet: '{}' must be of size /64".format(str(n)))
        return {}
    subnets = list(n.subnet(80, 4))
    tmp = {
        "switches": [
            str(subnets[0]),
        ],
        "hosts": [
            str(subnets[1]),
        ],
        "vips": [
            str(subnets[2]),
        ],
    }
    if not no_clients:
        tmp["clients"] = [
            str(subnets[3]),
        ]
    return tmp


def merge_dicts(one, two):
    ret = deepcopy(one)
    for k, v in two.items():
        if k in ret:
            ret[k] += v
        else:
            ret[k] = v
    return ret


def run(network_defs, no_clients=None):
    """Generates the default subnet layout
    Input:
    "internal_net": {
        "ceph": {
            "cidr": "10.0.23.0/24",
            "cidr6": "fd00:23::0/56",
            "vlan": 23
        }
    }
    Output:
    "ceph": {
        "clients": [
            "10.0.23.64/26",
            "10.0.23.128/25",
            "fd00:23:0:3::/64"
        ],
        "hosts": [
            "10.0.23.16/28",
            "fd00:23:0:1::/64"
        ],
        "switches": [
            "10.0.23.0/28",
            "fd00:23::/64"
        ],
        "vips": [
            "10.0.23.32/27",
            "fd00:23:0:2::/64"
        ]
    }
    """
    ret = {}
    no_clients = no_clients or []
    for k, v in network_defs.items():
        k_nc = no_clients is True or k in no_clients
        v4_dict = {}
        v6_dict = {}
        if "cidr" in v:
            v4_dict = split_network_v4(IPNetwork(v["cidr"]), k_nc)
        if "cidr6" in v:
            v6_dict = split_network_v6(IPNetwork(v["cidr6"]), k_nc)
        ret[k] = merge_dicts(v4_dict, v6_dict)
    return ret



class FilterModule(object):
    def filters(self):
        return {'default_subnet': run}
