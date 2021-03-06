# =============================================================================
# @file    Makefile
# @brief   Makefile for some steps in creating new releases on GitHub
# @date    2021-10-16
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/urial
# =============================================================================

.ONESHELL: 				# Run all commands in the same shell.
.SHELLFLAGS += -e			# Exit at the first error.

# Before we go any further, test if certain programs are available.
# The following is based on the approach posted by Jonathan Ben-Avraham to
# Stack Overflow in 2014 at https://stackoverflow.com/a/25668869

PROGRAMS_NEEDED = curl gh git jq sed pyinstaller
TEST := $(foreach p,$(PROGRAMS_NEEDED),\
	  $(if $(shell which $(p)),_,$(error Cannot find program "$(p)")))

# Set some basic variables.  These are quick to set; we set additional
# variables using "set-vars" but only when the others are needed.

name	  := $(strip $(shell awk -F "=" '/^name/ {print $$2}' setup.cfg))
version	  := $(strip $(shell awk -F "=" '/^version/ {print $$2}' setup.cfg))
url	  := $(strip $(shell awk -F "=" '/^url/ {print $$2}' setup.cfg))
desc	  := $(strip $(shell awk -F "=" '/^description / {print $$2}' setup.cfg))
author	  := $(strip $(shell awk -F "=" '/^author / {print $$2}' setup.cfg))
email	  := $(strip $(shell awk -F "=" '/^author_email/ {print $$2}' setup.cfg))
license	  := $(strip $(shell awk -F "=" '/^license / {print $$2}' setup.cfg))
app_name  := $(strip $(shell python3 -c 'print("$(name)".title()+".app")'))
platform  := $(strip $(shell python3 -c 'import sys; print(sys.platform)'))
os	  := $(subst $(platform),darwin,macos)
init_file := $(name)/__init__.py
zip_file  := dist/$(os)/$(name)-$(version)-$(os).zip
branch	  := $(shell git rev-parse --abbrev-ref HEAD)


# Print help if no command is given ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

help:
	@echo 'Available commands:'
	@echo ''
	@echo 'make'
	@echo 'make help'
	@echo '  Print this summary of available commands.'
	@echo ''
	@echo 'make report'
	@echo '  Print variables set in this Makefile from various sources.'
	@echo '  This is useful to verify the values that have been parsed.'
	@echo ''
	@echo 'make release'
	@echo '  Do a release on GitHub. This will push changes to GitHub,'
	@echo '  open an editor to let you edit release notes, and run'
	@echo '  "gh release create" followed by "gh release upload".'
	@echo '  Note: this will NOT upload to PyPI, nor create binaries.'
	@echo ''
	@echo 'make update-doi'
	@echo '  Update the DOI inside the README.md file.'
	@echo '  This is only to be done after doing a "make release".'
	@echo ''
	@echo 'make binaries'
	@echo '  Create binaries (both pyinstaller and zipapps).'
	@echo ''
	@echo 'make upload-binaries'
	@echo '  Upload binaries to GitHub.'
	@echo ''
	@echo 'make packages'
	@echo '  Create the distribution files for PyPI.'
	@echo '  Do this manually to check that everything looks okay before.'
	@echo '  After doing this, do a "make test-pypi".'
	@echo ''
	@echo 'make test-pypi'
	@echo '  Upload distribution to test.pypi.org.'
	@echo '  Do this before doing "make pypi" for real.'
	@echo ''
	@echo 'make pypi'
	@echo '  Upload distribution to pypi.org.'
	@echo ''
	@echo 'make clean'
	@echo '  Clean up various files generated by this Makefile.'


