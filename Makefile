# Summary: Makefile for developing and releasing Urial.
# Run "make" or "make help" to get a list of commands in this makefile.
#
# ╭──────────────────────── Notice ── Notice ── Notice ───────────────────────╮
# │ The codemeta.json file is considered the master source for version and    │
# │ other info. Information is pulled out of codemeta.json to update other    │
# │ files like setup.cfg, the README, and others. Maintainers should update   │
# │ codemeta.json and not edit other files to update version numbers & URLs.  │
# ╰───────────────────────────────────────────────────────────────────────────╯
#
# Copyright 2024 Michael Hucka.
# License: MIT License – see file "LICENSE" in the project website.
# Website: https://github.com/mhucka/urial

SHELL=/bin/bash
.ONESHELL:                              # Run all commands in the same shell.
.SHELLFLAGS += -e                       # Exit at the first error.

# This Makefile uses syntax that needs at least GNU Make version 3.82.
# The following test is based on the approach posted by Eldar Abusalimov to
# Stack Overflow in 2012 at https://stackoverflow.com/a/12231321/743730

ifeq ($(filter undefine,$(value .FEATURES)),)
$(error Unsupported version of Make. \
    This Makefile does not work properly with GNU Make $(MAKE_VERSION); \
    it needs GNU Make version 3.82 or later)
endif

# Before we go any further, test if certain programs are available.
# The following is based on the approach posted by Jonathan Ben-Avraham to
# Stack Overflow in 2014 at https://stackoverflow.com/a/25668869

programs_needed = awk curl gh git jq sed
TEST := $(foreach p,$(programs_needed),\
	  $(if $(shell which $(p)),_,$(error Cannot find program "$(p)")))

# Set some basic variables. These are quick to set; we set additional ones
# using the dependency named "vars" but only when the others are needed.

name	 := $(strip $(shell jq -r .name codemeta.json))
progname := $(strip $(shell jq -r '.identifier | ascii_downcase' codemeta.json))
version	 := $(strip $(shell jq -r .version codemeta.json))
repo	 := $(shell git ls-remote --get-url | sed -e 's/.*:\(.*\).git/\1/')
repo_url := https://github.com/$(repo)
branch	 := $(shell git rev-parse --abbrev-ref HEAD)
initfile := $(progname)/__init__.py
today	 := $(shell date "+%F")


# Print help if no command is given ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# The help scheme works by looking for lines beginning with "#:" above make
# targets in this file. Originally based on code posted to Stack Overflow on
# 2019-11-28 by Richard Kiefer at https://stackoverflow.com/a/59087509/743730

#: Print a summary of available commands.
help:
	@echo "This is the Makefile for $(bright)$(name)$(reset)."
	@echo "Available commands:"
	@echo
	@grep -B1 -E "^[a-zA-Z0-9_-]+\:([^\=]|$$)" $(MAKEFILE_LIST) \
	| grep -v -- -- \
	| sed 'N;s/\n/###/' \
	| sed -n 's/^#: \(.*\)###\(.*\):.*/$(color)\2$(reset):###\1/p' \
	| column -t -s '###'

#: Summarize how to do a release using this makefile.
instructions:;
	@$(info $(instructions_text))

define instructions_text =
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Steps for doing a release                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
 1. Run $(color)make lint$(reset), fix any problems, and commit any changes.
 2. Run $(color)make tests$(reset) fix any problems, and commit any changes.
 3. Update the version number in codemeta.json.
 4. Check CHANGES.md, update if needed, and commit changes.
 5. Check the output of $(color)make report$(reset).
 6. Run $(color)make clean$(reset).
 7. Run $(color)make release$(reset); after some steps, it will open a file
    in your editor to write GitHub release notes. Copy the notes
    from CHANGES.md. Save the opened file to finish the process.
 8. Check that everything looks okay with the GitHub release at
    $(link)$(repo_url)/releases$(reset)
endef


# Gather additional values we sometimes need ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# These variables take longer to compute, and for some actions like "make help"
# they are unnecessary and annoying to wait for.
vars:;
	$(eval url	:= $(strip $(shell jq -r .url codemeta.json)))
	$(eval url	:= $(or $(url),$(repo_url)))
	$(eval license	:= $(strip $(shell jq -r .license codemeta.json)))
	$(eval desc	:= $(strip $(shell jq -r .description codemeta.json)))
	$(eval author	:= \
	  $(strip $(shell jq -r '.author[0].givenName + " " + .author[0].familyName' codemeta.json)))
	$(eval email	:= $(strip $(shell jq -r .author[0].email codemeta.json)))
	$(eval related	:= \
	  $(strip $(shell jq -r '.relatedLink | if type == "array" then .[0] else . end' codemeta.json)))

