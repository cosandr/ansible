def run(paths, hosts, shares=None, kwargs=None):
    """
    :param shares: Current list of shares
    :param paths: List of paths to share
    :param kwargs: Arguments to apply to models
    """
    model_tmpl = {
        "enabled": True,
        "comment": "",
        "hosts": [],
        "alldirs": True,
        "ro": False,
    }
    kwargs = kwargs or {}
    shares = shares or []
    state = kwargs.pop('state', 'present')
    for p in paths:
        model = model_tmpl.copy()
        model['paths'] = [p]
        model['hosts'] = hosts
        model.update(kwargs)
        shares.append({'model': model, 'state': state})
    return shares


class FilterModule(object):
     def filters(self):
        return {'create_nfs_models': run}