# Gather values that we need ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.SILENT: vars
vars:
	$(info Gathering data -- this takes a few moments ...)
	$(eval repo	 := $(strip $(shell gh repo view | head -1 | cut -f2 -d':')))
	$(eval api_url   := https://api.github.com)
	$(eval id	 := $(shell curl -s $(api_url)/repos/$(repo) | jq '.id'))
	$(eval id_url	 := https://data.caltech.edu/badge/latestdoi/$(id))
	$(eval doi_url	 := $(shell curl -sILk $(id_url) | grep Locat | cut -f2 -d' '))
	$(eval doi	 := $(subst https://doi.org/,,$(doi_url)))
	$(eval doi_tail  := $(lastword $(subst ., ,$(doi))))
	$(info Gathering data -- this takes a few moments ... Done.)

report: vars
	@echo name	= $(name)
	@echo version	= $(version)
	@echo url	= $(url)
	@echo desc	= $(desc)
	@echo author	= $(author)
	@echo email	= $(email)
	@echo license	= $(license)
	@echo branch	= $(branch)
	@echo repo	= $(repo)
	@echo id	= $(id)
	@echo id_url	= $(id_url)
	@echo doi_url	= $(doi_url)
	@echo doi	= $(doi)
	@echo doi_tail	= $(doi_tail)
	@echo init_file = $(init_file)
	@echo app_name	= $(app_name)
	@echo zip_file	= $(zip_file)
	@echo os	= $(os)


# make binaries ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

binaries: | vars dist/$(os)/$(app_name)

dependencies:;
	pip3 install -r requirements.txt

pyinstaller dist/$(os)/$(app_name): | vars dependencies run-pyinstaller make-zip

run-pyinstaller: vars
	@mkdir -p dist/$(os)
	pyinstaller --distpath dist/$(os) --clean --noconfirm pyinstaller-$(os).spec

make-zip: run-pyinstaller
	$(eval tmp_file := $(shell mktemp /tmp/comments-$(name).XXXX))
	cat <<- EOF > $(tmp_file)
	┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
	┃ This Zip archive file includes a self-contained, runnable ┃
	┃ version of the program Urial for macOS. To learn more     ┃
	┃ about Urial, please visit the following site:             ┃
	┃                                                           ┃
	┃              https://github.com/mhucka/urial              ┃
	┃                                                           ┃
	┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
	EOF
	zip $(zip_file) dist/$(os)/$(name)
	zip -z $(zip_file) < $(tmp_file)
	-rm -f $(tmp_file)

shiv zipapps: | run-shiv

run-shiv:;
	@mkdir -p dist/$(os)
	dev/create-pyz/create-pyz dist/$(os) 3.8.2
	dev/create-pyz/create-pyz dist/$(os) 3.9.5
	dev/create-pyz/create-pyz dist/$(os) 3.10.0

#build-darwin: dist/$(os)/$(app_name) # $(about-file) $(help-file) # NEWS.html
#	packagesbuild dev/installer-builders/macos/packages-config/Urial.pkgproj
#	mv dist/Urial-mac.pkg dist/Urial-$(release)-macos-$(macos_vers).pkg 


# make release ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

release: | test-branch release-on-github print-instructions

test-branch: vars
ifneq ($(branch),main)
	$(error Current git branch != main. Merge changes into main first!)
endif

update-init: vars
	@sed -i .bak -e "s|^\(__version__ *=\).*|\1 '$(version)'|"  $(init_file)
	@sed -i .bak -e "s|^\(__description__ *=\).*|\1 '$(desc)'|" $(init_file)
	@sed -i .bak -e "s|^\(__url__ *=\).*|\1 '$(url)'|"	    $(init_file)
	@sed -i .bak -e "s|^\(__author__ *=\).*|\1 '$(author)'|"    $(init_file)
	@sed -i .bak -e "s|^\(__email__ *=\).*|\1 '$(email)'|"	    $(init_file)
	@sed -i .bak -e "s|^\(__license__ *=\).*|\1 '$(license)'|"  $(init_file)

update-meta: vars
	@sed -i .bak -e "/version/ s/[0-9].[0-9][0-9]*.[0-9][0-9]*/$(version)/" codemeta.json

update-citation: vars
	@sed -i .bak -e "/^version/ s/[0-9].[0-9][0-9]*.[0-9][0-9]*/$(version)/" CITATION.cff


edited := codemeta.json $(init_file) CITATION.cff

commit-updates: vars
	git add $(edited)
	git diff-index --quiet HEAD $(edited) || \
	    git commit -m"Update stored version number" $(edited)

release-on-github: | vars update-init update-meta update-citation commit-updates
	$(eval tmp_file  := $(shell mktemp /tmp/release-notes-$(name).XXXX))
	git push -v --all
	git push -v --tags
	$(info ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓)
	$(info ┃ Write release notes in the file opened in your editor, then ┃)
	$(info ┃ save & close the file to complete the release process.      ┃)
	$(info ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛)
	sleep 2
	$(EDITOR) $(tmp_file)
	gh release create v$(version) -t "Release $(version)" -F $(tmp_file)

print-instructions:;
	$(info ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓)
	$(info ┃ Next steps:                                                 ┃)
	$(info ┃ 1. Visit https://github.com/$(repo)/releases )
	$(info ┃ 2. Double-check the release                                 ┃)
	$(info ┃ 3. Wait a few seconds to let web services do their work     ┃)
	$(info ┃ 4. Run "make update-doi" to update the DOI in README.md     ┃)
	$(info ┃ 5. Run "make packages" and check the distribution           ┃)
	$(info ┃ 6. Run "make test-pypi" to push to test.pypi.org            ┃)
	$(info ┃ 7. Double-check https://test.pypi.org/$(repo) )
	$(info ┃ 8. Run "make pypi" to push to pypi for real                 ┃)
	$(info ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛)
	@echo ""

update-doi: vars
	sed -i .bak -e 's|/api/record/[0-9]\{1,\}|/api/record/$(doi_tail)|' README.md
	sed -i .bak -e 's|edu/records/[0-9]\{1,\}|edu/records/$(doi_tail)|' README.md
	sed -i .bak -e '/doi:/ s|10.22002/[0-9]\{1,\}|10.22002/$(doi_tail)|' CITATION.cff
	git add README.md CITATION.cff
	git diff-index --quiet HEAD README.md || \
	     (git commit -m"Update DOI" README.md && git push -v --all)
	git diff-index --quiet HEAD CITATION.cff || \
	     (git commit -m"Update DOI" CITATION.cff && git push -v --all)

packages: | vars
	-mkdir -p dist/$(os)
	-mkdir -p build/$(os)
	python3 setup.py sdist bdist_wheel
	mv dist/$(name)-$(version).tar.gz dist/$(os)/
	mv dist/$(name)-$(version)-py3-none-any.whl dist/$(os)/
	python3 -m twine check dist/$(os)/$(name)-$(version).tar.gz
	python3 -m twine check dist/$(os)/$(name)-$(version)-py3-none-any.whl

test-pypi: packages
	python3 -m twine upload --repository testpypi dist/$(os)/$(name)-$(version)*.{whl,gz}

pypi: packages
	python3 -m twine upload dist/$(os)/$(name)-$(version)*.{gz,whl}


# Cleanup and miscellaneous directives ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

clean: clean-dist clean-build clean-release clean-other

really-clean: clean really-clean-dist really-clean-build

clean-dist:
	-rm -fr dist/$(os)/$(name) dist/$(os)/$(app_name) $(zip_file) \
	    dist/$(name)-$(version)-py3-none-any.whl

really-clean-dist:
	-rm -fr dist

clean-build:
	-rm -rf build/$(os)

really-clean-build:
	-rm -rf build

clean-release:
	-rm -f $(name).egg-info codemeta.json.bak $(init_file).bak README.md.bak

clean-other:
	-rm -f *.pyc $(name)/*.pyc 
	-rm -f __pycache__ $(name)/__pycache__
	-rm -rf .cache

.PHONY: release release-on-github update-init update-meta update-citation \
	print-instructions packages clean test-pypi pypi
