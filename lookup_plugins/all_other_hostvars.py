from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: all_other_hostvars
    author: Andrei Costescu (@cosandr)
    version_added: "1.0"
    short_description: read specific hostvar from all others hosts
    description:
      - This lookup returns a list of all hostvars from other hosts.
    options:
      _terms:
        description: hostvar(s) to read
        required: True
      exclude:
        description:
          - Hosts to exclude from search.
        type: string
        default: self
      type:
        description:
          - Fail if vars are not this type.
        type: string
        default: list
      defaults:
        description:
          - Set default vars for each entry.
          - hv_ prefix will fetch from each host's vars.
        type: dict
        default: {}
"""

EXAMPLES = """
- name: fetch mt_dns_entries from all other hosts
  ansible.builtin.debug:
    msg: "{{ lookup('all_other_hostvars', 'mt_dns_entries') }}"
"""

from pydoc import locate

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display


display = Display()


class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):

        ret = []

        self.set_options(var_options=variables, direct=kwargs)

        exclude = self.get_option('exclude')
        if exclude == "self":
            exclude = variables['inventory_hostname']

        # Cast to actual type object
        want_type = locate(self.get_option('type'))
        if want_type is None:
            raise AnsibleLookupError("Unknown type %s" % self.get_option('type'))

        # TODO: Consider supporting other types
        if want_type is not list:
            raise AnsibleLookupError('Only list type is supported for now.')

        defaults = self.get_option('defaults')

        for term in terms:
            tmp = []
            for name, hv in variables['hostvars'].items():
                if name == exclude:
                    continue
                entries = hv.get(term)
                # Ignore empty
                if not entries:
                    continue
                if not isinstance(entries, want_type):
                    raise AnsibleLookupError("Found wrong type for host '%s', check for undefined variables" % name)
                if isinstance(entries, list):
                    for e in entries:
                        for k, v in defaults.items():
                            if isinstance(v, str) and v.startswith('hv_'):
                                var_name = v.split('hv_', 1)[1]
                                v = hv.get(var_name)
                                if v is None:
                                    raise AnsibleLookupError("%s is not defined for %s" % (var_name, name))
                            if k not in e:
                                e[k] = v
                        tmp.append(e)
            ret.append(tmp)

        return ret
