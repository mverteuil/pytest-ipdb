""" Interactive debugging with ipdb, the IPython Debugger. """
import inspect
import sys

import ipdb
import py
import pytest


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group._addoption('--ipdb',
               action="store_true", dest="use_ipdb", default=False,
               help="Starts the interactive IPython debugger on errors.")

def patch_ipdb(config):
    """patch ipdb.set_trace to first disable stdout capturing"""

    try:
        original_trace = ipdb.set_trace
    except AttributeError:
        # ipdb not installed
        return

    def cleanup():
        ipdb.set_trace = original_trace

    def set_trace(frame=None):
        # we don't want to drop in here, but at the point of the oriainal
        # set_trace statement
        if frame is None:
            frame = sys._getframe().f_back

        capman = config.pluginmanager.getplugin("capturemanager")
        if capman:
            # It might be not available, e.g. on pytest teardown.
            out, err = capman.suspend_global_capture(in_=True)
        original_trace(frame)

    py.std.ipdb.set_trace = set_trace
    config._cleanup.append(cleanup)


def pytest_configure(config):
    patch_ipdb(config)
    pytest.set_trace = PytestIpdb().set_trace
    if config.getvalue("use_ipdb"):
        config.pluginmanager.register(IpdbInvoke(), 'ipdbinvoke')


class PytestIpdb:
    """ Pseudo ipdb that defers to the real ipdb. """
    item = None
    collector = None

    def set_trace(self):
        """ invoke ipdb set_trace debugging, dropping any IO capturing. """
        frame = sys._getframe().f_back
        item = self.item or self.collector

        if item is not None:
            capman = item.config.pluginmanager.getplugin("capturemanager")
            out, err = capman.suspend_global_capture(in_=True)
            if hasattr(item, 'outerr'):
                item.outerr = (item.outerr[0] + out, item.outerr[1] + err)
            tw = py.io.TerminalWriter()
            tw.line()
            tw.sep(">", "PDB set_trace (IO-capturing turned off)")
        import ipdb
        ipdb.set_trace(frame)


def ipdbitem(item):
    PytestIpdb.item = item

pytest_runtest_setup = pytest_runtest_call = pytest_runtest_teardown = ipdbitem


class IpdbInvoke:
    def pytest_exception_interact(self, node, call, report):
        capman = node.config.pluginmanager.getplugin("capturemanager")
        if capman:
            capman.suspend_global_capture(in_=True)
        _enter_ipdb(node, call.excinfo, report)

    def pytest_internalerror(self, excrepr, excinfo):
        for line in str(excrepr).split("\n"):
            sys.stderr.write("INTERNALERROR> %s\n" %line)
            sys.stderr.flush()
        tb = _postmortem_traceback(excinfo)
        post_mortem(tb)


def _enter_ipdb(node, excinfo, rep):
    # XXX we re-use the TerminalReporter's terminalwriter
    # because this seems to avoid some encoding related troubles
    # for not completely clear reasons.
    tw = node.config.pluginmanager.getplugin("terminalreporter")._tw
    tw.line()
    tw.sep(">", "traceback")
    rep.toterminal(tw)
    tw.sep(">", "entering PDB")
    tb = _postmortem_traceback(excinfo)
    post_mortem(tb)
    rep._pdbshown = True
    return rep


def _postmortem_traceback(excinfo):
    # A doctest.UnexpectedException is not useful for post_mortem.
    # Use the underlying exception instead:
    from doctest import UnexpectedException
    if isinstance(excinfo.value, UnexpectedException):
        return excinfo.value.exc_info[2]
    else:
        return excinfo._excinfo[2]


def post_mortem(tb):
    import IPython
    stdout = sys.stdout
    try:
        sys.stdout = sys.__stdout__
        if hasattr(IPython, 'InteractiveShell'):
            if hasattr(IPython.InteractiveShell, 'instance'):
                shell = IPython.InteractiveShell.instance()
                p = IPython.core.debugger.Pdb(shell.colors)
            else:
                shell = IPython.InteractiveShell()
                ip = IPython.core.ipapi.get()
                p = IPython.core.debugger.Pdb(ip.colors)
        # and keep support for older versions
        else:
            shell = IPython.Shell.IPShell(argv=[''])
            ip = IPython.ipapi.get()
            p = IPython.Debugger.Pdb(ip.options.colors)
        p.reset()
        # inspect.getinnerframes() returns a list of frames information
        # from this frame to the one that raised the exception being
        # treated
        frame, filename, line, func_name, ctx, idx = inspect.getinnerframes(tb)[-1]
        p.interaction(frame, tb)
    finally:
        sys.stdout = stdout
