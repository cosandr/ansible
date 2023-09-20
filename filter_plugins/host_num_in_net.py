from ansible.errors import AnsibleFilterError
from netaddr import IPNetwork, IPAddress


def run(address, net=None):
    """Return address's number in net, if not given it assumes /24 and /64 for IPv4 and IPv6 respectively"""
    address = IPAddress(address)
    if net is not None:
        net = IPNetwork(net)
    elif address.version == 4:
        net = IPNetwork(str(address) + "/24")
    elif address.version == 6:
        net = IPNetwork(str(address) + "/64")
    else:
        raise AnsibleFilterError("host_num_in_net: Unknown error, cannot determine network")
    if address not in net:
        raise AnsibleFilterError("host_num_in_net: Address '{0}' is not in network '{1}'".format(str(address), str(net)))
    return int(address) - net.first


class FilterModule(object):
    def filters(self):
        return {'host_num_in_net': run}
