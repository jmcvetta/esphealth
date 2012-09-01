@echo off
:: Prepare the Command Processor
SETLOCAL ENABLEEXTENSIONS
SETLOCAL ENABLEDELAYEDEXPANSION

:: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:: 
::                                  ESP Health
::                                 Setup Script
:: 
:: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:: 
::  This script must be run by a user with write permission on the ESP'
::  folder.
:: 
:: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::
:: Main Logic
:: 
:: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if [%1]==[] (
    call :usage
    exit /b 1
)

:: Uncomment the following for debugging
:: echo on

for %%a in (%*) do (
    if "%%a"=="-i" (
        call :install
    ) else if "%%a"=="-d" (
        call :update_dependencies
    ) else if "%%a"=="-p" (
        call :update_plugins
    ) else if "%%a"=="-f" (
        call :freeze_requirements
    ) else if "%%a"=="-h" (
        call :usage
    ) else (
        call :usage
        exit /b 1
    )
)
exit /b


:usage
echo usage: setup option
echo   -i  Install ESP (first time installation)
echo   -d  Update PyPI dependency modules
echo   -p  Update ESP plugin modules
echo   -f  Freeze PIP requirements to requirements.frozen.txt
echo   -h  Show this usage message"
pause
exit /b


:activate_virtualenv
call Scripts\activate.bat
set PIP_RESPECT_VIRTUALENV=true
set PIP_REQUIRE_VIRTUALENV=true
exit /b


:install
:: Create the virtual environment, then install modules from the frozen
:: list.
::
echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
echo +
echo + Installing ESP...
echo +
echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
virtualenv --no-site-packages . 
call :activate_virtualenv
pip install -r requirements.frozen.txt
exit /b


:update_dependencies
:: Update dependency modules with the latest version from PyPI.
:: 
echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
echo +
echo + Updating PyPI dependency modules...
echo +
echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
call :activate_virtualenv
pip install -U -v -r requirements.pypi.txt
exit /b


:update_plugins
:: Update ESP plugin modules with the latest versions.
::
echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
echo +
echo + Updating ESP plugin modules...
echo +
echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
call :activate_virtualenv
pip install -U -v -r requirements.plugins.txt
exit /b


:freeze_requirements
:: Freeze currently installed modules to requirements.frozen.txt.
::
echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
echo +
echo + Freezing requirements...
echo +
echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
call :activate_virtualenv
pip freeze > requirements.frozen.txt
exit /b
