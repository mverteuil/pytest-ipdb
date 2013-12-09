"""set_trace() should drop us into an ipdb debugger

(not break with
    AttributeError: DontReadFromInput instance has no attribute 'encoding'
)
"""

def test_ipdb_set_trace():
    print "foo"

    # press 'c' to complete test
    import ipdb
    ipdb.set_trace()


def test_pytest_set_trace():
    print "foo"

    # press 'c' to complete test
    import pytest
    pytest.set_trace()
