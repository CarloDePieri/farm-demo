# Copyright: (c) 2021, Carlo De Pieri <depieri.carlo@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
import configparser
import re
from pathlib import Path
from typing import Dict, List, Union

from ansible.module_utils.basic import AnsibleModule


__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_farm_test_groups

short_description: Parse a pytest.ini file and return a list of markers matching r"^farm_group_\d*:".

version_added: "1.0.0"

description: Parse a pytest.ini file and return a list of markers matching r"^farm_group_\d*:".

options:
    pytest_ini:
        description: the path to the pytest.ini file that will be parsed. Default: tests/pytest.ini
        required: false
        type: str

author:
    - Carlo De Pieri (@CarloDePieri)
'''

EXAMPLES = r'''
- name: Get all farm test groups, looking for the pytest.ini locally, at the default path.
  get_farm_test_groups:
  register: farm_test_groups
  delegate_to: localhost

- name: Get all farm test groups, looking for the pytest.ini in a particular remote path.
  get_farm_test_groups:
    pytest_ini: /test/tests/pytest.ini
  register: farm_test_groups
'''

RETURN = r'''
groups:
    description: A list of collected group names
    type: List[str]
    returned: always
    sample: ['farm_group_1', 'farm_group_2']
'''


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        pytest_ini=dict(type='str', required=False, default="tests/pytest.ini"),
    )

    # seed the result dict in the object
    # we primarily care about changed and groups
    # changed is set if this module effectively modified the target (which, in this case, it won't)
    # groups will contain every group name parsed from the pytest.ini file
    result: Dict[str, Union[bool, List[str]]] = dict(
        changed=False,
        groups=[],
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    try:
        pytest_ini = module.params['pytest_ini']

        ini = Path(pytest_ini)
        if not ini.exists():
            raise Exception(f"ini file not found at {ini.absolute()}")

        config = configparser.ConfigParser()
        config.read(ini)

        reg = r"^(farm_group_\d*):"
        matches = re.finditer(reg, config['pytest']['markers'], re.MULTILINE)
        for m in matches:
            result['groups'].append(m[1])

    except Exception as e:
        # during the execution of the module, if there is an exception or a
        # conditional state that effectively causes a failure, run
        # AnsibleModule.fail_json() to pass in the message and the result
        module.fail_json(msg=f"Could not parse test groups: {e}", **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
