'''
Urial: URI Addition tooL

Copyright 2024 Michael Hucka.

Licensed under the MIT License – see file "LICENSE" in the project website.
For more information, please visit https://github.com/mhucka/urial
'''

# Package metadata ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#  ╭────────────────────── Notice ── Notice ── Notice ─────────────────────╮
#  |    The following values are automatically updated at every release    |
#  |    by the Makefile. Manual changes to these values will be lost.      |
#  ╰────────────────────── Notice ── Notice ── Notice ─────────────────────╯

__program__     = 'urial'
__version__     = '1.2.1'
__description__ = 'Add/update URIs in macOS Finder comments'
__url__         = 'https://github.com/mhucka/urial'
__author__      = 'Michael Hucka'
__email__       = 'mhucka@caltech.edu'
__license__     = 'https://github.com/mhucka/urial/blob/main/LICENSE'


# Miscellaneous utilities.
# .............................................................................

def print_version():
    print(f'{__program__} version {__version__}')
    print(f'Authors: {__author__}')
    print(f'URL: {__url__}')
    print(f'License: {__license__}')
