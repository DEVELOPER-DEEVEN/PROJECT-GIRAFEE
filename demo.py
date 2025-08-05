#!/usr/bin/env python3
"""
Demo script for Windows AI Assistant
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from core.config import Config
from ui.main_window import MainWindow
from utils.logger import setup_logging


def run_demo():
    """Run the Windows AI Assistant demo"""
    print("🚀 Starting Windows AI Assistant Demo")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Windows AI Assistant - Demo")
    app.setApplicationVersion("1.0.0")
    
    # Load configuration
    config = Config()
    
    # Create and show main window
    window = MainWindow(config)
    window.show()
    
    print("✅ Application started successfully!")
    print("\nDemo Features:")
    print("• Natural language chat interface")
    print("• Windows automation capabilities")
    print("• Workflow management system")
    print("• Settings configuration")
    print("\nTry these commands:")
    print("• 'Open Chrome and search for Python tutorials'")
    print("• 'Open notepad and type Hello World'")
    print("• 'What can you do?'")
    print("• 'Help me create a workflow'")
    
    # Start the application
    sys.exit(app.exec())


if __name__ == "__main__":
    run_demo() 