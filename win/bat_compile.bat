@echo off
set DIR="C:\.util"
py %DIR%\cmdcompiler\compile.py %1 %2 %3 %4 %5 %6 %7 %8 %9
@echo Press any key to close...
pause >nul