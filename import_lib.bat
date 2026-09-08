@echo off
pushd %~dp0

echo ================================
echo   Starte Bauteil-Import-Tool
echo ================================
echo.

python tools\import_lib.py

echo.
echo ================================
echo   Fertig! Ausgabe oben ansehen.
echo ================================
echo.

pause
popd
