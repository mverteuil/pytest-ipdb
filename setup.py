from setuptools import setup

setup(
    name="pytest-ipdb",
    packages=["pytestipdb"],
    version="0.1-prerelease2",
    description="A py.test plug-in to enable drop to ipdb debugger on test failure.",
    author="Matthew de Verteuil",
    author_email="onceuponajooks@gmail.com",
    url="https://github.com/mverteuil/pytest-ipdb",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Testing",
    ],
    install_requires=[
        'pytest',
        'ipdb',
    ],
    # the following makes a plugin available to py.test
    entry_points = {
        "pytest11": [
            "pytestipdb = pytestipdb.ptipdb",
        ]
    },
)
