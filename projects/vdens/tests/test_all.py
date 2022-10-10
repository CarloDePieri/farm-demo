# test
import pytest
import pexpect

@pytest.mark.farm_group_1
def test_that_it_s_the_right_vm():

    child = pexpect.spawn("hostname")
    child.expect('\r\n')

    if isinstance(child.before, bytes):
        out = child.before.decode("utf-8")  # type: str
        assert out == "V2-20220101-874"
    else:
        assert False

@pytest.mark.farm_group_1
def test_that_fails():
    assert False

def test_that_it_does_not_run():
    # This has no group assigned, so it will not run
    assert False
