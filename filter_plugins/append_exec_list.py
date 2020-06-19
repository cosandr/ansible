def run(_list, name, exec_cmd):
    """
    :param _list: Current list
    :param name: Name of unit
    :param exec_cmd: Command to execute
        Can have quotes, might be launching a subshell, etc.
    
    :return: The list with the following format
    [
        {
            "name": <name>,
            "paths": [
                ...,
                "<exec_cmd without arguments>"
            ]
        }
    ]
    """
    # Don't add shell commands
    # Could try to parse them in the future
    # but for now just skip them
    if exec_cmd.startswith(('bash', 'sh')):
        return _list
    # We only care about the base command
    exec_cmd = exec_cmd.split(' ')[0]
    for _d in _list:
        if name == _d['name']:
            if exec_cmd not in _d['paths']:
                _d['paths'].append(exec_cmd)
            return _list
    _list.append({'name': name, 'paths': [exec_cmd]})
    return _list

class FilterModule(object):
     def filters(self):
        return {'append_exec_list': run}
