@echo off
REM ============================================================
REM  DayZ local solo server launcher (Expansion AI + Dynamic AI)
REM  Place this in your DayZServer folder (next to DayZServer_x64.exe).
REM  Edit the CONFIG block below, then double-click to run.
REM ============================================================

REM --- CONFIG -------------------------------------------------
set SERVER_EXE=DayZServer_x64.exe
set CFG=serverDZ.cfg
set PORT=2302
set PROFILES=profiles
set CPUCOUNT=4

REM Client-side mods (must ALSO load on the client), dependency order first.
REM Core MUST come before AI. Licensed is optional assets; include it if the
REM Expansion-AI Workshop page lists it under Required Items (place it after Core).
set CLIENT_MODS=@CF;@DabsFramework;@DayZ-Expansion-Core;@DayZ-Expansion-Licensed;@DayZ-Expansion-AI

REM Server-side-only mods (never load these on the client):
set SERVER_MODS=@DayZ-Dynamic-AI-Addon
REM ------------------------------------------------------------

cd /d "%~dp0"

:loop
echo [%date% %time%] Starting DayZ server on port %PORT% ...
"%SERVER_EXE%" -config=%CFG% -port=%PORT% ^
 -mod=%CLIENT_MODS% ^
 -serverMod=%SERVER_MODS% ^
 -profiles=%PROFILES% -cpuCount=%CPUCOUNT% -dologs -adminlog -netlog -freezecheck

echo [%date% %time%] Server exited. Restarting in 10s (Ctrl+C to stop)...
timeout /t 10
goto loop
