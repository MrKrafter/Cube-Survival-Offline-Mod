@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 cube_patcher.py %*
    goto done
)
where python >nul 2>nul
if %errorlevel%==0 (
    python cube_patcher.py %*
    goto done
)
echo Python 3 не найден. Установите его с https://www.python.org/downloads/ и запустите снова.
echo Python 3 was not found. Install it from https://www.python.org/downloads/ and run this again.
:done
pause
