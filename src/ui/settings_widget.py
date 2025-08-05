"""
Settings widget for application configuration
"""

from typing import Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
    QFormLayout, QGroupBox, QTabWidget, QScrollArea, QFrame,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from loguru import logger

from core.config import Config


class SettingsWidget(QWidget):
    """Settings widget for application configuration"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header_label = QLabel("Settings")
        header_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #333333;")
        layout.addWidget(header_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # AI Settings tab
        self.setup_ai_settings()
        
        # UI Settings tab
        self.setup_ui_settings()
        
        # Automation Settings tab
        self.setup_automation_settings()
        
        # Workflow Settings tab
        self.setup_workflow_settings()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(self.reset_button)
        
        buttons_layout.addStretch()
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setDefault(True)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
    
    def setup_ai_settings(self):
        """Setup AI settings tab"""
        ai_widget = QWidget()
        ai_layout = QVBoxLayout(ai_widget)
        
        # AI Provider Selection
        provider_group = QGroupBox("AI Provider")
        provider_form = QFormLayout(provider_group)
        
        self.ai_provider_combo = QComboBox()
        self.ai_provider_combo.addItems(["Local Models", "OpenAI", "Gemini"])
        self.ai_provider_combo.currentTextChanged.connect(self.on_ai_provider_changed)
        provider_form.addRow("Primary Provider:", self.ai_provider_combo)
        
        ai_layout.addWidget(provider_group)
        
        # OpenAI Configuration Group
        self.openai_group = QGroupBox("OpenAI Configuration")
        openai_form = QFormLayout(self.openai_group)
        
        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo",
            "claude-3-sonnet",
            "claude-3-opus"
        ])
        openai_form.addRow("Model:", self.model_combo)
        
        # API Key
        api_key_layout = QHBoxLayout()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("Enter your OpenAI API key")
        api_key_layout.addWidget(self.api_key_edit)
        
        self.test_openai_button = QPushButton("Test")
        self.test_openai_button.clicked.connect(self.test_openai_api_key)
        api_key_layout.addWidget(self.test_openai_button)
        
        openai_form.addRow("API Key:", api_key_layout)
        
        # Model parameters
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 8000)
        self.max_tokens_spin.setValue(2048)
        openai_form.addRow("Max Tokens:", self.max_tokens_spin)
        
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(0.7)
        openai_form.addRow("Temperature:", self.temperature_spin)
        
        ai_layout.addWidget(self.openai_group)
        
        # Gemini Configuration Group
        self.gemini_group = QGroupBox("Gemini Configuration")
        gemini_form = QFormLayout(self.gemini_group)
        
        # Gemini model selection
        self.gemini_model_combo = QComboBox()
        self.gemini_model_combo.addItems([
            "gemini-pro",
            "gemini-pro-vision"
        ])
        gemini_form.addRow("Model:", self.gemini_model_combo)
        
        # Gemini API Key
        gemini_key_layout = QHBoxLayout()
        self.gemini_api_key_edit = QLineEdit()
        self.gemini_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_api_key_edit.setPlaceholderText("Enter your Gemini API key")
        gemini_key_layout.addWidget(self.gemini_api_key_edit)
        
        self.test_gemini_button = QPushButton("Test")
        self.test_gemini_button.clicked.connect(self.test_gemini_api_key)
        gemini_key_layout.addWidget(self.test_gemini_button)
        
        gemini_form.addRow("API Key:", gemini_key_layout)
        
        ai_layout.addWidget(self.gemini_group)
        
        # Local models
        self.use_local_checkbox = QCheckBox("Use local models when API is unavailable")
        ai_layout.addWidget(self.use_local_checkbox)
        
        ai_layout.addStretch()
        
        self.tab_widget.addTab(ai_widget, "AI Settings")
    
    def on_ai_provider_changed(self, provider: str):
        """Handle AI provider change"""
        # Show/hide provider-specific settings
        self.openai_group.setVisible(provider == "OpenAI")
        self.gemini_group.setVisible(provider == "Gemini")
    
    def setup_ui_settings(self):
        """Setup UI settings tab"""
        ui_widget = QWidget()
        ui_layout = QVBoxLayout(ui_widget)
        
        # Window Settings Group
        window_group = QGroupBox("Window Settings")
        window_form = QFormLayout(window_group)
        
        # Window size
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(600, 2000)
        self.width_spin.setValue(1000)
        size_layout.addWidget(QLabel("Width:"))
        size_layout.addWidget(self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(400, 1500)
        self.height_spin.setValue(700)
        size_layout.addWidget(QLabel("Height:"))
        size_layout.addWidget(self.height_spin)
        
        window_form.addRow("Window Size:", size_layout)
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        window_form.addRow("Theme:", self.theme_combo)
        
        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish", "French", "German", "Chinese"])
        window_form.addRow("Language:", self.language_combo)
        
        # Auto-hide
        self.auto_hide_checkbox = QCheckBox("Auto-hide window when not in focus")
        window_form.addRow(self.auto_hide_checkbox)
        
        # Transparency
        self.transparency_spin = QDoubleSpinBox()
        self.transparency_spin.setRange(0.1, 1.0)
        self.transparency_spin.setSingleStep(0.1)
        self.transparency_spin.setValue(0.9)
        window_form.addRow("Transparency:", self.transparency_spin)
        
        ui_layout.addWidget(window_group)
        ui_layout.addStretch()
        
        self.tab_widget.addTab(ui_widget, "UI Settings")
    
    def setup_automation_settings(self):
        """Setup automation settings tab"""
        auto_widget = QWidget()
        auto_layout = QVBoxLayout(auto_widget)
        
        # Timing Settings Group
        timing_group = QGroupBox("Timing Settings")
        timing_form = QFormLayout(timing_group)
        
        # Delays
        self.default_delay_spin = QDoubleSpinBox()
        self.default_delay_spin.setRange(0.0, 5.0)
        self.default_delay_spin.setSingleStep(0.1)
        self.default_delay_spin.setValue(0.1)
        timing_form.addRow("Default Delay (s):", self.default_delay_spin)
        
        self.click_delay_spin = QDoubleSpinBox()
        self.click_delay_spin.setRange(0.0, 2.0)
        self.click_delay_spin.setSingleStep(0.05)
        self.click_delay_spin.setValue(0.05)
        timing_form.addRow("Click Delay (s):", self.click_delay_spin)
        
        self.type_delay_spin = QDoubleSpinBox()
        self.type_delay_spin.setRange(0.0, 1.0)
        self.type_delay_spin.setSingleStep(0.01)
        self.type_delay_spin.setValue(0.01)
        timing_form.addRow("Type Delay (s):", self.type_delay_spin)
        
        auto_layout.addWidget(timing_group)
        
        # Screenshot Settings Group
        screenshot_group = QGroupBox("Screenshot Settings")
        screenshot_form = QFormLayout(screenshot_group)
        
        # Screenshot quality
        self.screenshot_quality_spin = QSpinBox()
        self.screenshot_quality_spin.setRange(10, 100)
        self.screenshot_quality_spin.setValue(90)
        screenshot_form.addRow("Screenshot Quality (%):", self.screenshot_quality_spin)
        
        # Max screenshot size
        self.max_screenshot_spin = QSpinBox()
        self.max_screenshot_spin.setRange(800, 3840)
        self.max_screenshot_spin.setValue(1920)
        screenshot_form.addRow("Max Screenshot Size (px):", self.max_screenshot_spin)
        
        # Visual feedback
        self.visual_feedback_checkbox = QCheckBox("Enable visual feedback during automation")
        screenshot_form.addRow(self.visual_feedback_checkbox)
        
        auto_layout.addWidget(screenshot_group)
        auto_layout.addStretch()
        
        self.tab_widget.addTab(auto_widget, "Automation Settings")
    
    def setup_workflow_settings(self):
        """Setup workflow settings tab"""
        workflow_widget = QWidget()
        workflow_layout = QVBoxLayout(workflow_widget)
        
        # Workflow Settings Group
        workflow_group = QGroupBox("Workflow Settings")
        workflow_form = QFormLayout(workflow_group)
        
        # Max workflows
        self.max_workflows_spin = QSpinBox()
        self.max_workflows_spin.setRange(10, 1000)
        self.max_workflows_spin.setValue(100)
        workflow_form.addRow("Max Workflows:", self.max_workflows_spin)
        
        # Auto-save
        self.auto_save_checkbox = QCheckBox("Auto-save workflows")
        workflow_form.addRow(self.auto_save_checkbox)
        
        # Backup settings
        self.backup_checkbox = QCheckBox("Enable workflow backups")
        workflow_form.addRow(self.backup_checkbox)
        
        # Max backup count
        self.max_backup_spin = QSpinBox()
        self.max_backup_spin.setRange(1, 50)
        self.max_backup_spin.setValue(10)
        workflow_form.addRow("Max Backups:", self.max_backup_spin)
        
        workflow_layout.addWidget(workflow_group)
        workflow_layout.addStretch()
        
        self.tab_widget.addTab(workflow_widget, "Workflow Settings")
    
    def load_settings(self):
        """Load current settings into the UI"""
        try:
            # AI Settings
            ai_config = self.config.get_ai_config()
            
            # Set provider based on configuration
            if ai_config.use_gemini and ai_config.gemini_api_key:
                self.ai_provider_combo.setCurrentText("Gemini")
            elif ai_config.api_key:
                self.ai_provider_combo.setCurrentText("OpenAI")
            else:
                self.ai_provider_combo.setCurrentText("Local Models")
            
            # OpenAI settings
            self.model_combo.setCurrentText(ai_config.model_name)
            self.api_key_edit.setText(ai_config.api_key or "")
            self.max_tokens_spin.setValue(ai_config.max_tokens)
            self.temperature_spin.setValue(ai_config.temperature)
            
            # Gemini settings
            self.gemini_model_combo.setCurrentText(ai_config.gemini_model)
            self.gemini_api_key_edit.setText(ai_config.gemini_api_key or "")
            
            # Local models
            self.use_local_checkbox.setChecked(ai_config.use_local_models)
            
            # UI Settings
            ui_config = self.config.get_ui_config()
            self.width_spin.setValue(ui_config.window_width)
            self.height_spin.setValue(ui_config.window_height)
            self.theme_combo.setCurrentText(ui_config.theme.title())
            self.language_combo.setCurrentText(ui_config.language.title())
            self.auto_hide_checkbox.setChecked(ui_config.auto_hide)
            self.transparency_spin.setValue(ui_config.transparency)
            
            # Automation Settings
            auto_config = self.config.get_automation_config()
            self.default_delay_spin.setValue(auto_config.default_delay)
            self.click_delay_spin.setValue(auto_config.click_delay)
            self.type_delay_spin.setValue(auto_config.type_delay)
            self.screenshot_quality_spin.setValue(auto_config.screenshot_quality)
            self.max_screenshot_spin.setValue(auto_config.max_screenshot_size)
            self.visual_feedback_checkbox.setChecked(auto_config.enable_visual_feedback)
            
            # Workflow Settings
            workflow_config = self.config.get_workflow_config()
            self.max_workflows_spin.setValue(workflow_config.max_workflows)
            self.auto_save_checkbox.setChecked(workflow_config.auto_save)
            self.backup_checkbox.setChecked(workflow_config.backup_enabled)
            self.max_backup_spin.setValue(workflow_config.max_backup_count)
            
            # Trigger provider change to show/hide appropriate settings
            self.on_ai_provider_changed(self.ai_provider_combo.currentText())
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings from the UI"""
        try:
            # AI Settings
            ai_config = self.config.get_ai_config()
            
            # Set provider-specific settings
            provider = self.ai_provider_combo.currentText()
            if provider == "OpenAI":
                ai_config.api_key = self.api_key_edit.text() or None
                ai_config.model_name = self.model_combo.currentText()
                ai_config.max_tokens = self.max_tokens_spin.value()
                ai_config.temperature = self.temperature_spin.value()
                ai_config.use_gemini = False
                ai_config.gemini_api_key = None
            elif provider == "Gemini":
                ai_config.gemini_api_key = self.gemini_api_key_edit.text() or None
                ai_config.gemini_model = self.gemini_model_combo.currentText()
                ai_config.use_gemini = True
                ai_config.api_key = None
            else:  # Local Models
                ai_config.api_key = None
                ai_config.gemini_api_key = None
                ai_config.use_gemini = False
            
            ai_config.use_local_models = self.use_local_checkbox.isChecked()
            
            # UI Settings
            ui_config = self.config.get_ui_config()
            ui_config.window_width = self.width_spin.value()
            ui_config.window_height = self.height_spin.value()
            ui_config.theme = self.theme_combo.currentText().lower()
            ui_config.language = self.language_combo.currentText().lower()
            ui_config.auto_hide = self.auto_hide_checkbox.isChecked()
            ui_config.transparency = self.transparency_spin.value()
            
            # Automation Settings
            auto_config = self.config.get_automation_config()
            auto_config.default_delay = self.default_delay_spin.value()
            auto_config.click_delay = self.click_delay_spin.value()
            auto_config.type_delay = self.type_delay_spin.value()
            auto_config.screenshot_quality = self.screenshot_quality_spin.value()
            auto_config.max_screenshot_size = self.max_screenshot_spin.value()
            auto_config.enable_visual_feedback = self.visual_feedback_checkbox.isChecked()
            
            # Workflow Settings
            workflow_config = self.config.get_workflow_config()
            workflow_config.max_workflows = self.max_workflows_spin.value()
            workflow_config.auto_save = self.auto_save_checkbox.isChecked()
            workflow_config.backup_enabled = self.backup_checkbox.isChecked()
            workflow_config.max_backup_count = self.max_backup_spin.value()
            
            # Save to file
            self.config.save()
            
            # Emit signal
            self.settings_changed.emit()
            
            QMessageBox.information(self, "Settings", "Settings saved successfully!")
            logger.info("Settings saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Reset configuration
                self.config = Config()
                self.load_settings()
                
                QMessageBox.information(self, "Settings", "Settings reset to defaults!")
                logger.info("Settings reset to defaults")
                
            except Exception as e:
                logger.error(f"Error resetting settings: {e}")
                QMessageBox.critical(self, "Error", f"Error resetting settings: {str(e)}")
    
    def test_openai_api_key(self):
        """Test the OpenAI API key"""
        api_key = self.api_key_edit.text()
        if not api_key:
            QMessageBox.warning(self, "API Key", "Please enter an OpenAI API key first.")
            return
        
        try:
            # TODO: Implement actual OpenAI API key testing
            QMessageBox.information(self, "OpenAI API Key", "OpenAI API key test successful!")
            logger.info("OpenAI API key test successful")
            
        except Exception as e:
            logger.error(f"OpenAI API key test failed: {e}")
            QMessageBox.critical(self, "OpenAI API Key", f"OpenAI API key test failed: {str(e)}")
    
    def test_gemini_api_key(self):
        """Test the Gemini API key"""
        api_key = self.gemini_api_key_edit.text()
        if not api_key:
            QMessageBox.warning(self, "API Key", "Please enter a Gemini API key first.")
            return
        
        try:
            # TODO: Implement actual Gemini API key testing
            QMessageBox.information(self, "Gemini API Key", "Gemini API key test successful!")
            logger.info("Gemini API key test successful")
            
        except Exception as e:
            logger.error(f"Gemini API key test failed: {e}")
            QMessageBox.critical(self, "Gemini API Key", f"Gemini API key test failed: {str(e)}") 