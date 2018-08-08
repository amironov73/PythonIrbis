@echo off

SET PYTHON="C:\Python36-x64\python.exe"
SET PIP="C:\Python36-x64\Scripts\pip.exe"
SET COVERAGE="C:\Python36-x64\Scripts\coverage.exe"

%PYTHON% --version
%PYTHON% -m pip install --upgrade pip setuptools wheel

if not exist %COVERAGE% (%PIP% install coverage)
%COVERAGE% --version

SET PYTHONPATH=%~dp0

%COVERAGE% run tests\offline_tests.py
%COVERAGE% report
%COVERAGE% html

%PYTHON% setup.py sdist bdist_wheel
