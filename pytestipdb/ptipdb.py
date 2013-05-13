""" Interactive debugging with ipdb, the IPython Debugger. """
import inspect
import pytest, py
import sys
import traceback
import ipdb

def pytest_addoption(parser):
    group = parser.getgroup("general")
    group._addoption('--ipdb',
               action="store_true", dest="use_ipdb", default=False,
               help="Starts the interactive IPython debugger on errors.")

def pytest_namespace():
    return {'set_trace': PytestIpdb().set_trace}

def pytest_configure(config):
    if config.getvalue("use_ipdb"):
        config.pluginmanager.register(IpdbInvoker(), 'ipdbinvoker')

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
            out, err = capman.suspendcapture()
            if hasattr(item, 'outerr'):
                item.outerr = (item.outerr[0] + out, item.outerr[1] + err)
            tw = py.io.TerminalWriter()
            tw.line()
            tw.sep(">", "PDB set_trace (IO-capturing turned off)")
        frame = sys._getframe().f_back
        ipdb.set_trace(frame)

def ipdbitem(item):
    PytestIpdb.item = item

pytest_runtest_setup = pytest_runtest_call = pytest_runtest_teardown = ipdbitem

@pytest.mark.tryfirst
def pytest_make_collect_report(__multicall__, collector):
    try:
        PytestIpdb.collector = collector
        return __multicall__.execute()
    finally:
        PytestIpdb.collector = None

def pytest_runtest_makereport():
    PytestIpdb.item = None

class IpdbInvoker:
    @pytest.mark.tryfirst
    def pytest_runtest_makereport(self, item, call, __multicall__):
        rep = __multicall__.execute()
        if not call.excinfo or \
            call.excinfo.errisinstance(pytest.skip.Exception) or \
            call.excinfo.errisinstance(py.std.bdb.BdbQuit):
            return rep
        if hasattr(rep, "wasxfail"):
            return rep
        # we assume that the above execute() suspended capturing
        # XXX we re-use the TerminalReporter's terminalwriter
        # because this seems to avoid some encoding related troubles
        # for not completely clear reasons.
        tw = item.config.pluginmanager.getplugin("terminalreporter")._tw
        tw.line()
        tw.sep(">", "traceback")
        rep.toterminal(tw)
        tw.sep(">", "entering PDB")
        # A doctest.UnexpectedException is not useful for post_mortem.
        # Use the underlying exception instead:
        if isinstance(call.excinfo.value, py.std.doctest.UnexpectedException):
            tb = call.excinfo.value.exc_info[2]
        else:
            tb = call.excinfo._excinfo[2]

        post_mortem(tb)
        rep._ipdbshown = True
        return rep


def post_mortem(tb):
    import IPython
    try:
        stdout = sys.stdout
        frame = sys._getframe().f_back
        # The IPython API changed a bit so we should
        # support the new version
        stdout = sys.stdout
        sys.stdout = sys.__stdout__
        shell = IPython.InteractiveShell()
        ip = IPython.core.ipapi.get()
        p = IPython.core.debugger.Pdb(ip.colors)
        p.reset()
        # inspect.trace() returns a list of frame information from this
        # frame to the one that raised the exception being treated
        ### frame, filename, line, func_name, ctx, idx = inspect.trace()[-1]
        p.interaction(frame, tb)
    finally:
        sys.stdout = stdout
"""
def post_mortem(tb):
    pdb = py.std.pdb
    class Pdb(pdb.Pdb):
        def get_stack(self, f, t):
            stack, i = pdb.Pdb.get_stack(self, f, t)
            if f is None:
                i = max(0, len(stack) - 1)
                while i and stack[i][0].f_locals.get("__tracebackhide__", False):
                    i-=1
            return stack, i
    p = Pdb()
    p.reset()
    p.interaction(None, t)
"""
