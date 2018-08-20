@echo off

rem Этот скрипт нужен лишь для сокрытия кода возврата pylint 
rem и предотвращения его вылетания из-за неумения работать с кодировками

chcp 65001

:AGAIN

if "%1" == "" goto :DONE

python -m pylint %1

shift

goto :AGAIN

:DONE

chcp 1252

echo All done