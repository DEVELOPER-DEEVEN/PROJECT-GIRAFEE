"""
Configuration management for the Windows AI Assistant
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class AIConfig:
    """AI model configuration"""
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 2048
    temperature: float = 0.7
    api_key: Optional[str] = None
    use_local_models: bool = False
    local_model_path: Optional[str] = None
    # Gemini API configuration
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-pro"
    use_gemini: bool = False


@dataclass
class UIConfig:
    """UI configuration"""
    window_width: int = 800
    window_height: int = 600
    theme: str = "light"
    language: str = "en"
    auto_hide: bool = True
    transparency: float = 0.9


@dataclass
class AutomationConfig:
    """Automation configuration"""
    default_delay: float = 0.1
    click_delay: float = 0.05
    type_delay: float = 0.01
    screenshot_quality: int = 90
    max_screenshot_size: int = 1920
    enable_visual_feedback: bool = True


@dataclass
class WorkflowConfig:
    """Workflow configuration"""
    max_workflows: int = 100
    auto_save: bool = True
    backup_enabled: bool = True
    max_backup_count: int = 10


class Config:
    """Main configuration class"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config_dir = Path(self.config_path).parent
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize configuration sections
        self.ai = AIConfig()
        self.ui = UIConfig()
        self.automation = AutomationConfig()
        self.workflow = WorkflowConfig()
        
        # Load configuration
        self.load()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path"""
        app_data_dir = Path.home() / ".windows_ai_assistant"
        app_data_dir.mkdir(exist_ok=True)
        return str(app_data_dir / "config.json")
    
    def load(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load AI config
                if 'ai' in data:
                    ai_data = data['ai']
                    self.ai.model_name = ai_data.get('model_name', self.ai.model_name)
                    self.ai.max_tokens = ai_data.get('max_tokens', self.ai.max_tokens)
                    self.ai.temperature = ai_data.get('temperature', self.ai.temperature)
                    self.ai.api_key = ai_data.get('api_key')
                    self.ai.use_local_models = ai_data.get('use_local_models', self.ai.use_local_models)
                    self.ai.local_model_path = ai_data.get('local_model_path')
                    # Load Gemini config
                    self.ai.gemini_api_key = ai_data.get('gemini_api_key')
                    self.ai.gemini_model = ai_data.get('gemini_model', self.ai.gemini_model)
                    self.ai.use_gemini = ai_data.get('use_gemini', self.ai.use_gemini)
                
                # Load UI config
                if 'ui' in data:
                    ui_data = data['ui']
                    self.ui.window_width = ui_data.get('window_width', self.ui.window_width)
                    self.ui.window_height = ui_data.get('window_height', self.ui.window_height)
                    self.ui.theme = ui_data.get('theme', self.ui.theme)
                    self.ui.language = ui_data.get('language', self.ui.language)
                    self.ui.auto_hide = ui_data.get('auto_hide', self.ui.auto_hide)
                    self.ui.transparency = ui_data.get('transparency', self.ui.transparency)
                
                # Load automation config
                if 'automation' in data:
                    auto_data = data['automation']
                    self.automation.default_delay = auto_data.get('default_delay', self.automation.default_delay)
                    self.automation.click_delay = auto_data.get('click_delay', self.automation.click_delay)
                    self.automation.type_delay = auto_data.get('type_delay', self.automation.type_delay)
                    self.automation.screenshot_quality = auto_data.get('screenshot_quality', self.automation.screenshot_quality)
                    self.automation.max_screenshot_size = auto_data.get('max_screenshot_size', self.automation.max_screenshot_size)
                    self.automation.enable_visual_feedback = auto_data.get('enable_visual_feedback', self.automation.enable_visual_feedback)
                
                # Load workflow config
                if 'workflow' in data:
                    workflow_data = data['workflow']
                    self.workflow.max_workflows = workflow_data.get('max_workflows', self.workflow.max_workflows)
                    self.workflow.auto_save = workflow_data.get('auto_save', self.workflow.auto_save)
                    self.workflow.backup_enabled = workflow_data.get('backup_enabled', self.workflow.backup_enabled)
                    self.workflow.max_backup_count = workflow_data.get('max_backup_count', self.workflow.max_backup_count)
                
                logger.info("Configuration loaded successfully")
            else:
                logger.info("No configuration file found, using defaults")
                self.save()
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    def save(self):
        """Save configuration to file"""
        try:
            data = {
                'ai': {
                    'model_name': self.ai.model_name,
                    'max_tokens': self.ai.max_tokens,
                    'temperature': self.ai.temperature,
                    'api_key': self.ai.api_key,
                    'use_local_models': self.ai.use_local_models,
                    'local_model_path': self.ai.local_model_path,
                    'gemini_api_key': self.ai.gemini_api_key,
                    'gemini_model': self.ai.gemini_model,
                    'use_gemini': self.ai.use_gemini
                },
                'ui': {
                    'window_width': self.ui.window_width,
                    'window_height': self.ui.window_height,
                    'theme': self.ui.theme,
                    'language': self.ui.language,
                    'auto_hide': self.ui.auto_hide,
                    'transparency': self.ui.transparency
                },
                'automation': {
                    'default_delay': self.automation.default_delay,
                    'click_delay': self.automation.click_delay,
                    'type_delay': self.automation.type_delay,
                    'screenshot_quality': self.automation.screenshot_quality,
                    'max_screenshot_size': self.automation.max_screenshot_size,
                    'enable_visual_feedback': self.automation.enable_visual_feedback
                },
                'workflow': {
                    'max_workflows': self.workflow.max_workflows,
                    'auto_save': self.workflow.auto_save,
                    'backup_enabled': self.workflow.backup_enabled,
                    'max_backup_count': self.workflow.max_backup_count
                }
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get_ai_config(self) -> AIConfig:
        """Get AI configuration"""
        return self.ai
    
    def get_ui_config(self) -> UIConfig:
        """Get UI configuration"""
        return self.ui
    
    def get_automation_config(self) -> AutomationConfig:
        """Get automation configuration"""
        return self.automation
    
    def get_workflow_config(self) -> WorkflowConfig:
        """Get workflow configuration"""
        return self.workflow 