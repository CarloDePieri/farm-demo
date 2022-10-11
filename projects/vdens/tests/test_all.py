# test
import pytest
import pexpect


def bash(cmd: str) -> pexpect.spawn:
    """Execute the provided command in a bash subshell."""
    return pexpect.spawn("/bin/bash", ["-c", cmd])


def test_that_vdens_works_as_expected():
    """Test that vdens works as expected.

    This reproduce the test found at:
        http://wiki.virtualsquare.org/#!tutorials/vde_ns.md#Scenario:_two_vdens_and_a_switch
    """

    # Spawn the vde_plug switch in a first subshell
    # I will not need to interact again with this shell so I can assign this spawn object to _
    # NOTE: it MUST be assigned to a variable anyway
    _ = bash("vde_plug null:// switch:///tmp/mysw")

    # Spawn the first vdens in another subshell
    ns_a = bash("vdens vde:///tmp/mysw")

    # Configure the first namespace
    ns_a.expect("net_raw# ")
    ns_a.send("ip addr add 10.0.0.10/24 dev vde0\r")
    ns_a.expect("net_raw# ")
    ns_a.send("ip link set vde0 up\r")
    ns_a.expect("net_raw# ")

    # Spawn the second vdens
    ns_b = bash("vdens vde:///tmp/mysw")

    # Configure the second namespace
    ns_b.expect("net_raw# ")
    ns_b.send("ip addr add 10.0.0.11/24 dev vde0\r")
    ns_b.expect("net_raw# ")
    ns_b.send("ip link set vde0 up\r")
    ns_b.expect("net_raw# ")

    # Send a ping from the second ns to the first
    ns_b.send("ping -c 1 10.0.0.10\n")


    # Expect either the string '1 received' or a TIMEOUT
    result_index = ns_b.expect(
            ["1 received", pexpect.TIMEOUT],
            timeout=3)

    # If the expect encountered a timeout, fail with a relevant error message
    if result_index == 1:
        pytest.fail("Ping timed out")


def test_that_fails():
    assert False
