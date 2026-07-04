@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] .venv\Scripts\python.exe not found.
  pause
  exit /b 1
)

if not exist "config.cloud.json" (
  echo [ERROR] config.cloud.json not found.
  echo Copy config.cloud.example.json to config.cloud.json and edit it first.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" ".\cloud_link_uploader.py" %*
echo.
pause


