#!/usr/bin/env python3
# Summary: installation setup file for Urial.
#
# Note: configuration metadata is maintained in setup.cfg.  This file exists
# primarily to hook in setup.cfg and requirements.txt.

# Copyright 2024 Michael Hucka.
# License: MIT License – see file "LICENSE" in the project website.
# Website: https://github.com/mhucka/urial

import os
from   os import path
from   setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'requirements.txt')) as f:
    reqs = f.read().rstrip().splitlines()

setup(
    setup_requires = ['wheel'],
    install_requires = reqs,
)
