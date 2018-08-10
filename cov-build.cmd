@echo off

SET COVERITY=D:\Coverity
SET COVERITY_BIN=%COVERITY%\bin

SET PYTHONPATH=%~dp0

%COVERITY_BIN%\cov-build.exe --dir D:\Projects\PythonIrbis\cov-int --no-command --fs-capture-search D:\Projects\PythonIrbis\pyirbis python pyirbis/ext.py
