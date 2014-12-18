pytest-ipdb
===========

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

   
