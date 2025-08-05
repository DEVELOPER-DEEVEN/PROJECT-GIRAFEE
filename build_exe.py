#!/usr/bin/env python3
"""
Build script for creating Windows AI Assistant executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import PyInstaller.__main__


def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}")


def create_version_info():
    """Create version info for the executable"""
    version_info = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Windows AI Assistant'),
         StringStruct(u'FileDescription', u'Windows AI Assistant - Natural Language Computer Control'),
         StringStruct(u'FileVersion', u'1.0.0'),
         StringStruct(u'InternalName', u'windows_ai_assistant'),
         StringStruct(u'LegalCopyright', u'Copyright (c) 2024'),
         StringStruct(u'OriginalFilename', u'WindowsAIAssistant.exe'),
         StringStruct(u'ProductName', u'Windows AI Assistant'),
         StringStruct(u'ProductVersion', u'1.0.0')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    with open('version_info.txt', 'w') as f:
        f.write(version_info)
    
    return 'version_info.txt'


def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('SETUP.md', '.'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'loguru',
        'openai',
        'google.generativeai',
        'transformers',
        'torch',
        'pyautogui',
        'pywinauto',
        'psutil',
        'requests',
        'numpy',
        'PIL',
        'cv2',
        'sqlalchemy',
        'apscheduler',
        'keyboard',
        'mouse',
        'spacy',
        'nltk',
        'textblob',
        'click',
        'rich',
        'tqdm',
        'colorama',
        'pydantic',
        'python-dotenv',
        'alembic',
        'schedule',
        'aiohttp',
        'httpx',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WindowsAIAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
'''
    
    with open('WindowsAIAssistant.spec', 'w') as f:
        f.write(spec_content)
    
    return 'WindowsAIAssistant.spec'


def create_installer_script():
    """Create NSIS installer script"""
    nsis_script = '''
!define APPNAME "Windows AI Assistant"
!define COMPANYNAME "Windows AI Assistant"
!define DESCRIPTION "Natural Language Computer Control"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/your-repo"
!define UPDATEURL "https://github.com/your-repo"
!define ABOUTURL "https://github.com/your-repo"
!define INSTALLSIZE 50000

RequestExecutionLevel admin

InstallDir "$PROGRAMFILES\\${COMPANYNAME}\\${APPNAME}"

Name "${APPNAME}"
Icon "assets\\icon.ico"
outFile "WindowsAIAssistant-Setup.exe"

!include LogicLib.nsh

Page license
Page directory
Page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
Pop $0
${If} $0 != "admin"
        messageBox mb_iconstop "Administrator rights required!"
        SetErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
        Quit
${EndIf}
!macroend

function .onInit
	setShellVarContext all
	!insertmacro VerifyUserIsAdmin
functionEnd

licenseData "LICENSE.txt"

section "install"
	setOutPath $INSTDIR
	file /r "dist\\WindowsAIAssistant\\*.*"
	
	writeUninstaller "$INSTDIR\\uninstall.exe"

	createDirectory "$SMPROGRAMS\\${COMPANYNAME}"
	createShortCut "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk" "$INSTDIR\\WindowsAIAssistant.exe" "" "$INSTDIR\\WindowsAIAssistant.exe"
	createShortCut "$SMPROGRAMS\\${COMPANYNAME}\\Uninstall ${APPNAME}.lnk" "$INSTDIR\\uninstall.exe" "" "$INSTDIR\\uninstall.exe"

	createShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\WindowsAIAssistant.exe" "" "$INSTDIR\\WindowsAIAssistant.exe"

	writeRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
	writeRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "UninstallString" "\\"$INSTDIR\\uninstall.exe\\""
	writeRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "QuietUninstallString" "\\"$INSTDIR\\uninstall.exe\\" /S"
	writeRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$INSTDIR"
	writeRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$INSTDIR\\WindowsAIAssistant.exe"
	writeRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
	writeRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "HelpLink" "${HELPURL}"
	writeRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
	writeRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
	writeRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
	writeRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
	writeRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
	writeRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoModify" 1
	writeRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
	writeRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
sectionEnd

section "uninstall"
	delete "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk"
	delete "$SMPROGRAMS\\${COMPANYNAME}\\Uninstall ${APPNAME}.lnk"
	delete "$DESKTOP\\${APPNAME}.lnk"

	rmDir "$SMPROGRAMS\\${COMPANYNAME}"

	delete "$INSTDIR\\uninstall.exe"
	rmDir /r "$INSTDIR"

	deleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}"
sectionEnd
'''
    
    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)


def create_assets():
    """Create assets directory and placeholder icon"""
    assets_dir = Path('assets')
    assets_dir.mkdir(exist_ok=True)
    
    # Create a simple placeholder icon (you should replace this with your actual icon)
    icon_content = '''
# This is a placeholder for the application icon
# Replace this with your actual .ico file
'''
    
    with open('assets/icon.ico', 'w') as f:
        f.write(icon_content)


def create_license():
    """Create license file"""
    license_content = '''
MIT License

Copyright (c) 2024 Windows AI Assistant

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
    
    with open('LICENSE.txt', 'w') as f:
        f.write(license_content)


def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building Windows AI Assistant Executable")
    print("=" * 50)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create necessary files
    create_assets()
    create_license()
    version_file = create_version_info()
    spec_file = create_spec_file()
    
    # Build the executable
    print("Building executable...")
    PyInstaller.__main__.run([
        spec_file,
        '--clean',
        '--noconfirm',
        '--log-level=INFO'
    ])
    
    print("✅ Executable built successfully!")
    print(f"Location: dist/WindowsAIAssistant/WindowsAIAssistant.exe")
    
    return True


def create_installer():
    """Create NSIS installer"""
    print("\n📦 Creating Installer")
    print("=" * 30)
    
    create_installer_script()
    
    # Check if NSIS is available
    try:
        subprocess.run(['makensis', '--version'], check=True, capture_output=True)
        print("Creating installer with NSIS...")
        subprocess.run(['makensis', 'installer.nsi'], check=True)
        print("✅ Installer created: WindowsAIAssistant-Setup.exe")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  NSIS not found. Installer not created.")
        print("To create installer, install NSIS and run: makensis installer.nsi")


def main():
    """Main build function"""
    print("🚀 Windows AI Assistant - Build System")
    print("=" * 50)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    # Build executable
    if build_executable():
        print("\n🎉 Build completed successfully!")
        print("\nFiles created:")
        print("- dist/WindowsAIAssistant/WindowsAIAssistant.exe (Standalone executable)")
        print("- installer.nsi (NSIS installer script)")
        
        # Create installer
        create_installer()
        
        print("\n📋 Distribution Instructions:")
        print("1. For standalone distribution: Copy the entire 'dist/WindowsAIAssistant' folder")
        print("2. For installer distribution: Use the generated NSIS installer")
        print("3. The executable is self-contained and doesn't require Python installation")
        
    else:
        print("❌ Build failed!")


if __name__ == "__main__":
    main() 