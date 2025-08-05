#!/usr/bin/env python3
"""
Launcher for Windows AI Assistant executable
"""

import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import Config
from ui.main_window import MainWindow
from utils.logger import setup_logging


def check_first_run():
    """Check if this is the first run and setup initial configuration"""
    config_dir = Path.home() / ".windows_ai_assistant"
    config_file = config_dir / "config.json"
    
    if not config_file.exists():
        # Create initial configuration with Gemini API key
        config_dir.mkdir(parents=True, exist_ok=True)
        
        initial_config = {
            'ai': {
                'model_name': 'gpt-3.5-turbo',
                'max_tokens': 2048,
                'temperature': 0.7,
                'api_key': None,
                'use_local_models': True,
                'local_model_path': None,
                'gemini_api_key': 'AIzaSyA8XM56HBBQoVjO_XlCwOKyxeEFRMfomC8',
                'gemini_model': 'gemini-pro',
                'use_gemini': True
            },
            'ui': {
                'window_width': 1000,
                'window_height': 700,
                'theme': 'light',
                'language': 'en',
                'auto_hide': True,
                'transparency': 0.9
            },
            'automation': {
                'default_delay': 0.1,
                'click_delay': 0.05,
                'type_delay': 0.01,
                'screenshot_quality': 90,
                'max_screenshot_size': 1920,
                'enable_visual_feedback': True
            },
            'workflow': {
                'max_workflows': 100,
                'auto_save': True,
                'backup_enabled': True,
                'max_backup_count': 10
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(initial_config, f, indent=2, ensure_ascii=False)
        
        return True
    
    return False


def show_welcome_message():
    """Show welcome message for first-time users"""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("Welcome to Windows AI Assistant")
    msg.setText("Welcome to Windows AI Assistant!")
    msg.setInformativeText(
        "This is your first time running the application.\n\n"
        "Features:\n"
        "• Natural language computer control\n"
        "• Windows automation\n"
        "• Workflow creation and scheduling\n"
        "• AI-powered assistance\n\n"
        "Your Gemini API key has been pre-configured.\n"
        "You can change settings in the Settings tab."
    )
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()


def create_splash_screen():
    """Create a splash screen"""
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(Qt.GlobalColor.white)
    
    # Create a simple splash screen
    splash = QSplashScreen(splash_pix)
    splash.setWindowTitle("Windows AI Assistant")
    
    # Add text to splash screen
    label = QLabel("Windows AI Assistant\nLoading...", splash)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet("""
        QLabel {
            color: #0078d4;
            font-size: 18pt;
            font-weight: bold;
        }
    """)
    label.setGeometry(50, 100, 300, 100)
    
    return splash


def main():
    """Main launcher function"""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Windows AI Assistant")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Windows AI Assistant")
    
    # Setup logging
    setup_logging()
    
    # Check if first run
    is_first_run = check_first_run()
    
    # Show splash screen
    splash = create_splash_screen()
    splash.show()
    
    # Process events to show splash screen
    app.processEvents()
    
    # Simulate loading time
    QTimer.singleShot(2000, lambda: None)
    
    try:
        # Load configuration
        config = Config()
        
        # Create and show main window
        window = MainWindow(config)
        
        # Close splash screen and show main window
        splash.finish(window)
        window.show()
        
        # Show welcome message for first-time users
        if is_first_run:
            QTimer.singleShot(500, show_welcome_message)
        
        # Start the application
        sys.exit(app.exec())
        
    except Exception as e:
        splash.close()
        QMessageBox.critical(None, "Error", f"Failed to start Windows AI Assistant:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 