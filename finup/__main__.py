'''
finup: Finder comment replacement utility

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2021 by Michael Hucka and the California Institute of Technology.
This code is open-source software released under a 3-clause BSD license.
Please see the file "LICENSE" for more information.
'''

import sys
if sys.version_info <= (3, 8):
    print('finup requires Python version 3.8 or higher,')
    print('but the current version of Python is ' +
          str(sys.version_info.major) + '.' + str(sys.version_info.minor) + '.')
    exit(1)

# Note: this code uses lazy loading.  Additional imports are made below.
import plac
from   finup import print_version, __program__


# Main body.
# .............................................................................

@plac.annotations(
    no_gui     = ('do not use macOS GUI dialogs',                 'flag',   'G'),
    overwrite  = ('forcefully overwrite previous Finder comment', 'flag',   'o'),
    version    = ('print program version info and exit',          'flag',   'V'),
    debug      = ('log debug output to "OUT" ("-" is console)',   'option', '@'),
    args       = 'a string (assumed to be a URI) followed by a file name',
)

def main(no_gui = False, overwrite = False, version = False, debug = 'OUT', *args):
    '''Add or update a URI in a Finder comment.

This program expects to be given at least two argument values.  The first
value is taken to be a string containing a URI, and the second value is the
path of a file whose Finder comment should be updated with the given string.

By default, if the Finder comment of the file already has any value, it is
only modified to update the substring that has the same type of URI, and then
only if the Finder comment contains such a substring.  For example, if the file
"somefile.md" contains a Finder comment with an existing x-devonthink-item
URI inside of it, then the following command,

  finup "x-devonthink-item://8A1A0F18-068680226F3" somefile.md

will rewrite the URI part of the comment to have the new URI given in the.
command.  If the Finder comment is empty, then the given URI is written as a
new comment.  If the Finder comment is not empty but does not contain a URI
of the same kind as the one given on the command line, then the Finder
comment is not changed at all unless the --overwrite option is given, in which
case, the ENTIRE Finder comment is replaced with just the URI string given on
the command line.
'''

    # Process arguments & handle early exits ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if version:
        print_version()
        sys.exit(0)

    if len(args) < 2:
        fatal('Must be given two arguments: a URI and a file path', no_gui)
        sys.exit(1)



# Miscellaneous helpers.
# .............................................................................


def alert(msg, no_gui, use_system = False):
    if no_gui:
        print('‼️  ' + msg)
    else:
        from osax import OSAX
        sa = OSAX("StandardAdditions",
                  name = "System Events" if use_system else "DEVONthink 3")
        sa.activate()
        sa.display_alert(__program__, buttons = ["OK"], message = msg)


def fatal(msg, no_gui, use_system = False):
    alert(msg, no_gui, use_system)
    sys.exit(1)


# Main entry point.
# .............................................................................

# The following entry point definition is for the console_scripts keyword
# option to setuptools.  The entry point for console_scripts has to be a
# function that takes zero arguments.
def console_scripts_main():
    main()

# The following allows users to invoke this using "python3 -m finup".
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'help':
        plac.call(main, ['-h'])
    else:
        plac.call(main)
    main()


# For Emacs users
# .............................................................................
# Local Variables:
# mode: python
# python-indent-offset: 4
# End:
