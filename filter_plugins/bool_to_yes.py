def run(_input, default=''):
    """
    Return yes if _input is True, no if False
    do nothing otherwise

    Equivalent to jinja2:
    {% if _input is sameas true %}
    yes
    {% elif _input is sameas false %}
    no
    {% else %}
    {{ input }}
    {% endif %}
    """
    if _input is True:
        return 'yes'
    elif _input is False:
        return 'no'
    elif default:
        return default
    else:
        return _input

class FilterModule(object):
     def filters(self):
        return {'bool_to_yes': run}
