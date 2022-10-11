This is an example of a project test. In here both the actual tests and the
definitions of the needed vms are present.

# Usage

### Setup

All requirements can be found in the [test\_farm README](https://github.com/jjak0b/test_farm#requirements).

### Run

Execute:

```shell
ansible-playbook main.yaml -K
```

This will go trough all provision and test phases and will result in two
files in a `out` folder:

- `out.xml`: a `junit2` file containing all tests results; this includes
failed tests with their stack trace;

- `out.html`: included only for this demo, it's a possible way to visualize
the test data contained in the `out.xml` output file (produced by
[junit2html](https://pypi.org/project/junit2html/)).

# Project structure

This is a somewhat minimal example that includes one vm definition (a
virtualsquare vm on a KVM x86\_64 machine) and a `pytest`/`pexpect` test that reproduce
a [v2 wiki test](http://wiki.virtualsquare.org/#!tutorials/vde_ns.md#Scenario:_two_vdens_and_a_switch).

## Test lifecycle

![uhm](../../docs/images/test-lifecycle.png)

The first step is to prepare the vm matrix definition (we just
have one vm, here); then, for each defined vm, the main test loop is started.

After provisioning and booting the vm, the first libvirt snapshot (called
`clean`) is taken. This will come in handy to clean the slate after a failure in
preparing the vm in the next phase.

During the `dependencies` and `init` phases, all required test dependencies are installed
in the vm. If successful another snapshot is taken, called `init`: it can be
used by the test if it needs to start from a safe point (but with all the dependencies
already installed!).

The `main` phase is responsible to run the actual tests: this may include compiling
from the source code, launching the test suite, recovering tests output, etc.

Just before shutting down the vm, the `terminate` phase will take care of
eventual clean ups.

## The entrypoint: [main.yaml](main.yaml)

This playbook takes care of parsing vms definitions, provisioning them and run
all tests phases. This is accomplished by using several Test Deploy roles:

- `parse_vms_definition` simply parses all definition files;

- `init_vm_connection` add all defined vms to the ansible inventory;

- `kvm_provision` create the vm;

- `guest_provision` is responsible of starting the vm, handling the snapshot, starting
  the test phases and finally shutting down the vm.

## Farm setup and VMs Definitions

### setup\_hypervisor

This folder contains the hypervisor related tasks about its setup.

- `networks`: contains the yaml network definitions (and eventually the XML
libvirt template it uses) that the VM needs to be defined on the libvirt env
during the setup.

### vms\_config.yaml

It's the YAML file containing the `VM configurations` matrix of `platforms` and
`targets`. Storing this into a file it's a convenient way to store the `VM configurations`
and importing them inside the playbook.

- The property `permutations` specify the values of `platforms` and `targets` names
used to create all possibile `(platform, target)` tuples.
- The property `definitions` specify a list of `(platform, target)` or `(platform,
target, template)` tuples;

### setup\_vm

This folder contains the `platform` and `target` definitions files use by the
`parse_vms_definitions` role to parse define the `VM definitions` object, and the
`template` files used by the `kvm_provision` role to generate the VM according to
it's specified template.
If no template name is specified inside the `VM definition`, then the `default`
template will be used.
Each definition and template file is respectively placed inside the `platforms`,
`targets` and `template` folder.

### group\_vars

This folder is used by Ansible to assign variable to inventory groups. It can also
define global variable (like the one in [all.yaml](group_vars/all.yaml)).
This is usefull to [override or set](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#understanding-variable-precedence)
ansible auth and connection variables based on the VM group.

## Test phases

This specific test utilizes only the `init` and the `main` phases.

### [init.yaml](provision_phases/init.yaml)

All dependencies for the test are installed in here. This includes:

- upgrading the image packages;
- installing the virtualsquare packages and projects with the `get_v2all` tool;
- install all python dependencies for the test suite via the `setup_test_suite` role.

### [main.yaml](provision_phases/main.yaml)

In here the pytest test suite is launched in the vm guest, by passing to the
`launch_test_suite` role the path of the test suite folder.

## Pytest/Pexpect tests ([tests](tests/) folder)

[Pytest](https://docs.pytest.org/en/7.1.x/getting-started.html) is a python framework
for writing test.
[Pexpect](https://pexpect.readthedocs.io/en/stable/index.html) is a python library
that allows to control other applications.
Together, they are the main tools employed by the Farm Test roles.

### pytest

Pytest is really simple to [get started with](https://docs.pytest.org/en/7.1.x/getting-started.html#get-started)
but can also scale to handle complex use cases if needed be.

A pytest test is as simple as a python function whose name starts with `test_`,
like [this dummy test](https://github.com/CarloDePieri/farm-demo/blob/15e454633aed3d8d61e1f7a3d94dc26564d31b09/projects/vdens/tests/test_all.py#L57),
contained in a file whose name itself starts with `test_`.

The main instrument to make assertions is `assert <boolean expression>`.
A test *passes* if the function does not raise any exception or it *fails*
otherwise. The aforementioned test *fails* since it asserts a falsy value (hence
raising an `AssertionError`); this test is included to showcase how the test suite
handles failures.

The [main test](https://github.com/CarloDePieri/farm-demo/blob/15e454633aed3d8d61e1f7a3d94dc26564d31b09/projects/vdens/tests/test_all.py#L11)
should *pass* instead, since it should return `None` if everything goes correctly
and the last `if` block is not entered.

The test suite will try to launch all provided tests, logging failures and
successes alike. The output is a `junit2` standard file, which is a broadly used
format. This allows to easly process and dispaly reports while maintaining access
to all the important informations (eg. why a test failed, via it's stack trace).

### pexpect

The [main test](https://github.com/CarloDePieri/farm-demo/blob/15e454633aed3d8d61e1f7a3d94dc26564d31b09/projects/vdens/tests/test_all.py#L11)
(which is thoroughly commented) simulates the interaction between two distinct
terminals using `pexpect`.

The principal pattern adopted by `pexpect` consist in calling `spaw(cmd)` to launch an
interactive command and then alternate between
`expect(['alternative1', 'alternative2', ...])` and `send("keys")` to respectively
expect a specific response by the launched application or sending an input to it.

The use of timeouts when expecting a response allows to model the test behaviour
if no response is coming back at all.
