Usage
-----

### Hypervisor and VM provisioning
```
ansible-playbook main.yaml -K
```
The `-K` may be required when using `roles/kvm_provision` because
`setup_hypervisor/prerequisite/targets/<arch_name>.yml` try to install emulator
dependencies on hypervisor host.

