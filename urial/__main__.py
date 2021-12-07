'''
urial: URI Addition tooL

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
    print('urial requires Python version 3.8 or higher,')
    print('but the current version of Python is ' +
          str(sys.version_info.major) + '.' + str(sys.version_info.minor) + '.')
    exit(1)

# Note: this code uses lazy loading.  Additional imports are made below.
import plac
from   sidetrack import set_debug, log


# Main body.
# .............................................................................

@plac.annotations(
    no_gui  = ('do not use macOS GUI dialogs',                     'flag',   'G'),
    mode    = ('what to do if comment exists (see help for info)', 'option', 'm'),
    version = ('print program version info and exit',              'flag',   'V'),
    debug   = ('log debug output to "OUT" ("-" is console)',       'option', '@'),
    args    = 'a URI followed by a file name',
)

def main(no_gui = False, mode = 'M', version = False, debug = 'OUT', *args):
    '''Add or update a URI in a Finder comment.

This program expects to be given at least two argument values.  The first
value is taken to be a string containing a URI, and the second value is the
path of a file whose Finder comment should be updated with the given string.
Optional arguments begin with dashes and modify the program's behavior.

By default, if the Finder comment of the file already has any value, it is
only modified to update the substring that has the same type of URI, and then
only if the Finder comment contains such a substring.  For example, if the file
"somefile.md" contains a Finder comment with an existing x-devonthink-item
URI inside of it, then the following command,

  urial "x-devonthink-item://8A1A0F18-068680226F3" somefile.md

will rewrite the URI part of the comment to have the new URI given on the
command line.  If the Finder comment is not empty but does not contain a URI
of the same kind as the one given on the command line, then the Finder comment
is not changed unless a suitable value for the option --mode is given (see below).

Handling existing Finder comments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the file already has a Finder comment, the default behavior of urial is to
first check if the comment contains a URI of the same scheme as the given URI;
if it does, urial replaces the URI (and just the URI) substring in the Finder
comment, and if it does not, urial appends the URL to the comment.  The --mode
option can be used to change this behavior, as follows:

  append:    if the URI is NOT found in the Finder comment string, append the
             given URI to the end of the comment; otherwise (if the comment
             string already contains the URI) do nothing

  overwrite: overwrite the Finder comment completely with the given URI string,
             no matter what the Finder comment string contains (even if it
             already contains the given URI)

  update:    (default) if a URI of the same kind exists in the comment,
             replace only the URI portion of the comment string (preserving
             the rest of the comment string), else (if a URI is NOT found in
             the comment string) do nothing

Note that the behavior of "--mode overwrite" is to replace unconditionally the
entire Finder comment.  In other words, "-- mode overwrite" will change a
Finder comment such as

    Blah blah blah. URI. More blah blah blah.

to just

    URI

assuming that "URI" is the URI given to urial on the command line.  If you want
to update the URI to a new value and leave the other comment text in place,
use "--mode update" or simply don't provide a value for --mode (because
update is the default action).

Additional command-line arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If given the --version option, this program will print the version and other
information, and exit without doing anything else.

By default, this program will use macOS dialogs to report errors or other
issues.  The option --no-gui will make it print messages only on the command
line, without using GUI dialogs.

If given the --debug argument, this program will output a detailed trace of
what it is doing. The trace will be sent to the given destination, which can
be '-' to indicate console output, or a file path to send the output to a file.

Command-line arguments summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

    # Process arguments & handle early exits ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if debug != 'OUT':
        set_debug(True, debug)

    if version:
        from urial import print_version
        print_version()
        sys.exit(0)

    if len(args) < 2:
        fatal('Must be given at least two arguments: a URI and a file path.', no_gui)

    uri = args[0]
    scheme, rest = parsed_uri(uri)
    if not scheme:
        fatal(f'Could not interpret argument value "' + uri + '" as a URI.', no_gui)

    mode = 'update' if mode == 'M' else mode
    if not mode in ['update', 'append', 'overwrite']:
        fatal(f'Unrecognized mode value: {mode}')

    from os.path import exists
    file = args[1]
    if not exists(file):
        fatal(f'File does not appear to exist: "{file}"', no_gui)

    # Do the real work --------------------------------------------------------

    import appscript
    import mactypes
    try:
        log('telling Finder to open file ' + file)
        finder = appscript.app('Finder')
        finder_file = finder.items[mactypes.Alias(file)]
        comment = finder_file.comment()
        if not comment:
            log('file has no comment, so writing ' + uri)
            finder_file.comment.set(uri)
        elif mode == 'overwrite':
            # There's a comment, but overwrite mode is in effect.
            log('overwriting existing Finder comment with ' + uri)
            finder_file.comment.set(uri)
        elif uri in comment:
            log('comment already contains the same URI -- nothing to do')
        elif scheme + '://' in comment:
            # The comment has a different URI with the same scheme.
            log('comment has an existing URI with the same scheme')
            if mode == 'append':
                log('appending to existing Finder comment the string ' + uri)
                finder_file.comment.set(comment + '\n' + uri)
            else:
                # Mode is update.
                import re
                regex = r'(.*?)(?!' + scheme + ')?' + scheme + '://' + '([^\s]+)(.*?)'
                s = re.search(regex, comment, re.IGNORECASE)
                new_comment = s.group(1) + scheme + '://' + rest + s.group(3)
                log('writing new comment: ' + new_comment)
                finder_file.comment.set(new_comment)
        elif mode == 'append':
            # Didn't find a URI, and not doing overwrite => append.
            log('appending to existing Finder comment the string ' + uri)
            finder_file.comment.set(comment + '\n' + uri)
        else:
            # Didn't find a URI of the same kind and we're not appending.
            log('nothing to do')

    except KeyboardInterrupt:
        log(f'user interrupted program -- exiting')
        sys.exit(0)
    except Exception as ex:
       fatal(f'Encountered error: ' + str(ex), no_gui)

    log('done.')
    sys.exit(0)


# Miscellaneous helpers.
# .............................................................................

def parsed_uri(uri):
    if '://' not in uri:
        return None, None
    parts = uri.split('://')
    if not all(len(part) > 0 for part in parts):
        return None, None
    return parts[0], parts[1]


def alert(msg, no_gui):
    log('alert: ' + msg)
    if no_gui:
        print('‼️  ' + msg)
    else:
        from urial import __program__
        from osax import OSAX
        sa = OSAX("StandardAdditions", name = "System Events")
        sa.activate()
        sa.display_dialog(__program__.title() + ' error:\n\n' + msg,
                          buttons = ["OK"], with_icon = 0)


def fatal(msg, no_gui):
    alert(msg, no_gui)
    sys.exit(1)


# Main entry point.
# .............................................................................

# The following entry point definition is for the console_scripts keyword
# option to setuptools.  The entry point for console_scripts has to be a
# function that takes zero arguments.
def console_scripts_main():
    main()

# The following allows users to invoke this using "python3 -m urial".
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'help':
        plac.call(main, ['-h'])
    else:
        plac.call(main)


# For Emacs users
# .............................................................................
# Local Variables:
# mode: python
# python-indent-offset: 4
# End:
