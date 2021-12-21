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
    mode    = ('how to handle existing comment (see help for info)', 'option', 'm'),
    show    = ('print the Finder comment or the URI, and exit',      'option', 's'),
    no_gui  = ('do not use macOS GUI dialogs for error messages',    'flag',   'U'),
    version = ('print program version info and exit',                'flag',   'V'),
    debug   = ('log debug output to "OUT" ("-" is console)',         'option', '@'),
    args    = 'a URI followed by a file name',
)

def main(mode = 'M', show = 'S', no_gui = False, version = False,
         debug = 'OUT', *args):
    '''Add or update a URI in a Finder comment.

This program expects to be given at least two argument values.  The first
value is taken to be a string containing a URI, and the second value is the
path of a file whose Finder comment should be updated with the given string.
Optional arguments begin with dashes and modify the program's behavior.

Default behavior
~~~~~~~~~~~~~~~~

If the current Finder comment for the file is empty, then this program will
write the URI into the Finder comment.

If the current Finder comment is not empty, this program will modify the
comment to update the substring that has the same type of URI, and then only
if urial finds such a substring in the Finder comment. For example, if the file
"somefile.md" contains a Finder comment with an existing x-devonthink-item
URI inside of it, then the following command,

  urial  x-devonthink-item://8A1A0F18-068680226F3  somefile.md

will rewrite just the URI part of the comment to have the new URI given on the
command line.

If the current Finder comment is not empty but also does not contain a URI of
the same kind as the one given on the command line, then the Finder comment is
not changed unless a suitable value for the option --mode is given (see below).

Options for handling existing Finder comments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The --mode option can be used to change this program's behavior, as follows:

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

Printing the Finder comment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of writing a Finder comment, urial can be used to print an existing
comment via the --show option. The --show option takes a required argument,
which can be either "comment" or "uri"; the former causes urial to print the
entire Finder comment of the file, and the latter just the URI(s) found in
the comment. For example, given a file named "somefile.md", the following
command will extract and print any URI(s) found anywhere in the Finder
comment text:

  urial --show uri somefile.md

If more than one URI is found in the Finder comment, they will be printed
separately to the terminal, one per line.

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

    # Define shortcut functions for common user feedback actions.
    def alert(msg): inform(msg, no_gui)
    def stop(msg): inform(msg, no_gui), sys.exit(1)

    # Process arguments & handle early exits ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if debug != 'OUT':
        set_debug(True, debug)

    if version:
        from urial import print_version
        print_version()
        sys.exit(0)

    mode = 'update' if mode == 'M' else mode
    if not mode in ['update', 'append', 'overwrite']:
        stop(f'Unrecognized mode value: {mode}')

    show = show.lower() if show != 'S' else False
    if show:
        if show not in ['comment', 'uri']:
            stop(f'Invalid option value for --show: {show}. The valid options'
                 + ' are "comment" and "uri".')
        file = args[0]
    else:
        if len(args) < 2:
            stop('Must be given at least two arguments: a URI and a file path.')
        uri = args[0]
        file = args[1]
        scheme, rest = parsed_uri(uri)
        if not scheme:
            stop(f'Could not interpret argument value "' + uri + '" as a URI.')

    if file == '':
        stop(f'File name is an empty string.')
    from os.path import exists
    if not exists(file):
        stop(f'File does not appear to exist: {file}')

    # Do the real work --------------------------------------------------------

    import appscript
    import mactypes
    try:
        log(f'urial is running in {mode} mode')
        log('telling Finder to open file ' + file)
        finder = appscript.app('Finder')
        finder_file = finder.items[mactypes.Alias(file)]
        comment = finder_file.comment()
        if show:
            if show == 'comment':
                print(comment)
            elif (uris := uris_in_text(comment)):
                print(r'\n'.join(uris))
        elif not comment:
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
                regex = r'(.*?)(?!' + scheme + ')?' + scheme + '://' + '([^\s".,;<>(){}\[\]]+)(.*?)'
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
       from traceback import format_exception
       exception = sys.exc_info()
       details = ''.join(format_exception(*exception))
       stop(f'Encountered error: ' + str(ex) + '\n\n' + details)

    log('done.')
    sys.exit(0)


# Miscellaneous helpers.
# .............................................................................

# FIXME the only reason for the split is to get the scheme in another part of
# the code above, but if I return a single uri instead, then the code above
# could take do a split on :// to get the scheme pretty easily.

def uris_in_text(text):
    import re
    uris = []
    split_chars = '!"#$%\'()*+.,;<>@[]^`{}'
    splitter = str.maketrans(split_chars, ' '*len(split_chars))
    chunks = str.translate(text, splitter).split(' ')
    for chunk in filter(None, chunks):
        left, right = parsed_uri(chunk)
        if left:
            uris.append(left + '://' + right)
    return uris


def parsed_uri(uri):
    if '://' not in uri:
        return None, None
    parts = uri.split('://')
    if not all(len(part) > 0 for part in parts):
        return None, None
    return parts[0], parts[1]


def inform(msg, no_gui):
    log('inform: ' + msg)
    if no_gui:
        print('‼️  ' + msg)
    else:
        from urial import __program__
        from osax import OSAX
        sa = OSAX("StandardAdditions", name = "System Events")
        sa.activate()
        # The text below uses Unicode characters to get bold text.
        sa.display_dialog('𝗨𝗿𝗶𝗮𝗹 𝗲𝗿𝗿𝗼𝗿:\n\n' + msg,
                          buttons = ["OK"], default_button = 'OK', with_icon = 0)


# Main entry point.
# .............................................................................

# The following entry point definition is for the console_scripts keyword
# option to setuptools.  The entry point for console_scripts has to be a
# function that takes zero arguments.
def console_scripts_main():
    plac.call(main)

# The following allows users to invoke this using "python3 -m urial" and also
# pass it an argument of "help" to get the help text.
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
