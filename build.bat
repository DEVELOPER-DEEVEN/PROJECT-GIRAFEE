@echo off
echo 🚀 Windows AI Assistant - Build Script
echo ======================================

echo.
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo.
echo Installing/updating PyInstaller...
pip install --upgrade pyinstaller

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building executable...
python build_exe.py

echo.
if exist "dist\WindowsAIAssistant\WindowsAIAssistant.exe" (
    echo ✅ Build completed successfully!
    echo.
    echo 📁 Executable location: dist\WindowsAIAssistant\WindowsAIAssistant.exe
    echo.
    echo 📦 Distribution files:
    echo    - dist\WindowsAIAssistant\ (entire folder for distribution)
    echo    - WindowsAIAssistant-Setup.exe (if NSIS installer was created)
    echo.
    echo 🎉 Ready for distribution!
) else (
    echo ❌ Build failed! Check the error messages above.
)

echo.
pause 