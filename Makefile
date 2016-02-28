.PHONY: clean-pyc clean-build docs clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "test - run tests quickly with the default Python"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "check - package & run metadata sanity checks"
	@echo "run - runserver"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

test: clean-pyc clean-test
	python -B -R -tt -W ignore setup.py test

release: dist
	twine upload dist/*

dist: test clean
	python setup.py sdist bdist_wheel
	ls -l dist

check: dist
	check-manifest
	pyroma .
	restview --long-description

install: clean
	python setup.py install

run: clean-pyc
	python demo_project.py runserver 0.0.0.0:8080
