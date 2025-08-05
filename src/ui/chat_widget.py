"""
Chat widget for natural language interaction with the AI assistant
"""

import json
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QFrame, QScrollArea, QSizePolicy, QSpacerItem,
    QLineEdit, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QTextCursor, QColor, QPalette
from loguru import logger

from core.ai_engine import AIEngine
from core.automation_engine import AutomationEngine
from core.config import Config


class ChatMessage(QFrame):
    """Individual chat message widget"""
    
    def __init__(self, text: str, is_user: bool = True, timestamp: str = None):
        super().__init__()
        self.text = text
        self.is_user = is_user
        self.timestamp = timestamp
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the message UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Create message bubble
        message_frame = QFrame()
        message_layout = QVBoxLayout(message_frame)
        message_layout.setContentsMargins(12, 8, 12, 8)
        
        # Message text
        text_label = QLabel(self.text)
        text_label.setWordWrap(True)
        text_label.setMaximumWidth(400)
        text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Timestamp
        if self.timestamp:
            time_label = QLabel(self.timestamp)
            time_label.setStyleSheet("color: #666666; font-size: 8pt;")
            message_layout.addWidget(time_label)
        
        message_layout.addWidget(text_label)
        
        # Style based on message type
        if self.is_user:
            message_frame.setStyleSheet("""
                QFrame {
                    background-color: #0078d4;
                    color: white;
                    border-radius: 12px;
                    border-top-right-radius: 4px;
                }
            """)
            layout.addStretch()
            layout.addWidget(message_frame)
        else:
            message_frame.setStyleSheet("""
                QFrame {
                    background-color: #f0f0f0;
                    color: black;
                    border-radius: 12px;
                    border-top-left-radius: 4px;
                }
            """)
            layout.addWidget(message_frame)
            layout.addStretch()


