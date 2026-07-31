# Ansible 14

https://docs.ansible.com/projects/ansible/latest/porting_guides/porting_guide_core_2.19.html

https://docs.ansible.com/projects/ansible/latest/porting_guides/porting_guide_12.html
https://docs.ansible.com/projects/ansible/latest/porting_guides/porting_guide_13.html
https://docs.ansible.com/projects/ansible/latest/porting_guides/porting_guide_14.html

### Broken conditionals

`rg -n -U -P '^([ \t]*)when:[ \t]*(\n(\1[ \t]+\S.*)?)*'`

Keep an eye on warning and remove `allow_broken_conditionals` from ansible.cfg when done.

