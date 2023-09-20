from ansible.errors import AnsibleFilterError
from netaddr import IPNetwork, spanning_cidr


def run(ips, host, query="", prefixlen=None):
    """Given a list of CIDRs, returns the nth host as if it was a single continous range
    Examples:
    ['10.0.50.0/28', '10.0.50.128/25'] | ipaddr_concat(15) => 10.0.50.15
    ['10.0.50.0/28', '10.0.50.128/25'] | ipaddr_concat(16) => 10.0.50.128
    ['10.0.50.0/28', '10.0.50.128/25'] | ipaddr_concat(15, 'address') => 10.0.50.15/28
    ['10.0.50.0/28', '10.0.50.128/25'] | ipaddr_concat(16, 'address') => 10.0.50.128/25
    """
    host = int(host)
    nets = []
    if isinstance(ips, list):
        # Create IPNetwork objects
        nets = [IPNetwork(v) for v in ips]
    else:
        nets = [IPNetwork(ips)]
    # Validate, ensure they're in the same network
    if len(nets) > 1 and spanning_cidr(nets).prefixlen == 0:
        raise AnsibleFilterError("ipaddr_concat: CIDRs span the entire address range")
    if prefixlen is not None:
        query = 'address'
    nets.sort()
    for n in nets:
        if host >= n.size:
            host -= n.size
            continue
        if query in ["", "host"]:
            return str(n[host])
        elif query == "address":
            return str(n[host]) + "/" + str(prefixlen or n.prefixlen)


class FilterModule(object):
    def filters(self):
        return {'ipaddr_concat': run}
