@echo off
:: Prepare the Command Processor
SETLOCAL ENABLEEXTENSIONS
SETLOCAL ENABLEDELAYEDEXPANSION

:: ===============================================================================
:: 
::                              ESP Health Project
:: 
::                          './bin/esp' Wrapper Script
:: 
:: 
::  Wrapper script for running ESP commands.  Sets PYTHONPATH to ESP 'src' folder
::  and calls 'manage.py'.  
:: 
:: ===============================================================================
:: 
:: 
::  @author: Jason McVetta <jason.mcvetta@gmail.com>
::  @organization: Channing Laboratory http://www.channing.harvard.edu
::  @contact: http://esphealth.org
::  @copyright: (c) 2009-2010 Channing Laboratory
::  @license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
:: 
:: ===============================================================================

:: Uncomment the following for debugging
:: echo on

:: IF path to Python executable has not been specified, use system default
if "%PYTHON%" == "" (
    call :where python PYTHON
)

:: Calculate path to ESP installation based on location of this script
call :dirname %0 _bin_dir
call :dirname %_bin_dir% ESP_HOME

:: Activate virtualenv
call %ESP_HOME%\Scripts\activate.bat

:: Call manage.py
set DJANGO_SETTINGS_MODULE=ESP.settings
set PYTHONPATH=%ESP_HOME%
%ESP_HOME%\Scripts\python %ESP_HOME%\ESP\manage.py %*

exit /b


:where cmd result_var
:: Search PATH for "cmd"
:: Return the result in "var_results"
for %%e in (%PATHEXT%) do (
    for %%i in (%1%%e) do (
        if NOT "%%~$PATH:i" == "" (
            set "%~2=%%~$PATH:i"
        )
    )
)
exit /b


:dirname file result_var
:: Return the directory name for the specified file by getting the
:: directory and stripping the trailing backslash
setlocal
set "d=%~dp1"
set "d=%d:~0,-1%
endlocal & set "%~2=%d%"
exit /b