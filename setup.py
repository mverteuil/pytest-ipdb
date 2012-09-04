from setuptools import setup

setup(
    name="pytest-ipdb",
    packages = ['pytestipdb'],

    # the following makes a plugin available to py.test
    entry_points = {
        'pytest11': [
            'pytestipdb = pytestipdb.ipdb',
        ]
    },
)
