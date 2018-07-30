@echo off

SET PYTHON="C:\Python36-x64\python.exe"
SET PIP="C:\Python36-x64\Scripts\pip.exe"

%PYTHON% --version
%PIP% --version

SET PYTHONPATH=%~dp0

%PYTHON% tests\offline_tests.py