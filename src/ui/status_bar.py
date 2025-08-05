"""
Status bar widget for displaying application status
"""

from PyQt6.QtWidgets import QStatusBar, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette
from loguru import logger


class StatusBar(QStatusBar):
    """Enhanced status bar with progress indication"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """Setup the status bar UI"""
        # Main status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: 500;
            }
        """)
        self.addWidget(self.status_label)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 2px;
            }
        """)
        self.addPermanentWidget(self.progress_bar)
        
        # Error label (hidden by default)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-weight: 500;
            }
        """)
        self.error_label.setVisible(False)
        self.addPermanentWidget(self.error_label)
    
    def setup_timer(self):
        """Setup timer for auto-clearing messages"""
        self.clear_timer = QTimer()
        self.clear_timer.timeout.connect(self.clear_error)
        self.clear_timer.setSingleShot(True)
    
    def update_status(self, message: str):
        """Update the status message"""
        logger.debug(f"Status update: {message}")
        self.status_label.setText(message)
        
        # Auto-clear after 5 seconds for non-persistent messages
        if not message.startswith("Ready") and not message.startswith("Error"):
            QTimer.singleShot(5000, lambda: self.clear_status())
    
    def show_progress(self, visible: bool = True, value: int = 0):
        """Show or hide the progress bar"""
        self.progress_bar.setVisible(visible)
        if visible:
            self.progress_bar.setValue(value)
    
    def update_progress(self, value: int):
        """Update progress bar value"""
        self.progress_bar.setValue(value)
    
    def show_error(self, error_message: str):
        """Show an error message"""
        logger.error(f"Status bar error: {error_message}")
        
        # Show error in status label
        self.status_label.setText(f"Error: {error_message}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-weight: 500;
            }
        """)
        
        # Show error label
        self.error_label.setText("⚠")
        self.error_label.setVisible(True)
        
        # Auto-clear after 10 seconds
        self.clear_timer.start(10000)
    
    def clear_error(self):
        """Clear error messages"""
        self.error_label.setVisible(False)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: 500;
            }
        """)
        self.status_label.setText("Ready")
    
    def clear_status(self):
        """Clear status message if it's not an error"""
        current_text = self.status_label.text()
        if not current_text.startswith("Error"):
            self.status_label.setText("Ready")
    
    def show_success(self, message: str):
        """Show a success message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #28a745;
                font-weight: 500;
            }
        """)
        
        # Reset to normal after 3 seconds
        QTimer.singleShot(3000, lambda: self.clear_error())
    
    def show_warning(self, message: str):
        """Show a warning message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffc107;
                font-weight: 500;
            }
        """)
        
        # Reset to normal after 5 seconds
        QTimer.singleShot(5000, lambda: self.clear_error()) 