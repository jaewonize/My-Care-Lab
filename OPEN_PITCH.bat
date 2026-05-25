@echo off
title My Care Lab Pitch
echo.
echo   Opening My Care Lab pitch...
echo.

set "HTML=%~dp0index.html"
set "PROFILE=%TEMP%\mcl_pitch_profile"
set "BROWSER="

set "C1=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
set "C2=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
set "C3=%LocalAppData%\Google\Chrome\Application\chrome.exe"
set "E1=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
set "E2=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"

if exist "%C1%" set "BROWSER=%C1%"
if not defined BROWSER if exist "%C2%" set "BROWSER=%C2%"
if not defined BROWSER if exist "%C3%" set "BROWSER=%C3%"
if not defined BROWSER if exist "%E1%" set "BROWSER=%E1%"
if not defined BROWSER if exist "%E2%" set "BROWSER=%E2%"

if not defined BROWSER (
  echo   [!] Chrome or Edge not found. One of them must be installed.
  echo.
  pause
  exit /b
)

echo   Browser found. Opening a new window...
start "" "%BROWSER%" --allow-file-access-from-files --user-data-dir="%PROFILE%" --new-window "%HTML%"

echo.
echo   Done. A new browser window is opening.
ping -n 3 127.0.0.1 >nul
