@echo off

rem ���� ������ ����� ���� ��� �������� ���� �������� pylint

:AGAIN

if "%1" == "" goto :DONE

python -m pylint %1

shift

goto :AGAIN

:DONE

echo All done