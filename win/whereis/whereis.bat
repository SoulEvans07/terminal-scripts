@echo OFF

set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.\

groovy.bat "%DIRNAME%\where.groovy" %*