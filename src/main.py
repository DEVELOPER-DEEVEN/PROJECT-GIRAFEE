#!/usr/bin/env python3
"""
Main entry point for the Windows AI Assistant application
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
from core.config import Config
from utils.logger import setup_logging

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Windows AI Assistant")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Windows AI Assistant")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Load configuration
    config = Config()
    
    # Create and show main window
    window = MainWindow(config)
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 