@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo   CCI ^> CIA Converter - Build
echo ==========================================
echo.

if not exist "vendor\3dsconv.py" (
    echo FEHLER: vendor\3dsconv.py fehlt.
    echo Bitte die offizielle 3dsconv.py in vendor\ ablegen.
    pause
    exit /b 1
)

py -3 -m pip install --upgrade pip
if errorlevel 1 goto :error

py -3 -m pip install -r requirements.txt
if errorlevel 1 goto :error

py -3 -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "CCI_to_CIA_Converter" ^
  --add-data "vendor\3dsconv.py;vendor" ^
  cci_to_cia_gui.py

if errorlevel 1 goto :error

echo.
echo ==========================================
echo Fertig!
echo EXE: dist\CCI_to_CIA_Converter.exe
echo ==========================================
pause
exit /b 0

:error
echo.
echo BUILD FEHLGESCHLAGEN.
pause
exit /b 1
