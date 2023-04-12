# Urial<img width="12%" align="right" src="https://github.com/mhucka/urial/raw/main/.graphics/urial-icon.png">

Urial (_**URI** **a**ddition too**l**_) is a simple but intelligent command-line tool to add, view, or replace URIs in macOS Finder comments.

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Python](https://img.shields.io/badge/Python-3.6+-brightgreen.svg?style=flat-square)](http://shields.io)
[![Latest release](https://img.shields.io/github/v/release/mhucka/urial.svg?style=flat-square&color=b44e88)](https://github.com/mhucka/urial/releases)
[![PyPI](https://img.shields.io/pypi/v/urial.svg?style=flat-square&color=orange&label=PyPI)](https://pypi.org/project/urial/)


## Table of contents

* [Introduction](#introduction)
* [Installation](#installation)
* [Usage](#usage)
* [Getting help](#getting-help)
* [Contributing](#contributing)
* [License](#license)
* [Authors and history](#authors-and-history)
* [Acknowledgments](#authors-and-acknowledgments)


## Introduction

_Urial_ (a loose acronym of _**URI** **a**ddition too**l**_) is a command-line program written in Python 3 that allows you to read, write and update URIs in the macOS Finder comments of a file. Urial makes it easier to create scripts (e.g., in Bash/Bourne shell syntax, or AppleScripts) that keep those URIs updated.  You can find an example of how the author uses this program with [DEVONthink](https://www.devontechnologies.com/apps/devonthink) in the project [wiki](https://github.com/mhucka/urial/wiki).

Incidentally, the [urial](https://en.wikipedia.org/wiki/Urial) (properly known as _Ovis vignei_) are a kind of wild sheep native to Central and South Asia.  They are listed by the [IUCN](https://en.wikipedia.org/wiki/International_Union_for_Conservation_of_Nature) as a [vulnerable species](https://www.iucnredlist.org/species/54940655/195296049) and their population continues to twindle due to human activity, hunting, and climate change.


## Installation

There are multiple ways of installing the program `urial`, ranging from downloading a self-contained, single-file, ready-to-run program, to installing it as a typical Python program using `pip`.  Please choose the alternative that suits you.

### _Alternative 1: downloading the ready-to-run program_

A binary, ready-to-run version of `urial` is available that only needs a Python interpreter version 3.8 or higher on your computer. Happily, that's the case for macOS 10.15 and later. To be sure, first check the version of the program `python3` that you get by running the following command in a terminal and inspecting the results:
```sh
python3 --version
```

(Note: if this is the first time you've run `python3` on your system, macOS will ask if you want to install certain additional software components. Let it do so.) Make sure the version is at least 3.8. Note that if you are running a macOS version before 10.15, you will need to manually install Python 3.8 or later.

Next,
1. <img align="right" width="350px" src="https://github.com/mhucka/urial/raw/main/.graphics/shiv-releases.png"/>Go to the [latest release on GitHub](https://github.com/mhucka/urial/releases) and find the **Assets**
2. **Download** the ZIP file whose name contains the version of Python on your computer
3. **Unzip** the file (if your browser didn't unzip it)
4. **Open the folder** that gets created (it will have a name like `urial-1.0.0-macos-python3.8`)
5. Look inside for `urial` and **move it** to a location where you put other command-line programs (such as `/usr/local/bin`). 

If you want to put it in `/usr/local/bin` but that folder does not exist on your computer yet, you can create it by opening a terminal window and running the following command (_prior_ to moving `urial` into `/usr/local/bin`):

```shell
sudo mkdir /usr/local/bin
```

The following is an example command that you can type in a terminal to move `urial` there:

```shell
sudo mv urial /usr/local/bin
```


### _Alternative 2: installation using `pipx`_

You can use [pipx](https://pypa.github.io/pipx/) to install `urial`. Pipx will install it into a separate Python environment that isolates the dependencies needed by `urial` from other Python programs on your system, and yet the resulting `urial` program wil be executable from any shell &ndash; like any normal program on your computer. If you do not already have `pipx` on your system, it can be installed in a variety of easy ways and it is best to consult [Pipx's installation guide](https://pypa.github.io/pipx/installation/) for instructions. Once you have pipx on your system, you can install `urial` with the following command:
```sh
pipx install urial
```

Pipx can also let you run `urial` directly using `pipx run urial`, although in that case, you must always prefix every `urial` command with `pipx run`.  Consult the [documentation for `pipx run`](https://github.com/pypa/pipx#walkthrough-running-an-application-in-a-temporary-virtual-environment) for more information.


### _Alternative 3: installation using `pip`_

The instructions below assume you have a Python 3 interpreter installed on your computer.  Note that the default on macOS at least through 10.14 (Mojave) is Python **2** &ndash; please first install Python version 3 and familiarize yourself with running Python programs on your system before proceeding further.

You should be able to install `urial` with [`pip`](https://pip.pypa.io/en/stable/installing/) for Python&nbsp;3.  To install `urial` from the [Python package repository (PyPI)](https://pypi.org), run the following command:
```sh
python3 -m pip install urial
```

As an alternative to getting it from [PyPI](https://pypi.org), you can use `pip` to install `urial` directly from GitHub:
```sh
python3 -m pip install git+https://github.com/mhucka/urial.git
```

_If you already installed `urial` once before_, and want to update to the latest version, add `--upgrade` to the end of either command line above.


### _Alternative 4: installation from sources_

If  you prefer to install `urial` directly from the source code, you can do that too. To get a copy of the files, you can clone the GitHub repository:
```sh
git clone https://github.com/mhucka/urial
```

Alternatively, you can download the files as a ZIP archive using this link directly from your browser using this link: <https://github.com/mhucka/urial/archive/refs/heads/main.zip>

Next, after getting a copy of the files,  run `setup.py` inside the code directory:
```sh
cd urial
python3 setup.py install
```


## Usage

This program expects to be given one or more arguments on the command line, as described below.  Optional arguments begin with dashes and modify the program's behavior.

### Default behavior<img src="https://github.com/mhucka/urial/raw/main/.graphics/finder-get-info-screenshot.png" width="300px" align="right">

Without any optional flags or arguments to modify its behavior, `urial` expects to be given at least two argument values.  The first value should be a URI, and the second value should be the path of a file whose Finder comment is to be updated with the given URI.

If the current Finder comment for the file is empty, then `urial` will simply write the URI into the Finder comment. An example of the result is shown in the screenshot at right.

If the Finder comment is _not_ empty, `urial` will edit the comment to update the substring that has the same kind of URI (meaning, one that uses the same URI scheme), and then only if `urial` finds such a substring in the Finder comment.  For example, if the file "somefile.md" has a Finder comment with an existing `x-devonthink-item` URI string somewhere inside of it, then the following command,

```sh
urial  x-devonthink-item://8A1A0F18-0686-802-26F33443  somefile.md
```

will make `urial` rewrite **just the URI part of the comment** to be the new URI given on the command line.

If the Finder comment is not empty but also does _not_ contain a URI with the same scheme as the one given on the command line, then the Finder comment is not changed, unless a suitable value for the option `--mode` is given (see below).

`urial` is careful to match based on URI schemes to make it more robust against accidentally matching other URIs that may exist in a Finder comment. So, for example, If you supply a URI that has a `x-devonthink-item` scheme type, it will _look_ only for `x-devonthink-item` URIs and will not match other URIs; if you supply a URI that has a `zotero` scheme type, it will look only for `zotero` URIs; and so on.


### URI detection

The full syntax of URIs is complex. The characters that can appear in URIs (according to [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986)) include periods, semicolons, question marks, dollar signs, exclamation points, parentheses, square brackets, and more. Here are some examples of valid yet potentially surprising URIs:

```text
paparazzi:http://www.caltech.edu
https://en.wikipedia.org/wiki/Bracket_(disambiguation)
z39.50s://lx2.loc.gov:210/lcdb?9=84243207
ldap://[2001:db8::7]/c=GB?a?b
http://wayback.archive.org/web/*/http://www.alexa.com/topsites
prefs:root=General&path=VPN/DNS
```

URIs are difficult to detect when they're embedded in human language text. One can't assume that URIs are delineated by whitespace characters, because a human or software tool may have written a Finder comment without being careful to delimit URIs from the rest of the text. Even worse, URI syntax according to [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986) allows for a scheme name followed by an empty path, which means that in the following text,
```text
Original source: x-devonthink-item://40C401DB-8A1D-4B1D-032FB186D85A.
```

a strict interpretation requires that the string `source:` is considered a valid URI. (In addition, the trailing period is, strictly speaking, part of the second URI). This is probably not what the author intended.

These strict interpretations are usually unhelpful in Urial's domain of application. For this reason, `urial` tries to be intelligent about recognizing URIs in Finder comments by applying the following rules:

1) it will assume that the following characters are not part of a URI if they come at the end of something that otherwise looks like a URI: `.` `,` `:` `;` `'` `?` `!` `$` `(` `[`
2) it will assume that `)` and `]` characters at the end of something that looks like a URI are not part of the URI if there is no opening `(` or `[` character in the rest of the URI
3) it will ignore strings that could be URIs with empty path components (e.g., `something:`, `abc-def:`, etc.)

To disable this behavior, use the <code>--strict</code> option; then, the program will assume that URIs are separated from text only by (1) whitespace characters and (2) the characters `<` `>` `^` `"` <code>&#96;</code> `{` and `}`, and it will not ignore potential URIs with empty paths.

### Options for handling existing Finder comments

The `--mode` option can be used to change the behavior described above. The following are the possible values for this option:

* `append`: in this mode, if the URI is _not_ found in the Finder comment string, `urial` will append the given URI to the end of the comment; otherwise (if the comment string already contains the URI) it will do nothing.
* `prepend`: in this mode, if the URI is _not_ found in the Finder comment string, `urial` will prepend the given URI to the front of the comment; otherwise (if the comment string already contains the URI) it will do nothing.
* `overwrite`: the program will overwrite the Finder comment completely with the given URI string, no matter what the Finder comment string contains (even if it already contains the given URI).
* `update`: (default) if a URI of the same kind exists in the comment, `urial` will replace only the URI portion of the comment string (preserving the rest of the comment string), else (if a URI is NOT found in the comment string) it will do nothing.

Note carefully that `--mode overwrite` makes `urial` replace unconditionally the entire Finder comment.  In other words, `--mode overwrite` will change a Finder comment such as

    Blah blah blah. URI. More blah blah blah.

to just

    URI

assuming that `URI` is the URI given to `urial` on the command line.  If you want to update the URI to a new value and leave rest of the text the same, use `--mode update` or simply don't provide a value for `--mode` (because `update` is the default action).


### Printing the Finder comment

Instead of writing a Finder comment, `urial` can be used to print an existing comment via the `--print` option. The `--print` option takes a required argument, which can be either `comment` or `uri`; the former causes `urial` to print the entire Finder comment of the file, and the latter just the URI(s) found in the comment. For example, given a file named "somefile.md", the following command will extract and print any URI(s) found anywhere in the Finder comment text:

```sh
urial --print uri somefile.md
```

If more than one URI is found in the Finder comment, they will be printed separately to the terminal, one per line.


### Additional command-line options

If given the `--version` option, this program will print the version and other information, and exit without doing anything else.

By default, this program will use macOS dialogs to report errors or other issues.  The option `--no-gui` will make it print messages only on the command line, without using GUI dialogs.

If given the `--debug` argument, this program will output a detailed trace of what it is doing. The trace will be sent to the destination given as the value of the option, which can be `-` (i.e., a dash) to indicate console output, or a file path to send the output to a file.


### _Summary of command-line options_

The following table summarizes all the command line options available.

| Short&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   | Long&nbsp;form&nbsp;opt&nbsp;&nbsp; | Meaning | Default |  |
|---------- |-------------------|--------------------------------------|---------|---|
| `-h`      | `--help`          | Display help text and exit | | |
| `-m`      | `--mode` _M_      | Approach for handling existing comments | `update` | ⚑ |
| `-p`      | `--print` _P_     | Print Finder comment or URIs therein, and exit  | | ★ |
| `-s`      | `--strict`        | Be strict about URI syntax | Don't be pedantic | |
| `-U`      | `--no-gui`        | Print errors & warnings to terminal | Use GUI dialogs | |
| `-V`      | `--version`       | Display program version info, and exit | | |
| `-@`_OUT_ | `--debug` _OUT_   | Debugging mode; write trace to _OUT_ | Normal mode | ⬥ |

⚑ &nbsp; Available values are `append`, `prepend`, `overwrite`, and `update`.<br>
★ &nbsp; Available values are `comment` and `uri`.<br>
⬥ &nbsp; To write to the console, use the character `-` as the value of _OUT_; otherwise, _OUT_ must be the name of a file where the output should be written.<br>


## Getting help

Some notes about how the author uses this program can be found in the [wiki](https://github.com/mhucka/urial/wiki).

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/mhucka/urial/issues) for this repository.


## Contributing

I would be happy to receive your help and participation if you are interested.  Everyone is asked to read and respect the [code of conduct](CONDUCT.md) when participating in this project.


## License

This software is Copyright (C) 2021&ndash;2023, by Michael Hucka and the California Institute of Technology (Pasadena, California, USA).  This software is freely distributed under a 3-clause BSD type license.  Please see the [LICENSE](LICENSE) file for more information.


## Acknowledgments

This work is a personal project developed by the author, using computing facilities and other resources of the [California Institute of Technology Library](https://www.library.caltech.edu).

The [vector artwork](https://thenounproject.com/icon/bighorn-sheep-head-2608122/) of a sheep with horns, used as the icon for Urial, was created by  [Vectors Point](https://thenounproject.com/vectorspoint/) from the Noun Project.  It is licensed under the Creative Commons [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/) license.

Urial makes use of numerous open-source packages, without which Urial could not have been developed.  I want to acknowledge this debt.  In alphabetical order, the packages are:

* [appscript](http://appscript.sourceforge.net/py-appscript/doc.html) &ndash; high-level Apple event bridge for controlling scriptable Mac OS X applications
* [plac](http://micheles.github.io/plac/) &ndash; a command line argument parser
* [setuptools](https://github.com/pypa/setuptools) &ndash; library for `setup.py`
* [Sidetrack](https://github.com/caltechlibrary/sidetrack) &ndash; simple debug logging/tracing package
* [uritools](https://github.com/tkem/uritools/) &ndash; functions for parsing, classifying, and composing URIs
* [wheel](https://pypi.org/project/wheel/) &ndash; setuptools extension for building wheels
