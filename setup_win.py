# setup_win.py

from distutils.core import setup
import py2exe


options = {"py2exe": {
    "compressed": 1,
    "optimize": 2,
    "bundle_files": 1
}}

setup(windows=["main.py"], options=options, zipfile=None)
