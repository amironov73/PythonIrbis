@echo off

rem ���� ������ ����� ���� ��� �������� ���� �������� pylint 
rem � �������������� ��� ��������� ��-�� �������� �������� � �����������

chcp 65001

:AGAIN

if "%1" == "" goto :DONE

python -m pylint %1

shift

goto :AGAIN

:DONE

chcp 1252

echo All done