#: Print variables set in this Makefile from various sources.
.SILENT: report
report: vars
	echo "$(color)name$(reset)	 = $(name)"	  | expand -t 20
	echo "$(color)progname$(reset)	 = $(progname)"	  | expand -t 20
	echo "$(color)url$(reset)	 = $(url)"	  | expand -t 20
	echo "$(color)desc$(reset)	 = $(desc)"	  | expand -t 20
	echo "$(color)version$(reset)	 = $(version)"	  | expand -t 20
	echo "$(color)author$(reset)	 = $(author)"	  | expand -t 20
	echo "$(color)email$(reset)	 = $(email)"	  | expand -t 20
	echo "$(color)license$(reset)	 = $(license)"	  | expand -t 20
	echo "$(color)repo url$(reset)	 = $(repo_url)"	  | expand -t 20
	echo "$(color)branch$(reset)	 = $(branch)"	  | expand -t 20


# make lint & make test ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#: Run the code through Python linters like flake8.
lint:
	markdownlint-cli2 *.md
	flake8 $(progname)

#: Run unit tests and coverage tests.
test tests:;
	pytest -v --cov=$(progname) -l tests/


# make binaries ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#: Build self-contained binary versions of the program.
binaries: | vars dependencies zipapps

dependencies:;
	pip3 install -r requirements-dev.txt

zipapps shiv: | run-shiv

run-shiv:;
	@mkdir -p dist
	dev/create-pyz/create-pyz dist 3.8.16
	dev/create-pyz/create-pyz dist 3.9.16
	dev/create-pyz/create-pyz dist 3.10.10
	dev/create-pyz/create-pyz dist 3.11.2


# make release ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#: Make a release on GitHub.
release: | test-branch confirm-release release-on-github print-next-steps

test-branch:
ifneq ($(branch),main)
	$(error Current git branch != main. Merge changes into main first!)
endif

confirm-release:
	@read -p "Have you updated the version number? [y/N] " ans && : $${ans:=N} ;\
	if [ $${ans::1} != y ]; then \
	  echo ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
	  echo ┃ Update the version number in codemeta.json first. ┃
	  echo ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
	  exit 1
	fi

update-all: update-setup update-init update-meta update-citation

update-setup: vars
	@sed -i .bak -e '/^version/ s|= .*|= $(version)|'    setup.cfg
	@sed -i .bak -e '/^description/ s|= .*|= $(desc)|'   setup.cfg
	@sed -i .bak -e '/^author / s|= .*|= $(author)|'     setup.cfg
	@sed -i .bak -e '/^author_email/ s|= .*|= $(email)|' setup.cfg
	@sed -i .bak -e '/^license / s|= .*|= $(license)|'   setup.cfg

update-init: vars
	@sed -i .bak -e "s|^\(__version__ *=\).*|\1 '$(version)'|"  $(initfile)
	@sed -i .bak -e "s|^\(__description__ *=\).*|\1 '$(desc)'|" $(initfile)
	@sed -i .bak -e "s|^\(__url__ *=\).*|\1 '$(url)'|"	    $(initfile)
	@sed -i .bak -e "s|^\(__author__ *=\).*|\1 '$(author)'|"    $(initfile)
	@sed -i .bak -e "s|^\(__email__ *=\).*|\1 '$(email)'|"	    $(initfile)
	@sed -i .bak -e "s|^\(__license__ *=\).*|\1 '$(license)'|"  $(initfile)

# Note that this doesn't replace "version" in codemeta.json, because that's the
# variable from which this makefile gets its version number in the first place.
update-meta:
	@sed -i .bak -e '/"datePublished"/ s|: ".*"|: "$(today)"|' codemeta.json

update-citation: vars
	@sed -i .bak -e '/^url:/ s|".*"|"$(url)"|' CITATION.cff
	@sed -i .bak -e '/^title:/ s|".*"|"$(name)"|' CITATION.cff
	@sed -i .bak -e '/^version:/ s|".*"|"$(version)"|' CITATION.cff
	@sed -i .bak -e '/^abstract:/ s|".*"|"$(desc)"|' CITATION.cff
	@sed -i .bak -e '/^license-url:/ s|".*"|"$(license)"|' CITATION.cff
	@sed -i .bak -e '/^date-released:/ s|".*"|"$(today)"|' CITATION.cff
	@sed -i .bak -e '/^repository-code:/ s|".*"|"$(repo_url)"|' CITATION.cff

