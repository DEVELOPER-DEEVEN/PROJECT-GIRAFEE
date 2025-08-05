"""
Main application window for the Windows AI Assistant
"""

import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QLabel, QFrame, QSplitter,
    QTabWidget, QScrollArea, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor
from loguru import logger

from core.config import Config
from ui.chat_widget import ChatWidget
from ui.workflow_widget import WorkflowWidget
from ui.settings_widget import SettingsWidget
from ui.status_bar import StatusBar
from core.ai_engine import AIEngine
from core.automation_engine import AutomationEngine


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.ai_engine = AIEngine(config)
        self.automation_engine = AutomationEngine(config)
        
        self.setup_ui()
        self.setup_connections()
        self.setup_styles()
        
        logger.info("Main window initialized")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Window properties
        self.setWindowTitle("Windows AI Assistant")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)
        
        # Center window on screen
        self.center_window()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Chat interface
        self.chat_widget = ChatWidget(self.ai_engine, self.automation_engine)
        splitter.addWidget(self.chat_widget)
        
        # Right panel - Tabs for workflows, settings, etc.
        self.setup_right_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([600, 400])
        
        # Status bar
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)
        
        # Menu bar
        self.setup_menu_bar()
    
    def setup_right_panel(self, splitter: QSplitter):
        """Setup the right panel with tabs"""
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumWidth(300)
        splitter.addWidget(self.tab_widget)
        
        # Workflows tab
        self.workflow_widget = WorkflowWidget(self.config)
        self.tab_widget.addTab(self.workflow_widget, "Workflows")
        
        # Settings tab
        self.settings_widget = SettingsWidget(self.config)
        self.tab_widget.addTab(self.settings_widget, "Settings")
        
        # Set tab style
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #0078d4;
            }
        """)
    
    def setup_menu_bar(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # New workflow action
        new_workflow_action = file_menu.addAction("&New Workflow")
        new_workflow_action.setShortcut("Ctrl+N")
        new_workflow_action.triggered.connect(self.new_workflow)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = file_menu.addAction("E&xit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Settings action
        settings_action = tools_menu.addAction("&Settings")
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # About action
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.show_about)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect AI engine signals
        self.ai_engine.status_updated.connect(self.status_bar.update_status)
        self.ai_engine.error_occurred.connect(self.handle_error)
        
        # Connect automation engine signals
        self.automation_engine.status_updated.connect(self.status_bar.update_status)
        self.automation_engine.error_occurred.connect(self.handle_error)
        
        # Connect workflow widget signals
        self.workflow_widget.workflow_created.connect(self.chat_widget.add_workflow)
    
    def setup_styles(self):
        """Setup application styles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
            }
            
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #106ebe;
            }
            
            QPushButton:pressed {
                background-color: #005a9e;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            
            QTextEdit:focus {
                border-color: #0078d4;
            }
        """)
    
    def center_window(self):
        """Center the window on the screen"""
        screen = self.screen()
        screen_geometry = screen.geometry()
        window_geometry = self.geometry()
        
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        
        self.move(x, y)
    
    def new_workflow(self):
        """Create a new workflow"""
        logger.info("Creating new workflow")
        self.tab_widget.setCurrentWidget(self.workflow_widget)
        self.workflow_widget.create_new_workflow()
    
    def show_settings(self):
        """Show settings dialog"""
        logger.info("Opening settings")
        self.tab_widget.setCurrentWidget(self.settings_widget)
    
    def show_about(self):
        """Show about dialog"""
        from PyQt6.QtWidgets import QMessageBox
        
        QMessageBox.about(
            self,
            "About Windows AI Assistant",
            """
            <h3>Windows AI Assistant</h3>
            <p>Version 1.0.0</p>
            <p>A natural language interface for Windows automation.</p>
            <p>Built with Python and PyQt6</p>
            """
        )
    
    def handle_error(self, error_message: str):
        """Handle errors from AI or automation engines"""
        logger.error(f"Error occurred: {error_message}")
        self.status_bar.show_error(error_message)
    
    def closeEvent(self, event):
        """Handle application close event"""
        logger.info("Application closing")
        
        # Save configuration
        self.config.save()
        
        # Stop AI and automation engines
        self.ai_engine.stop()
        self.automation_engine.stop()
        
        event.accept() 