class ChatWidget(QWidget):
    """Main chat interface widget"""
    
    message_sent = pyqtSignal(str)
    workflow_requested = pyqtSignal(str)
    
    def __init__(self, ai_engine: AIEngine, automation_engine: AutomationEngine):
        super().__init__()
        self.ai_engine = ai_engine
        self.automation_engine = automation_engine
        self.messages: List[ChatMessage] = []
        
        self.setup_ui()
        self.setup_connections()
        
        # Add welcome message
        self.add_assistant_message(
            "Hello! I'm your Windows AI Assistant. I can help you automate tasks, "
            "control applications, and answer questions. Just type your request in natural language!"
        )
    
    def setup_ui(self):
        """Setup the chat interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("Chat with AI Assistant")
        header.setStyleSheet("font-size: 16pt; font-weight: bold; color: #333333;")
        layout.addWidget(header)
        
        # Messages area
        self.setup_messages_area(layout)
        
        # Input area
        self.setup_input_area(layout)
        
        # Control buttons
        self.setup_control_buttons(layout)
    
    def setup_messages_area(self, parent_layout: QVBoxLayout):
        """Setup the messages display area"""
        # Create scroll area for messages
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        # Create widget to hold messages
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(16, 16, 16, 16)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch()
        
        scroll_area.setWidget(self.messages_widget)
        parent_layout.addWidget(scroll_area)
        
        self.scroll_area = scroll_area
    
    def setup_input_area(self, parent_layout: QVBoxLayout):
        """Setup the input area"""
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 12, 12, 12)
        
        # Input field
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(80)
        self.input_field.setPlaceholderText("Type your message here... (e.g., 'Open Chrome and search for Python tutorials')")
        self.input_field.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                font-size: 10pt;
            }
        """)
        input_layout.addWidget(self.input_field)
        
        # Input controls
        controls_layout = QHBoxLayout()
        
        # Mode selector
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Chat", "Automation", "Workflow"])
        self.mode_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
            }
        """)
        controls_layout.addWidget(QLabel("Mode:"))
        controls_layout.addWidget(self.mode_combo)
        
        # Background mode checkbox
        self.background_checkbox = QCheckBox("Background Mode")
        self.background_checkbox.setToolTip("Run tasks in background without taking over your screen")
        controls_layout.addWidget(self.background_checkbox)
        
        controls_layout.addStretch()
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setMinimumWidth(80)
        self.send_button.clicked.connect(self.send_message)
        controls_layout.addWidget(self.send_button)
        
        input_layout.addLayout(controls_layout)
        parent_layout.addWidget(input_frame)
    
    def setup_control_buttons(self, parent_layout: QVBoxLayout):
        """Setup control buttons"""
        buttons_layout = QHBoxLayout()
        
        # Record workflow button
        self.record_button = QPushButton("Record Workflow")
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.record_button.clicked.connect(self.start_workflow_recording)
        buttons_layout.addWidget(self.record_button)
        
        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.stop_button.clicked.connect(self.stop_current_task)
        buttons_layout.addWidget(self.stop_button)
        
        buttons_layout.addStretch()
        
        # Clear chat button
        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.clicked.connect(self.clear_chat)
        buttons_layout.addWidget(self.clear_button)
        
        parent_layout.addLayout(buttons_layout)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect AI engine signals
        self.ai_engine.response_ready.connect(self.handle_ai_response)
        self.ai_engine.error_occurred.connect(self.handle_error)
        
        # Connect automation engine signals
        self.automation_engine.task_completed.connect(self.handle_task_completion)
        self.automation_engine.error_occurred.connect(self.handle_error)
        
        # Connect input field
        self.input_field.textChanged.connect(self.on_input_changed)
    
    def send_message(self):
        """Send the current message"""
        text = self.input_field.toPlainText().strip()
        if not text:
            return
        
        # Add user message to chat
        self.add_user_message(text)
        
        # Clear input field
        self.input_field.clear()
        
        # Determine mode and process
        mode = self.mode_combo.currentText()
        background_mode = self.background_checkbox.isChecked()
        
        if mode == "Chat":
            self.process_chat_message(text)
        elif mode == "Automation":
            self.process_automation_request(text, background_mode)
        elif mode == "Workflow":
            self.process_workflow_request(text)
        
        # Emit signal
        self.message_sent.emit(text)
    
    def process_chat_message(self, text: str):
        """Process a chat message"""
        logger.info(f"Processing chat message: {text}")
        self.ai_engine.process_message(text)
    
    def process_automation_request(self, text: str, background_mode: bool):
        """Process an automation request"""
        logger.info(f"Processing automation request: {text} (background: {background_mode})")
        self.automation_engine.process_request(text, background_mode)
    
    def process_workflow_request(self, text: str):
        """Process a workflow request"""
        logger.info(f"Processing workflow request: {text}")
        self.workflow_requested.emit(text)
    
    def add_user_message(self, text: str):
        """Add a user message to the chat"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        
        message = ChatMessage(text, is_user=True, timestamp=timestamp)
        self.messages.append(message)
        
        # Insert before the stretch
        self.messages_layout.insertWidget(len(self.messages) - 1, message)
        
        # Scroll to bottom
        self.scroll_to_bottom()
    
    def add_assistant_message(self, text: str):
        """Add an assistant message to the chat"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        
        message = ChatMessage(text, is_user=False, timestamp=timestamp)
        self.messages.append(message)
        
        # Insert before the stretch
        self.messages_layout.insertWidget(len(self.messages) - 1, message)
        
        # Scroll to bottom
        self.scroll_to_bottom()
    
    def handle_ai_response(self, response: str):
        """Handle AI response"""
        self.add_assistant_message(response)
    
    def handle_task_completion(self, result: str):
        """Handle task completion"""
        self.add_assistant_message(f"Task completed: {result}")
    
    def handle_error(self, error_message: str):
        """Handle errors"""
        self.add_assistant_message(f"Error: {error_message}")
    
    def start_workflow_recording(self):
        """Start workflow recording"""
        logger.info("Starting workflow recording")
        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        # TODO: Implement workflow recording
    
    def stop_current_task(self):
        """Stop current task"""
        logger.info("Stopping current task")
        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        # TODO: Implement task stopping
    
    def clear_chat(self):
        """Clear the chat history"""
        logger.info("Clearing chat history")
        
        # Remove all message widgets
        for message in self.messages:
            message.deleteLater()
        
        self.messages.clear()
        
        # Add stretch back
        self.messages_layout.addStretch()
        
        # Add welcome message back
        self.add_assistant_message(
            "Chat cleared. How can I help you today?"
        )
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat"""
        QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
    
    def on_input_changed(self):
        """Handle input field changes"""
        text = self.input_field.toPlainText()
        self.send_button.setEnabled(bool(text.strip()))
    
    def add_workflow(self, workflow_name: str):
        """Add a workflow to the available options"""
        # TODO: Implement workflow integration
        logger.info(f"Adding workflow: {workflow_name}") 