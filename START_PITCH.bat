@echo off
title My Care Lab Pitch (server)
cd /d "%~dp0"
echo.
echo   Starting local server and opening the pitch...
echo   (keep the other black window open; close it to stop the server)
echo.
start "My Care Lab Server" cmd /k npx --yes http-server . -p 4173 -c-1 --silent
timeout /t 2 /nobreak >nul
start "" http://localhost:4173/index.html
exit