edited := setup.cfg codemeta.json $(initfile) CITATION.cff

commit-updates:
	git add $(edited)
	git diff-index --quiet HEAD $(edited) || \
	    git commit -m"chore: update stored version number" $(edited)

release-on-github: | update-all commit-updates binaries
	$(eval tmp_file := $(shell mktemp /tmp/release-notes-$(progname).XXXX))
	$(eval tag := "v$(shell tr -d '()' <<< "$(version)" | tr ' ' '-')")
	git push -v --all
	git push -v --tags
	@$(info ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓)
	@$(info ┃ Write release notes in the file that gets opened in your  ┃)
	@$(info ┃ editor. Close the editor to complete the release process. ┃)
	@$(info ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛)
	sleep 2
	$(EDITOR) $(tmp_file)
	gh release create $(tag) -t "Release $(version)" -F $(tmp_file)
	gh release edit $(tag) --latest
	gh release upload $(tag) $(shell find dist -name '*.zip')
	open "$(repo_url)/releases"

print-next-steps: vars
	@$(info ┏━━━━━━━━━━━━┓)
	@$(info ┃ Next steps ┃)
	@$(info ┗━━━━━━━━━━━━┛)
	@$(info  Next steps: )
	@$(info  1. Check $(repo_url)/releases )
	@$(info  2. Run $(color)make packages$(reset) )
	@$(info  3. Run $(color)make test-pypi$(reset) )
	@$(info  4. Check $(link)https://test.pypi.org/project/$(progname)$(reset) )
	@$(info  5. Run $(color)make pypi$(reset) to push to PyPI for real )
	@$(info  6. Check $(link)https://pypi.org/project/$(progname)$(reset) )

#: Create the distribution files for PyPI.
packages: | clean
	-mkdir -p build dist
	python3 setup.py sdist --dist-dir dist
	python3 setup.py bdist_wheel --dist-dir dist
	python3 -m twine check dist/$(progname)-$(version).tar.gz

# Note: for the next action to work, the repository "testpypi" needs to be
# defined in your ~/.pypirc file. Here is an example file:
#
#  [distutils]
#  index-servers =
#    pypi
#    testpypi
#
#  [testpypi]
#  repository = https://test.pypi.org/legacy/
#  username = YourPyPIlogin
#  password = YourPyPIpassword
#
# You could copy-paste the above to ~/.pypirc, substitute your user name and
# password, and things should work after that. See the following for more info:
# https://packaging.python.org/en/latest/specifications/pypirc/

#: Upload distribution to test.pypi.org.
test-pypi: packages
	python3 -m twine upload --verbose --repository testpypi \
	   dist/$(progname)-$(version)*.{whl,gz}

#: Upload distribution to pypi.org.
pypi: packages
	python3 -m twine upload dist/$(progname)-$(version)*.{gz,whl}


# Cleanup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#: Clean this directory of temporary and backup files.
clean: clean-build clean-dist clean-release clean-other
	@echo ✨ Cleaned! ✨

clean-build:;
	rm -rf build

clean-dist: vars
	rm -rf dist

clean-release:;
	rm -rf codemeta.json.bak README.md.bak $(progname).egg-info

clean-other:;
	rm -fr __pycache__ $(progname)/__pycache__ .eggs
	rm -rf .cache
	rm -rf .pytest_cache
	rm -f *.bak
	rm -f tests/*.log


# Miscellaneous directives ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#: Print a random joke from https://icanhazdadjoke.com/.
joke:
	@echo "$(shell curl -s https://icanhazdadjoke.com/)"

# Color codes used in messages.
color  := $(shell tput bold; tput setaf 6)
bright := $(shell tput bold; tput setaf 15)
dim    := $(shell tput setaf 66)
link   := $(shell tput setaf 111)
reset  := $(shell tput sgr0)

.PHONY: help vars report release test-branch test tests update-all \
	update-init update-meta update-citation update-example commit-updates \
	update-setup release-on-github print-instructions update-doi \
	packages test-pypi pypi clean really-clean completely-clean \
	clean-dist really-clean-dist clean-build really-clean-build \
	clean-release clean-other

.SILENT: clean clean-dist clean-build clean-release clean-other really-clean \
	really-clean-dist really-clean-build completely-clean vars
