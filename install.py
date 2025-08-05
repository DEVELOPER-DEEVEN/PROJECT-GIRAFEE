#!/usr/bin/env python3
"""
Installation script for Windows AI Assistant
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True


def check_platform():
    """Check if running on Windows"""
    if platform.system() != "Windows":
        print("❌ This application is designed for Windows")
        print(f"Current platform: {platform.system()}")
        return False
    print("✅ Windows platform detected")
    return True


def create_virtual_environment():
    """Create a virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def install_dependencies():
    """Install required dependencies"""
    try:
        # Determine the pip command based on the platform
        if platform.system() == "Windows":
            pip_cmd = "venv\\Scripts\\pip"
        else:
            pip_cmd = "venv/bin/pip"
        
        print("Installing dependencies...")
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_launcher_script():
    """Create a launcher script"""
    launcher_content = """@echo off
echo Starting Windows AI Assistant...
cd /d "%~dp0"
venv\\Scripts\\python.exe src\\main.py
pause
"""
    
    try:
        with open("run_assistant.bat", "w") as f:
            f.write(launcher_content)
        print("✅ Launcher script created (run_assistant.bat)")
        return True
    except Exception as e:
        print(f"❌ Failed to create launcher script: {e}")
        return False


def create_desktop_shortcut():
    """Create a desktop shortcut"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "Windows AI Assistant.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = os.path.abspath("run_assistant.bat")
        shortcut.WorkingDirectory = os.path.abspath(".")
        shortcut.IconLocation = os.path.abspath("src\\main.py")
        shortcut.save()
        
        print("✅ Desktop shortcut created")
        return True
    except ImportError:
        print("⚠️  Could not create desktop shortcut (missing pywin32)")
        return False
    except Exception as e:
        print(f"❌ Failed to create desktop shortcut: {e}")
        return False


def main():
    """Main installation function"""
    print("🚀 Windows AI Assistant - Installation")
    print("=" * 50)
    
    # Check requirements
    if not check_python_version():
        return False
    
    if not check_platform():
        return False
    
    # Create virtual environment
    if not create_virtual_environment():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create launcher script
    if not create_launcher_script():
        return False
    
    # Create desktop shortcut (optional)
    create_desktop_shortcut()
    
    print("\n🎉 Installation completed successfully!")
    print("\nTo start the application:")
    print("1. Double-click 'run_assistant.bat'")
    print("2. Or run: venv\\Scripts\\python.exe src\\main.py")
    print("\nFor help, see README.md")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 