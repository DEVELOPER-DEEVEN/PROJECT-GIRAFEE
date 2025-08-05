"""
Automation Engine for Windows application control and task execution
"""

import time
import subprocess
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from loguru import logger

import pyautogui
import pywinauto
from pywinauto import Application
import psutil


@dataclass
class AutomationTask:
    """Represents an automation task"""
    action: str
    target: str
    parameters: Dict[str, Any]
    background_mode: bool = False


class AutomationEngine(QObject):
    """Automation Engine for Windows application control"""
    
    # Signals
    task_completed = pyqtSignal(str)
    status_updated = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.automation_config = config.get_automation_config()
        
        # Setup automation
        self.setup_automation()
        self.setup_app_mappings()
        
        # Current task tracking
        self.current_task: Optional[AutomationTask] = None
        self.is_running = False
        
        logger.info("Automation Engine initialized")
    
    def setup_automation(self):
        """Setup automation components"""
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = self.automation_config.default_delay
        
        # Common application paths
        self.app_paths = {
            'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe',
            'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            'notepad': r'C:\Windows\System32\notepad.exe',
            'calculator': r'C:\Windows\System32\calc.exe',
            'explorer': r'C:\Windows\explorer.exe',
            'word': r'C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE',
            'excel': r'C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE',
            'powerpoint': r'C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE',
            'outlook': r'C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE'
        }
        
        # Application aliases
        self.app_aliases = {
            'browser': 'chrome',
            'web browser': 'chrome',
            'internet': 'chrome',
            'text editor': 'notepad',
            'calc': 'calculator',
            'file manager': 'explorer',
            'files': 'explorer'
        }
    
    def setup_app_mappings(self):
        """Setup application name mappings"""
        self.app_mappings = {
            # Web browsers
            'chrome': 'chrome',
            'google chrome': 'chrome',
            'firefox': 'firefox',
            'mozilla': 'firefox',
            'edge': 'edge',
            'microsoft edge': 'edge',
            
            # Office applications
            'word': 'word',
            'microsoft word': 'word',
            'excel': 'excel',
            'microsoft excel': 'excel',
            'powerpoint': 'powerpoint',
            'microsoft powerpoint': 'powerpoint',
            'outlook': 'outlook',
            'microsoft outlook': 'outlook',
            
            # System applications
            'notepad': 'notepad',
            'calculator': 'calculator',
            'calc': 'calculator',
            'explorer': 'explorer',
            'file explorer': 'explorer',
            'files': 'explorer',
            
            # Development tools
            'visual studio': 'devenv',
            'vs code': 'code',
            'vscode': 'code',
            'visual studio code': 'code',
            'pycharm': 'pycharm64',
            'intellij': 'idea64',
            'sublime': 'sublime_text',
            
            # Media applications
            'spotify': 'spotify',
            'vlc': 'vlc',
            'media player': 'wmplayer',
            'windows media player': 'wmplayer'
        }
    
    def process_request(self, request: str, background_mode: bool = False):
        """Process an automation request"""
        try:
            logger.info(f"Processing automation request: {request}")
            self.status_updated.emit("Processing automation request...")
            
            # Parse the request
            task = self.parse_automation_request(request, background_mode)
            
            if task:
                self.current_task = task
                self.is_running = True
                
                # Execute the task
                if background_mode:
                    self.execute_background_task(task)
                else:
                    self.execute_task(task)
            else:
                self.error_occurred.emit("Could not understand the automation request")
                
        except Exception as e:
            error_msg = f"Error processing automation request: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def parse_automation_request(self, request: str, background_mode: bool) -> Optional[AutomationTask]:
        """Parse an automation request into a task"""
        request_lower = request.lower()
        
        # Check for application opening
        if any(word in request_lower for word in ['open', 'launch', 'start']):
            return self.parse_open_app_request(request, background_mode)
        
        # Check for web search
        elif any(word in request_lower for word in ['search', 'google', 'find']):
            return self.parse_web_search_request(request, background_mode)
        
        # Check for file operations
        elif any(word in request_lower for word in ['file', 'folder', 'document']):
            return self.parse_file_operation_request(request, background_mode)
        
        # Check for system controls
        elif any(word in request_lower for word in ['volume', 'brightness', 'wifi', 'bluetooth']):
            return self.parse_system_control_request(request, background_mode)
        
        # Check for clicking/typing
        elif any(word in request_lower for word in ['click', 'type', 'press']):
            return self.parse_interaction_request(request, background_mode)
        
        return None
    
    def parse_open_app_request(self, request: str, background_mode: bool) -> AutomationTask:
        """Parse an open application request"""
        request_lower = request.lower()
        
        # Extract application name
        app_name = None
        
        # Check for common patterns
        patterns = [
            r'open\s+(\w+)',
            r'launch\s+(\w+)',
            r'start\s+(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, request_lower)
            if match:
                app_name = match.group(1)
                break
        
        if not app_name:
            # Try to extract from the request
            words = request_lower.split()
            for word in words:
                if word in self.app_mappings:
                    app_name = word
                    break
        
        if app_name:
            # Map to actual application
            mapped_app = self.app_mappings.get(app_name, app_name)
            
            return AutomationTask(
                action='open_app',
                target=mapped_app,
                parameters={'app_name': app_name, 'mapped_app': mapped_app},
                background_mode=background_mode
            )
        
        return AutomationTask(
            action='open_app',
            target='unknown',
            parameters={'app_name': 'unknown'},
            background_mode=background_mode
        )
    
    def parse_web_search_request(self, request: str, background_mode: bool) -> AutomationTask:
        """Parse a web search request"""
        request_lower = request.lower()
        
        # Extract search query
        query = None
        
        patterns = [
            r'search\s+(?:for\s+)?(.+)',
            r'google\s+(.+)',
            r'find\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, request_lower)
            if match:
                query = match.group(1).strip()
                break
        
        return AutomationTask(
            action='web_search',
            target=query or 'unknown',
            parameters={'query': query},
            background_mode=background_mode
        )
    
    def parse_file_operation_request(self, request: str, background_mode: bool) -> AutomationTask:
        """Parse a file operation request"""
        request_lower = request.lower()
        
        operation = 'open'
        file_path = None
        
        # Determine operation
        if 'create' in request_lower:
            operation = 'create'
        elif 'delete' in request_lower or 'remove' in request_lower:
            operation = 'delete'
        elif 'save' in request_lower:
            operation = 'save'
        
        # Extract file path
        file_patterns = [
            r'(?:file|folder)\s+(.+)',
            r'(?:open|create|save|delete)\s+(.+)'
        ]
        
        for pattern in file_patterns:
            match = re.search(pattern, request_lower)
            if match:
                file_path = match.group(1).strip()
                break
        
        return AutomationTask(
            action='file_operation',
            target=file_path or 'unknown',
            parameters={'operation': operation, 'file_path': file_path},
            background_mode=background_mode
        )
    
    def parse_system_control_request(self, request: str, background_mode: bool) -> AutomationTask:
        """Parse a system control request"""
        request_lower = request.lower()
        
        control_type = None
        value = None
        
        # Determine control type
        if 'volume' in request_lower:
            control_type = 'volume'
        elif 'brightness' in request_lower:
            control_type = 'brightness'
        elif 'wifi' in request_lower:
            control_type = 'wifi'
        elif 'bluetooth' in request_lower:
            control_type = 'bluetooth'
        
        # Determine value
        if 'up' in request_lower or 'increase' in request_lower:
            value = 'up'
        elif 'down' in request_lower or 'decrease' in request_lower:
            value = 'down'
        elif 'on' in request_lower or 'enable' in request_lower:
            value = 'on'
        elif 'off' in request_lower or 'disable' in request_lower:
            value = 'off'
        
        return AutomationTask(
            action='system_control',
            target=control_type or 'unknown',
            parameters={'control_type': control_type, 'value': value},
            background_mode=background_mode
        )
    
    def parse_interaction_request(self, request: str, background_mode: bool) -> AutomationTask:
        """Parse an interaction request (click, type, etc.)"""
        request_lower = request.lower()
        
        action = 'click'
        target = None
        
        # Determine action
        if 'click' in request_lower:
            action = 'click'
        elif 'type' in request_lower or 'enter' in request_lower:
            action = 'type'
        elif 'press' in request_lower:
            action = 'press'
        
        # Extract target
        words = request_lower.split()
        for i, word in enumerate(words):
            if word in ['click', 'type', 'press'] and i + 1 < len(words):
                target = words[i + 1]
                break
        
        return AutomationTask(
            action=action,
            target=target or 'unknown',
            parameters={'action': action, 'target': target},
            background_mode=background_mode
        )
    
    def execute_task(self, task: AutomationTask):
        """Execute an automation task"""
        try:
            logger.info(f"Executing task: {task.action} {task.target}")
            self.status_updated.emit(f"Executing: {task.action} {task.target}")
            
            if task.action == 'open_app':
                result = self.open_application(task.target, task.parameters)
            elif task.action == 'web_search':
                result = self.perform_web_search(task.target, task.parameters)
            elif task.action == 'file_operation':
                result = self.perform_file_operation(task.target, task.parameters)
            elif task.action == 'system_control':
                result = self.perform_system_control(task.target, task.parameters)
            elif task.action in ['click', 'type', 'press']:
                result = self.perform_interaction(task.action, task.target, task.parameters)
            else:
                result = f"Unknown action: {task.action}"
            
            self.task_completed.emit(result)
            self.status_updated.emit("Task completed")
            
        except Exception as e:
            error_msg = f"Error executing task: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
        finally:
            self.is_running = False
            self.current_task = None
    
    def execute_background_task(self, task: AutomationTask):
        """Execute a task in background mode"""
        # Create a background thread for the task
        self.background_thread = BackgroundTaskThread(task, self)
        self.background_thread.task_completed.connect(self.task_completed)
        self.background_thread.error_occurred.connect(self.error_occurred)
        self.background_thread.start()
    
    def open_application(self, app_name: str, parameters: Dict[str, Any]) -> str:
        """Open an application"""
        try:
            # Get the actual application path
            app_path = self.get_app_path(app_name)
            
            if app_path and os.path.exists(app_path):
                subprocess.Popen([app_path])
                return f"Opened {app_name}"
            else:
                # Try to find the application in PATH
                try:
                    subprocess.Popen([app_name])
                    return f"Opened {app_name}"
                except FileNotFoundError:
                    return f"Could not find application: {app_name}"
                    
        except Exception as e:
            logger.error(f"Error opening application {app_name}: {e}")
            return f"Error opening {app_name}: {str(e)}"
    
    def get_app_path(self, app_name: str) -> Optional[str]:
        """Get the path for an application"""
        # Check direct mappings
        if app_name in self.app_paths:
            return self.app_paths[app_name]
        
        # Check aliases
        if app_name in self.app_aliases:
            mapped_app = self.app_aliases[app_name]
            return self.app_paths.get(mapped_app)
        
        # Check mappings
        if app_name in self.app_mappings:
            mapped_app = self.app_mappings[app_name]
            return self.app_paths.get(mapped_app)
        
        return None
    
    def perform_web_search(self, query: str, parameters: Dict[str, Any]) -> str:
        """Perform a web search"""
        try:
            # Open browser and search
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            # Try to open Chrome first
            chrome_path = self.app_paths.get('chrome')
            if chrome_path and os.path.exists(chrome_path):
                subprocess.Popen([chrome_path, search_url])
            else:
                # Try to open default browser
                import webbrowser
                webbrowser.open(search_url)
            
            return f"Searched for: {query}"
            
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            return f"Error searching for {query}: {str(e)}"
    
    def perform_file_operation(self, file_path: str, parameters: Dict[str, Any]) -> str:
        """Perform a file operation"""
        try:
            operation = parameters.get('operation', 'open')
            
            if operation == 'open':
                # Open file or folder
                if os.path.exists(file_path):
                    os.startfile(file_path)
                    return f"Opened: {file_path}"
                else:
                    return f"File not found: {file_path}"
            
            elif operation == 'create':
                # Create file or folder
                if os.path.isdir(file_path) or '.' not in os.path.basename(file_path):
                    os.makedirs(file_path, exist_ok=True)
                    return f"Created folder: {file_path}"
                else:
                    with open(file_path, 'w') as f:
                        pass
                    return f"Created file: {file_path}"
            
            elif operation == 'delete':
                # Delete file or folder
                if os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        os.rmdir(file_path)
                        return f"Deleted folder: {file_path}"
                    else:
                        os.remove(file_path)
                        return f"Deleted file: {file_path}"
                else:
                    return f"File not found: {file_path}"
            
            return f"Unknown operation: {operation}"
            
        except Exception as e:
            logger.error(f"Error performing file operation: {e}")
            return f"Error with file operation: {str(e)}"
    
    def perform_system_control(self, control_type: str, parameters: Dict[str, Any]) -> str:
        """Perform system control operations"""
        try:
            value = parameters.get('value', 'unknown')
            
            if control_type == 'volume':
                if value == 'up':
                    pyautogui.press('volumeup')
                    return "Volume increased"
                elif value == 'down':
                    pyautogui.press('volumedown')
                    return "Volume decreased"
                elif value == 'off':
                    pyautogui.press('volumemute')
                    return "Volume muted"
            
            elif control_type == 'brightness':
                # Windows brightness control
                if value == 'up':
                    pyautogui.press('f2')  # Brightness up
                    return "Brightness increased"
                elif value == 'down':
                    pyautogui.press('f1')  # Brightness down
                    return "Brightness decreased"
            
            elif control_type in ['wifi', 'bluetooth']:
                # Open settings for wifi/bluetooth
                subprocess.Popen(['ms-settings:network'])
                return f"Opened {control_type} settings"
            
            return f"Unknown control type: {control_type}"
            
        except Exception as e:
            logger.error(f"Error performing system control: {e}")
            return f"Error with system control: {str(e)}"
    
    def perform_interaction(self, action: str, target: str, parameters: Dict[str, Any]) -> str:
        """Perform mouse/keyboard interactions"""
        try:
            if action == 'click':
                # Try to find and click the target
                if target.lower() in ['ok', 'yes', 'no', 'cancel']:
                    # Common button clicks
                    pyautogui.click()
                    return f"Clicked {target}"
                else:
                    # Try to find text on screen
                    try:
                        location = pyautogui.locateOnScreen(f"{target}.png")
                        if location:
                            pyautogui.click(location)
                            return f"Clicked {target}"
                        else:
                            return f"Could not find {target} on screen"
                    except:
                        return f"Could not click {target}"
            
            elif action == 'type':
                pyautogui.typewrite(target)
                return f"Typed: {target}"
            
            elif action == 'press':
                pyautogui.press(target)
                return f"Pressed: {target}"
            
            return f"Unknown interaction: {action}"
            
        except Exception as e:
            logger.error(f"Error performing interaction: {e}")
            return f"Error with interaction: {str(e)}"
    
    def stop(self):
        """Stop the automation engine"""
        logger.info("Stopping automation engine")
        self.is_running = False
        
        if hasattr(self, 'background_thread'):
            self.background_thread.stop()


class BackgroundTaskThread(QThread):
    """Background thread for executing automation tasks"""
    
    task_completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, task: AutomationTask, engine: AutomationEngine):
        super().__init__()
        self.task = task
        self.engine = engine
        self.running = True
    
    def run(self):
        """Execute the task in background"""
        try:
            self.engine.execute_task(self.task)
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        """Stop the background thread"""
        self.running = False 