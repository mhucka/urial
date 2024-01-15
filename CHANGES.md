# Change log for Urial

## ★ Version 1.2.0 ★

Changes in this version:

* Switch to MIT license and drop mention of Caltech (the latter as a result of discussions at work).
* Updat some files for git and metadata to follow my latest template versions of those files.
* Add `.flake8` and `.editorconfig` files.
* Fix some lint warnings in `__main__.py`.
* Update the `Makefile`.


## ★ Version 1.1.2 ★

This release fixes a bug in the arguments to the `OSAX` constructor, which takes different arguments in the latest release of the `appscript` package.


## ★ Version 1.1.1 ★

Changes in this release:

* Updated dependencies.
* Updated format of `CITATION.cff`


## ★ Version 1.1.0 ★

Changes in this release:

* Added `--mode prepend`, similar to `--mode append` but to prepend the URI to the front of the Finder comment instead of appending it to the end.
* Updated versions of dependencies in `requirements.txt`.
* Added `requirements-dev.txt`.
* Improved `codemeta.json`.
* Updated `Makefile`.


## ★ Version 1.0.0 ★

First public release. This version improves parsing of URIs in Finder comments, and the release now includes ready-to-run binary executables for macOS.


## ★ Version 0.0.4 ★

This release updates `requirements.txt` for some missing dependencies.


## ★ Version 0.0.3 ★

Changes in this release:

* Added new option `--strict`.
* Added new option `--print`.
* Rewrote URI-matching code to use functions from the [uritools](https://github.com/tkem/uritools/) package.


## ★ Version 0.0.2 ★

Fix bug in handling command-line arguments when installed using `pip` or `pipx`.


## ★ Version 0.0.1 ★

First complete test release.


## ★ Version 0.0.0 ★

Repository created.
