from math import log2, trunc
from netaddr import IPNetwork
from ansible.errors import AnsibleFilterError


def net_overlaps(net, others):
    for o in others:
        if net in o or o in net:
            return True
    return False


def prefix_from_diff(net, diff):
    if net.version == 4:
        return 32 - diff
    return 128 - diff


def next_of_size(net, subnets, size, start=0):
    for sub in net.subnet(size):
        if not net_overlaps(sub, subnets) and sub.first > start:
            return sub
    raise AnsibleFilterError("cidrsubnets: '{}' is too small".format(str(net)))


def fill_remaining(net, subnets, start=0):
    if not subnets:
        return [net]
    subnets = sorted(subnets)
    size = 0
    # Look for gaps at the end
    gap = abs(net.last - subnets[-1].last)
    if gap > 1:
        size = prefix_from_diff(net, trunc(log2(gap)))
    else:
        # Look for gaps in the middle
        for i in range(len(subnets) - 1):
            gap = abs(subnets[i].last - subnets[i+1].first)
            if gap > 1:
                if start > 0 and subnets[i].last < start:
                    continue
                size = prefix_from_diff(net, trunc(log2(gap)))
                break
    if size > 0:
        subnets.append(next_of_size(net, subnets, size, start))
        # Try again in case there are more
        return fill_remaining(net, subnets, start)
    return subnets


def run(net, *prefixes, fill=False, fill_only_end=True):
    """
    Input: {{ '10.0.50.0/24' | cidrsubnets(29, 30, 28, fill=true) }}
    Output:
    [
        "10.0.50.0/29",
        "10.0.50.8/30",
        "10.0.50.16/28",
        "10.0.50.32/27",
        "10.0.50.64/26",
        "10.0.50.128/25"
    ]
    """
    net = IPNetwork(net)
    subnets = []
    for p in prefixes:
        subnets.append(next_of_size(net, subnets, p))
    if fill:
        start = 0
        if fill_only_end and subnets:
            start = subnets[-1].last
        subnets = fill_remaining(net, subnets, start)
    return [str(s) for s in subnets]


class FilterModule(object):
    def filters(self):
        return {'cidrsubnets': run}
