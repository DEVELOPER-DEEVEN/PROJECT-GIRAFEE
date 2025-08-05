"""
Workflow management widget for creating and managing automation workflows
"""

import json
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QListWidgetItem, QTextEdit, QFrame, QScrollArea,
    QDialog, QLineEdit, QComboBox, QCheckBox, QSpinBox, QTimeEdit,
    QFormLayout, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QTime
from PyQt6.QtGui import QFont, QIcon
from loguru import logger

from core.config import Config


class WorkflowDialog(QDialog):
    """Dialog for creating/editing workflows"""
    
    def __init__(self, parent=None, workflow_data: Dict[str, Any] = None):
        super().__init__(parent)
        self.workflow_data = workflow_data or {}
        self.setup_ui()
        self.load_workflow_data()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Create Workflow")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Workflow name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter workflow name")
        form_layout.addRow("Name:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Describe what this workflow does")
        form_layout.addRow("Description:", self.description_edit)
        
        # Trigger type
        self.trigger_combo = QComboBox()
        self.trigger_combo.addItems(["Manual", "Scheduled", "Hotkey"])
        form_layout.addRow("Trigger:", self.trigger_combo)
        
        # Schedule settings
        self.schedule_frame = QFrame()
        self.schedule_layout = QFormLayout(self.schedule_frame)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(9, 0))
        self.schedule_layout.addRow("Time:", self.time_edit)
        
        self.days_combo = QComboBox()
        self.days_combo.addItems(["Daily", "Weekly", "Monthly"])
        self.schedule_layout.addRow("Frequency:", self.days_combo)
        
        self.schedule_frame.setVisible(False)
        form_layout.addRow(self.schedule_frame)
        
        # Hotkey settings
        self.hotkey_frame = QFrame()
        self.hotkey_layout = QFormLayout(self.hotkey_frame)
        
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("Ctrl+Shift+A")
        self.hotkey_layout.addRow("Hotkey:", self.hotkey_edit)
        
        self.hotkey_frame.setVisible(False)
        form_layout.addRow(self.hotkey_frame)
        
        # Enable background mode
        self.background_checkbox = QCheckBox("Run in background")
        self.background_checkbox.setToolTip("Run workflow without taking over the screen")
        form_layout.addRow(self.background_checkbox)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        buttons_layout.addStretch()
        
        self.save_button = QPushButton("Save Workflow")
        self.save_button.clicked.connect(self.accept)
        self.save_button.setDefault(True)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        
        # Connect signals
        self.trigger_combo.currentTextChanged.connect(self.on_trigger_changed)
    
    def on_trigger_changed(self, trigger: str):
        """Handle trigger type change"""
        self.schedule_frame.setVisible(trigger == "Scheduled")
        self.hotkey_frame.setVisible(trigger == "Hotkey")
    
    def load_workflow_data(self):
        """Load existing workflow data"""
        if self.workflow_data:
            self.name_edit.setText(self.workflow_data.get('name', ''))
            self.description_edit.setPlainText(self.workflow_data.get('description', ''))
            
            trigger = self.workflow_data.get('trigger', 'Manual')
            index = self.trigger_combo.findText(trigger)
            if index >= 0:
                self.trigger_combo.setCurrentIndex(index)
            
            self.background_checkbox.setChecked(self.workflow_data.get('background', False))
    
    def get_workflow_data(self) -> Dict[str, Any]:
        """Get workflow data from form"""
        return {
            'name': self.name_edit.text(),
            'description': self.description_edit.toPlainText(),
            'trigger': self.trigger_combo.currentText(),
            'background': self.background_checkbox.isChecked(),
            'schedule': {
                'time': self.time_edit.time().toString('HH:mm'),
                'frequency': self.days_combo.currentText()
            } if self.trigger_combo.currentText() == "Scheduled" else None,
            'hotkey': self.hotkey_edit.text() if self.trigger_combo.currentText() == "Hotkey" else None
        }


