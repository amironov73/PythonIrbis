@echo off

rem Ётот скрипт нужен лишь дл€ сокрыти€ кода возврата pylint

:AGAIN

if "%1" == "" goto :DONE

python -m pylint %1

shift

goto :AGAIN

:DONE

echo All done