This document aim is to give an overview of the api offered
by the deploy\_farm collection.

This is only usefull to begin to understand what's going on under the hood; for
writing actual tests, take a look at the [readme in the provided example](projects/vdens/).

FIXME ^

#### Get the code

Since there's a submodule present, to clone this repo run:

```
git clone --recurse-submodules git@github.com:CarloDePieri/farm-demo.git
```
FIXME ^

# Farm library

These roles are currently under a git submodule in `test_farm/roles/`.

## Farm deploy roles

We define a virtual machine via `VM definitions`: they are objects that
describe the VM structure like machine, architecture, emulator, interfaces,
disks, and devices and the used operating system.

Each target and platform definitions can be defined into a respective definition
file in YAML format. Each generated `VM definition` is the merged result of both
type of definitions, including their variables, and it's provided as parameter
of the Hypervisor provisioning role.

- **platform**: synonym of OS; it's the definition of the used OS; it's also
  used to setup network, auth and fetch and install vm images and other assets
  from their URI.

- **target**: synonym of machine, architecture of machine; it's the definition
  of the architecture type used in each vm configuration, like CPU, machine type,
  emulator info, interfaces, devices, etc ...

These `VM definitions` are parsed by the `parse_vms_definition` utility role and
then used throughout the project by several roles.

### Hypervisor provisioning ([kvm\_provision](https://github.com/jjak0b/test_farm/tree/274053931fffdecac3744ffd4ab76ae6a5ec978e/roles/kvm_provision))

The hypervisor provisioning role deploy a list of virtual machines into the
hypervisor host through their respective `VM definitions` objects.

The Hypervisor provisioning role will fetch and install remote or local resources
required by each `VM definition`.

During the installation the `VM definition` object variables are used to compile
a [libvirt domain xml definition](https://libvirt.org/formatdomain.html) by
filling in a [jinja template](https://jinja.palletsprojects.com/en/3.1.x/templates/#template-designer-documentation).
The user, when writing tests, can specify and expand these templates.

The platforms, target definitions and templates are defined respectively in the
`platforms`, `targets` and `templates` sub folders inside the a setup vm folder
defined by the user in the actual test.

The use can futhermore define the network the vms will use by leveraging the
`libvirt_network` role. This also includes DHCP entries for the vms.

### Guest provisioning ([guest\_provision](https://github.com/jjak0b/test_farm/tree/274053931fffdecac3744ffd4ab76ae6a5ec978e/roles/guest_provision))

The Guest provisioning role distributes and runs tasks split into provisioning
phases for each VM host.

The role loops on a vm group defined by the user. It starts the vm and the run
the following phases:

- dependencies
- init
- main
- terminate

Each phase is associated with its respective YAML file which contains the user
defined list of tasks to run during that phase. It's possibile to specifically
define a phase file for:

- a target of a specific platform
- any target for a specific platfor
- any platform

The tasks of the most specific phase file will be used as phase tasks, overwriting
less specific files.

When the execution of the terminate phase ends, then the VM gets shutdown
(unless otherwise specified).

## Farm test roles

These are currently located under the [roles](roles) folder. They provide an easy way to launch
automated tests.

### Install the test suite dependencies ([setup\_test\_suite](roles/setup_test_suite))

Its first task is to install all test suite dependencies in the guest vm; it
then proceeds to prepare the folder structure needed to execute tests.

### Execute the test suite on the vm ([launch\_test\_suite](roles/launch_test_suite))

After copying all test files into the guest vm, it launches the test suite.
A `junit2 xml` file and an `html` file are produced by this process which are
eventually copied back to the hypervisor host.
