# -*- coding: utf-8 -*-

pytest_plugins = "pytester"


class Option(object):
    def __init__(self, no_ipdb=False):
        self.no_ipdb = no_ipdb

    @property
    def args(self):
        if self.no_ipdb:
            l = ['--pdb']
        else:
            l = ['--ipdb']
        return l


def pytest_generate_tests(metafunc):
    if "option" in metafunc.fixturenames:
        metafunc.addcall(id="default",
                         funcargs={'option': Option(no_ipdb=False)})
        metafunc.addcall(id="no_ipdb",
                         funcargs={'option': Option(no_ipdb=True)})


def test_post_mortem(testdir, option):
    testdir.makepyfile(
        """
        def test_func():
            assert 0
        """
    )

    result = testdir.runpytest(*option.args)

    if option.no_ipdb:
        result.stdout.fnmatch_lines(['(Pdb) '])
    else:
        result.stdout.fnmatch_lines(['ipdb> '])


def test_pytest_set_trace(testdir, option):
    testdir.makepyfile(
        """
        import pytest

        def test_func():
            pytest.set_trace()
        """
    )

    result = testdir.runpytest(*option.args)

    if option.no_ipdb:
        result.stdout.fnmatch_lines(['(Pdb) '])
    else:
        result.stdout.fnmatch_lines([
            '*PDB set_trace (IO-capturing turned off)*',
            'ipdb> ',
        ])


def test_ipdb_set_trace(testdir, option):
    testdir.makepyfile(
        """
        import ipdb

        def test_func():
            ipdb.set_trace()
        """
    )

    result = testdir.runpytest(*option.args)

    if option.no_ipdb:
        result.stdout.fnmatch_lines([
            "*AttributeError: DontReadFromInput instance has no attribute 'encoding'",
        ])
    else:
        result.stdout.fnmatch_lines([
            'ipdb> ',
        ])
