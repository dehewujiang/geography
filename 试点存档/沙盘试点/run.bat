@echo off
rem sandbox pilot launcher: starts local server (minimal window) then opens the page
cd /d %~dp0..\..
start "shapan-server" /min cmd /c "python -m http.server 8765"
timeout /t 2 /nobreak >nul
start "" "http://localhost:8765/试点存档/沙盘试点/index.html"
