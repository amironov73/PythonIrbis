@echo off

SET PYTHON="C:\Python36-x64\python.exe"
SET PIP="C:\Python36-x64\Scripts\pip.exe"
SET COVERAGE="C:\Python36-x64\Scripts\coverage.exe"

%PYTHON% --version
%PYTHON% -m pip install --upgrade pip setuptools wheel

if not exist %COVERAGE% (%PIP% install coverage)
%COVERAGE% --version

SET PYTHONPATH=%~dp0

if NOT "L%APPVEYOR_BUILD_VERSION%L" == "LL" (
%PYTHON% utils\patch_version.py irbis\__init__.py %APPVEYOR_BUILD_VERSION%
%PYTHON% utils\patch_version.py setup.py %APPVEYOR_BUILD_VERSION%
)

%COVERAGE% run tests\offline_tests.py
%COVERAGE% report
%COVERAGE% html

%PYTHON% setup.py sdist bdist_wheel
