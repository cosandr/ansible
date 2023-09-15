import re


def get_vlan_entry(data, entry, check_key):
    for d in data:
        if d.get(check_key) == entry[check_key]:
            return d
    return None


def entries_eq(old, new):
    for k, v in new.items():
        if k not in old:
            return False
        if old[k] != v:
            return False

    return True


def make_vid_map(networks):
    vid_map = {}
    for name, cfg in networks.items():
        if 'vlan' not in cfg:
            continue
        vid_map[name.upper()] = cfg['vlan']
    return vid_map


def make_add_update_remove(existing, new_data, check_key):
    to_add = []
    to_update = []
    to_remove = []

    for d in existing:
        if not get_vlan_entry(new_data, d, check_key):
            to_remove.append(d)

    for d in new_data:
        old = get_vlan_entry(existing, d, check_key)
        if not old:
            to_add.append(d)
        elif not entries_eq(old, d):
            # Add ID for faster editing
            d['.id'] = old['.id']
            to_update.append(d)

    return to_add, to_update, to_remove


def sort_trunks(trunk_ports, switch_cpu):
    """Sort like source data: switch, ether, sfpplus, sfp-sfpplus"""
    tmp = ','.join(trunk_ports)
    ether = re.findall(r'(ether\d+)', tmp)
    sfpplus = re.findall(r'[^-](sfpplus\d+)', tmp)
    sfp = re.findall(r'(sfp-sfpplus\d+)', tmp)
    return [switch_cpu] + ether + sfpplus + sfp
