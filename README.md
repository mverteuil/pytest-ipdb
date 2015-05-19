pytest-ipdb
===========

NOTICE
======

I am no longer supporting this tool. Please see **pdb++** as a far more capable alternative that doesn't require plugins or special imports.

**pdb++**: https://pypi.python.org/pypi/pdbpp/ 


Provides ipdb on failures for py.test.

Installation and usage
----------------------

To install

    pip install git+git://github.com/mverteuil/pytest-ipdb.git
  
To use: run pytest with `--ipdb` instead of `--pdb`.

[![Build Status](https://travis-ci.org/mverteuil/pytest-ipdb.svg)](https://travis-ci.org/mverteuil/pytest-ipdb)

Now you can breakpoints in your in your code:

    import ipdb ; ipdb.set_trace()

... or ...:

    import pytest ; pytest.set_trace()

   
