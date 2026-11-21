@echo off
setlocal enabledelayedexpansion

pushd "%~dp0"
set "PARENT=%~dp0..\"
set CLEAN=false
set CONFIG=Release
set SCHEMA=all
set DISCOVER=false
set JOBS=0
set USD_FLAVOR=usd-dev
set DIRECTORIES_TO_CLEAN=_install _build\cmake _build\usd-deps _build\host-deps

:parseargs
if "%~1"=="" goto :argsdone
if /I "%~1"=="--clean" (
    set CLEAN=true
    shift
    goto :parseargs
)
if /I "%~1"=="--debug" (
    set CONFIG=Debug
    shift
    goto :parseargs
)
if /I "%~1"=="--relwithdebinfo" (
    set CONFIG=RelWithDebInfo
    shift
    goto :parseargs
)
if /I "%~1"=="--discover" (
    set DISCOVER=true
    shift
    goto :parseargs
)
if /I "%~1"=="--schema" (
    if "%~2"=="" (
        echo [build.bat] --schema requires a schema name.
        goto :ArgError
    )
    set "SCHEMA=%~2"
    shift
    shift
    goto :parseargs
)
if /I "%~1"=="--jobs" (
    if "%~2"=="" (
        echo [build.bat] --jobs requires a number.
        goto :ArgError
    )
    set "JOBS=%~2"
    shift
    shift
    goto :parseargs
)
if /I "%~1"=="--help" (
    echo build.bat [--clean] [--debug ^| --relwithdebinfo] [--schema NAME] [--jobs N] [--discover] [--help]
    echo Builds USD schema plugins into _install
    echo   --schema NAME   Build only the schema whose libraryName is NAME ^(default: all^)
    echo   --jobs N        Max schemas built in parallel ^(default: all at once; 1 = sequential, live output^)
    echo   --discover      Print matching schemas and exit without building
    popd
    exit /b 0
)
echo [build.bat] Unknown argument: %~1
goto :ArgError

:argsdone

if "%CLEAN%"=="true" (
    for %%a in (%DIRECTORIES_TO_CLEAN%) DO (
        if exist "%PARENT%%%a\" rmdir /s /q "%PARENT%%%a"
    )
    goto :Success
)

set "PY_ARGS=--config %CONFIG% --schema %SCHEMA% --jobs %JOBS%"
if "%DISCOVER%"=="true" set "PY_ARGS=!PY_ARGS! --discover"

REM Discovery only walks source/extensions/; skip the packman fetch.
if not "%DISCOVER%"=="true" (
    call "%PARENT%tools\packman\python.bat" scripts\setup.py --usd-flavor=%USD_FLAVOR% --config=%CONFIG%
    if !errorlevel! neq 0 goto :Error
)

REM Discover every schema.usda under source/extensions/ and build each in its
REM own CMake project so per-schema CMAKE_INSTALL_PREFIX values don't collide.
REM Schemas build in parallel and share one schemagen venv (_build\schemagen_venv).
call "%PARENT%tools\packman\python.bat" "%~dp0scripts\build_schemas.py" !PY_ARGS!
if !errorlevel! neq 0 goto :Error

:Success
popd
exit /b 0

:ArgError
popd
exit /b 1

:Error
echo.
echo [build.bat] Schema build failed with exit code !errorlevel!.
echo [build.bat] See error output above.
popd
exit /b !errorlevel!