class WorkflowWidget(QWidget):
    """Workflow management widget"""
    
    workflow_created = pyqtSignal(str)
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.workflows: List[Dict[str, Any]] = []
        
        self.setup_ui()
        self.load_workflows()
    
    def setup_ui(self):
        """Setup the workflow widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header_layout = QHBoxLayout()
        
        header_label = QLabel("Workflows")
        header_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #333333;")
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        # New workflow button
        self.new_workflow_button = QPushButton("New Workflow")
        self.new_workflow_button.clicked.connect(self.create_new_workflow)
        header_layout.addWidget(self.new_workflow_button)
        
        layout.addLayout(header_layout)
        
        # Splitter for workflow list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Workflow list
        self.setup_workflow_list(splitter)
        
        # Right panel - Workflow details
        self.setup_workflow_details(splitter)
        
        # Set splitter proportions
        splitter.setSizes([200, 300])
    
    def setup_workflow_list(self, parent):
        """Setup the workflow list panel"""
        # Create frame for workflow list
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(8, 8, 8, 8)
        
        # List widget
        self.workflow_list = QListWidget()
        self.workflow_list.itemClicked.connect(self.on_workflow_selected)
        self.workflow_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        list_layout.addWidget(self.workflow_list)
        
        parent.addWidget(list_frame)
    
    def setup_workflow_details(self, parent):
        """Setup the workflow details panel"""
        # Create frame for workflow details
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(16, 16, 16, 16)
        
        # Details header
        self.details_header = QLabel("Select a workflow to view details")
        self.details_header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #333333;")
        details_layout.addWidget(self.details_header)
        
        # Details content
        self.details_content = QTextEdit()
        self.details_content.setReadOnly(True)
        self.details_content.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f9f9f9;
            }
        """)
        details_layout.addWidget(self.details_content)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_workflow)
        self.edit_button.setEnabled(False)
        actions_layout.addWidget(self.edit_button)
        
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_workflow)
        self.run_button.setEnabled(False)
        actions_layout.addWidget(self.run_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_workflow)
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        actions_layout.addWidget(self.delete_button)
        
        actions_layout.addStretch()
        
        details_layout.addLayout(actions_layout)
        
        parent.addWidget(details_frame)
    
    def load_workflows(self):
        """Load workflows from storage"""
        try:
            # TODO: Load from actual storage
            # For now, create some example workflows
            self.workflows = [
                {
                    'id': '1',
                    'name': 'Open Browser and Search',
                    'description': 'Opens Chrome and searches for the specified query',
                    'trigger': 'Manual',
                    'background': False,
                    'steps': [
                        {'action': 'open_app', 'target': 'chrome'},
                        {'action': 'web_search', 'target': '{query}'}
                    ]
                },
                {
                    'id': '2',
                    'name': 'Daily File Backup',
                    'description': 'Creates a backup of important files',
                    'trigger': 'Scheduled',
                    'background': True,
                    'schedule': {'time': '18:00', 'frequency': 'Daily'},
                    'steps': [
                        {'action': 'file_operation', 'target': 'backup_folder', 'operation': 'create'},
                        {'action': 'copy_files', 'target': 'important_files', 'destination': 'backup_folder'}
                    ]
                }
            ]
            
            self.refresh_workflow_list()
            
        except Exception as e:
            logger.error(f"Error loading workflows: {e}")
    
    def refresh_workflow_list(self):
        """Refresh the workflow list"""
        self.workflow_list.clear()
        
        for workflow in self.workflows:
            item = QListWidgetItem(workflow['name'])
            item.setData(Qt.ItemDataRole.UserRole, workflow)
            self.workflow_list.addItem(item)
    
    def create_new_workflow(self):
        """Create a new workflow"""
        dialog = WorkflowDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            workflow_data = dialog.get_workflow_data()
            
            # Add workflow
            workflow_data['id'] = str(len(self.workflows) + 1)
            workflow_data['steps'] = []
            self.workflows.append(workflow_data)
            
            # Refresh list
            self.refresh_workflow_list()
            
            # Emit signal
            self.workflow_created.emit(workflow_data['name'])
            
            logger.info(f"Created new workflow: {workflow_data['name']}")
    
    def on_workflow_selected(self, item: QListWidgetItem):
        """Handle workflow selection"""
        workflow = item.data(Qt.ItemDataRole.UserRole)
        self.show_workflow_details(workflow)
    
    def show_workflow_details(self, workflow: Dict[str, Any]):
        """Show workflow details"""
        self.details_header.setText(workflow['name'])
        
        # Build details text
        details = f"<h3>{workflow['name']}</h3>"
        details += f"<p><strong>Description:</strong> {workflow['description']}</p>"
        details += f"<p><strong>Trigger:</strong> {workflow['trigger']}</p>"
        details += f"<p><strong>Background Mode:</strong> {'Yes' if workflow.get('background') else 'No'}</p>"
        
        if workflow['trigger'] == 'Scheduled' and workflow.get('schedule'):
            schedule = workflow['schedule']
            details += f"<p><strong>Schedule:</strong> {schedule['time']} ({schedule['frequency']})</p>"
        
        if workflow['trigger'] == 'Hotkey' and workflow.get('hotkey'):
            details += f"<p><strong>Hotkey:</strong> {workflow['hotkey']}</p>"
        
        if workflow.get('steps'):
            details += "<p><strong>Steps:</strong></p><ul>"
            for step in workflow['steps']:
                details += f"<li>{step['action']} {step['target']}</li>"
            details += "</ul>"
        
        self.details_content.setHtml(details)
        
        # Enable action buttons
        self.edit_button.setEnabled(True)
        self.run_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        
        # Store current workflow
        self.current_workflow = workflow
    
    def edit_workflow(self):
        """Edit the current workflow"""
        if hasattr(self, 'current_workflow'):
            dialog = WorkflowDialog(self, self.current_workflow)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.get_workflow_data()
                
                # Update workflow
                self.current_workflow.update(updated_data)
                
                # Refresh list and details
                self.refresh_workflow_list()
                self.show_workflow_details(self.current_workflow)
                
                logger.info(f"Updated workflow: {self.current_workflow['name']}")
    
    def run_workflow(self):
        """Run the current workflow"""
        if hasattr(self, 'current_workflow'):
            logger.info(f"Running workflow: {self.current_workflow['name']}")
            # TODO: Implement workflow execution
            QMessageBox.information(self, "Workflow", f"Running workflow: {self.current_workflow['name']}")
    
    def delete_workflow(self):
        """Delete the current workflow"""
        if hasattr(self, 'current_workflow'):
            reply = QMessageBox.question(
                self, 
                "Delete Workflow", 
                f"Are you sure you want to delete '{self.current_workflow['name']}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Remove workflow
                self.workflows = [w for w in self.workflows if w['id'] != self.current_workflow['id']]
                
                # Refresh list
                self.refresh_workflow_list()
                
                # Clear details
                self.details_header.setText("Select a workflow to view details")
                self.details_content.clear()
                
                # Disable action buttons
                self.edit_button.setEnabled(False)
                self.run_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                
                # Clear current workflow
                if hasattr(self, 'current_workflow'):
                    delattr(self, 'current_workflow')
                
                logger.info(f"Deleted workflow: {self.current_workflow['name']}") 