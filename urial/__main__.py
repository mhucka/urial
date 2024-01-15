'''
Urial: URI Addition tooL

Copyright 2024 Michael Hucka.

Licensed under the MIT License – see file "LICENSE" in the project website.
For more information, please visit https://github.com/mhucka/urial
'''

import sys
if sys.version_info <= (3, 9):
    print('Urial requires Python version 3.9 or higher,')
    print('but the current version of Python is '
          + str(sys.version_info.major) + '.' + str(sys.version_info.minor) + '.')
    exit(1)

# Note: this code uses lazy loading.  Additional imports are made below.
import plac
from   sidetrack import set_debug, log
from   uritools import urisplit


# Constants.
# .............................................................................

_NON_URI_CHARS = r'"\<>^`{}|'
_NON_URI_END = tuple(r".,:;'?!$([")


# Main body.
# .............................................................................

@plac.annotations(
    mode    = ('how to handle existing comment (see help for info)'   , 'option', 'm'),
    print_  = ('print the Finder comment or the URI, and exit'        , 'option', 'p'),
    strict  = ('be strict about recognizing URIs (see help for info)' , 'flag'  , 's'),
    no_gui  = ('do not use macOS GUI dialogs for error messages'      , 'flag'  , 'U'),
    version = ('print program version info and exit'                  , 'flag'  , 'V'),
    debug   = ('log debug output to "OUT" ("-" is console)'           , 'option', '@'),
    args    = 'a URI followed by a file name',
)
def main(mode = 'M', print_ = 'P', strict = False, no_gui = False,
         version = False, debug = 'OUT', *args):
    '''Add or update a URI in a Finder comment.

This program expects to be given one or more arguments on the command line, as
described below. Optional arguments begin with dashes and modify the program's
behavior.

Default behavior
~~~~~~~~~~~~~~~~

Without any optional flags or arguments to modify its behavior, this program
expects to be given at least two argument values.  The first value should be
a URI, and the second value should be the path of a file whose Finder comment
should be updated with the given URI.

If the current Finder comment for the file is empty, then this program will
write the URI into the Finder comment.

If the current Finder comment is not empty, this program will modify the
comment to update the substring that has the same type of URI, and then only
if urial finds such a substring in the Finder comment. For example, if the file
"somefile.md" contains a Finder comment with an existing x-devonthink-item
URI inside of it, then the following command,

  urial  x-devonthink-item://8A1A0F18-068680226F3  somefile.md

will cause urial to look for the first "x-devonthink-item" URI it finds in the
Finder comment and replacing it with the new value.

If the current Finder comment is not empty but also does not contain a URI of
the same kind as the one given on the command line, then the Finder comment is
not changed unless a suitable value for the option --mode is given (see below).

URI detection
~~~~~~~~~~~~~

The full syntax of URIs is complex. The characters that can appear in URIs
(according to RFC 3986) include periods, semicolons, question marks, dollar
signs, exclamation points, parentheses, square brackets, and more. Here are
some examples of valid yet potentially surprising URIs:

  paparazzi:http://www.caltech.edu
  https://en.wikipedia.org/wiki/Bracket_(disambiguation)
  z39.50s://lx2.loc.gov:210/lcdb?9=84243207
  ldap://[2001:db8::7]/c=GB?a?b
  http://wayback.archive.org/web/*/http://www.alexa.com/topsites
  prefs:root=General&path=VPN/DNS

URIs are difficult to detect when they're embedded in human language
text. One can't assume that URIs are delineated by whitespace characters,
because a human or software tool may have written a Finder comment without
being careful to delimit URIs from the rest of the text. Even worse, URI
syntax according to RFC 3986 allows for a scheme name followed by an empty
path, which means that in the following text,

  Original source: x-devonthink-item://40C401DB-8A1D-4B1D-032FB186D85A.

a strict interpretation requires that the string "source:" is considered a
valid URI. (In addition, the trailing period is, strictly speaking, part of
the second URI). This is probably not what the author intended.

These strict interpretations are usually unhelpful in urial's domain of
application. For this reason, urial tries to be intelligent about recognizing
URIs in Finder comments by applying the following rules:

  1) it will assume that the following characters are not part of a URI if
     they come at the end of something that otherwise looks like a URI:
     . , : ; ' ? ! $ ( [

  2) it will assume that ) and ] characters at the end of something that
     looks like a URI are not part of the URI if there is no opening ( or [
     character in the rest of the URI

  3) it will ignore strings that could be URIs with empty path components
     (e.g., "something:", "abc-def:", etc.)

To disable this behavior, use the --strict option; then, the program will
assume that URIs are separated from text only by (1) whitespace characters
and (2) the characters < > ^ " ` { and }, and it will not ignore potential
URIs with empty paths.

Options for handling existing Finder comments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The --mode option can be used to change this program's behavior, as follows:

  append:    if the URI is NOT found in the Finder comment string, append the
             given URI to the end of the comment; otherwise (if the comment
             string already contains the URI) do nothing

  prepend:   if the URI is NOT found in the Finder comment string, prepend the
             given URI to the front of the comment; otherwise (if the comment
             string already contains the URI) do nothing

  overwrite: overwrite the Finder comment completely with the given URI string,
             no matter what the Finder comment string contains (even if it
             already contains the given URI)

  update:    (default) if a URI of the same kind exists in the comment,
             replace only the URI portion of the comment string (preserving
             the rest of the comment string), else (if a URI is NOT found in
             the comment string) do nothing

Note that the behavior of "--mode overwrite" is to replace unconditionally the
entire Finder comment. In other words, "-- mode overwrite" will change a
Finder comment such as

    Blah blah blah. URI. More blah blah blah.

to just

    URI

assuming that "URI" is the URI given to urial on the command line. If you want
to update the URI to a new value and leave the other comment text in place,
use "--mode update" or simply don't provide a value for --mode (because
update is the default action).

Printing the Finder comment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of writing a Finder comment, urial can be used to print an existing
comment via the --print option. The --print option takes a required argument,
which can be either "comment" or "uri"; the former causes urial to print the
entire Finder comment of the file, and the latter just the URI(s) found in
the comment. For example, given a file named "somefile.md", the following
command will extract and print any URI(s) found anywhere in the Finder
comment text:

  urial --print uri somefile.md

If more than one URI is found in the Finder comment, they will be printed
separately to the terminal, one per line.

Additional command-line arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If given the --version option, this program will print the version and other
information, and exit without doing anything else.

By default, this program will use macOS dialogs to report errors or other
issues. The option --no-gui will make it print messages only on the command
line, without using GUI dialogs.

If given the --debug argument, this program will output a detailed trace of
what it is doing. The trace will be sent to the given destination, which can
be '-' to indicate console output, or a file path to send the output to a file.

Command-line arguments summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

    # Define shortcut functions for common user feedback actions.
    def alert(msg): inform(msg, no_gui)               # noqa: #704
    def stop(msg): inform(msg, no_gui), sys.exit(1)   # noqa: #704

    # Process arguments & handle early exits ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if debug != 'OUT':
        set_debug(True, debug)

    if version:
        from urial import print_version
        print_version()
        sys.exit(0)

    mode = 'update' if mode == 'M' else mode.lower()
    if mode not in ['update', 'append', 'prepend', 'overwrite']:
        stop(f'Unrecognized mode value: {mode}')

    show = print_.lower() if print_ != 'P' else False
    if show:
        if show not in ['comment', 'uri']:
            stop(f'Invalid option value for --print: {print_}. The valid'
                 ' options are "comment" and "uri".')
        file = args[0]
    else:
        if len(args) < 2:
            stop('Must be given at least two arguments: a URI and a file path.')
        uri = args[0]
        file = args[1]
        scheme = urisplit(uri).scheme
        if not scheme:
            stop(f'Could not interpret argument value "{uri}" as a URI.')

    if file == '':
        stop('File name must not be an empty string.')
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
            elif (uris := uris_in_text(comment, strict)):
                print('\n'.join(uris))
        elif not comment:
            log('file has no comment, so writing ' + uri)
            finder_file.comment.set(uri)
        elif mode == 'overwrite':
            # There's a comment, but overwrite mode is in effect.
            log('overwriting existing Finder comment with ' + uri)
            finder_file.comment.set(uri)
        elif uri in comment:
            log('comment already contains the same URI: ' + uri)
        elif mode == 'append':
            log('appending to existing Finder comment the string ' + uri)
            finder_file.comment.set(comment + '\n' + uri)
        elif mode == 'prepend':
            log('prepending to existing Finder comment the string ' + uri)
            finder_file.comment.set(uri + '\n' + comment)
        else:
            # Check if there's a URI with the same scheme in the comment.
            uris = uris_in_text(comment, strict)
            same_scheme_uris = [u for u in uris if urisplit(u).scheme == scheme]
            if any(same_scheme_uris):
                log(f'replacing {same_scheme_uris[0]} with {uri}')
                parts = comment.partition(same_scheme_uris[0])
                new_comment = parts[0] + uri + parts[2]
                finder_file.comment.set(new_comment)
            else:
                # Didn't find a URI of the same kind and we're not appending.
                log('nothing to do')
    except KeyboardInterrupt:
        log('user interrupted program -- exiting')
        sys.exit(0)
    except Exception as ex:             # noqa: PIE786
        from traceback import format_exception
        exception = sys.exc_info()
        details = ''.join(format_exception(*exception))
        stop('Encountered error: ' + str(ex) + '\n\n' + details)

    # If we get here, exit normally -------------------------------------------

    log('done.')
    sys.exit(0)


# Miscellaneous helpers.
# .............................................................................
# The syntax of URIs is defined in https://www.rfc-editor.org/rfc/rfc3986.

def unsurrounded(text):
    '''Remove matched parentheses or brackets surrounding the text.'''
    # Loop in order to handle nested cases.
    while text.startswith(('(', '[')):
        if text.startswith('(') and text.endswith(')'):
            text = text[1:-1]
        elif text.startswith('[') and text.endswith(']'):
            text = text[1:-1]
        else:
            break
    return text


def extracted_uri(text, strict = False):
    # URIs have to begin with a scheme description, which means any character
    # not allowed in a scheme description can't be part of the start of a URI.
    # Further, scheme descriptions have to start with an alpha character, so
    # any other character at the start can be stripped away.  Making this
    # trickier is that chunks may have URIs nested inside parens or brackets,
    # so we can't blindly just strip chars from the front and back.
    while text and (not text[0].isalpha()
                    or (not strict and text.endswith(_NON_URI_END + (')', ']')))):
        text = unsurrounded(text)
        if not text:
            break
        elif not text[0].isalpha():
            text = text[1:]
        elif text.endswith((')', ']')) and '(' not in text and '[' not in text:
            text = text[:-1]
        elif not strict and text.endswith(_NON_URI_END):
            text = text[:-1]
        else:
            break
    uri = urisplit(text)
    if not uri.scheme:
        return ''
    if not strict and not any([uri.authority, uri.path, uri.query, uri.fragment]):
        return ''
    return text


def uris_in_text(text, strict = False):
    '''Try to find URIs in the given text and return urisplit objects.'''
    # Do a first pass of this in case the whole text is surrounded.
    text = unsurrounded(text)
    # 1st replace non-URI special characters like < and > by a space, then
    # use split(' ') to bust up the text into chunks.
    import string
    separators = string.whitespace + _NON_URI_CHARS
    space_replacements = str.maketrans(separators, ' '*len(separators))
    chunks = str.translate(text, space_replacements).split(' ')
    # Now we have chunks that may be URIs or contain URIs embedded in them.
    # Examine each chunk and return the URIs found.
    return list(filter(None, [extracted_uri(chunk, strict) for chunk in chunks]))


def inform(msg, no_gui):
    log('inform: ' + msg)
    if no_gui:
        print('‼️  ' + msg)
    else:
        from osax import OSAX
        sa = OSAX(name = "System Events")
        sa.activate()
        # The text below uses Unicode characters to produce bold text.
        sa.display_dialog('𝗨𝗿𝗶𝗮𝗹 𝗲𝗿𝗿𝗼𝗿:\n\n' + msg, buttons = ["OK"],
                          default_button = 'OK', with_icon = 0)


# Main entry point.
# .............................................................................

# The following entry point definition is for the console_scripts keyword
# option to setuptools. The entry point for console_scripts has to be a
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
