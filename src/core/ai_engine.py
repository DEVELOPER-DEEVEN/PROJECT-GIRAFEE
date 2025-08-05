"""
AI Engine for natural language processing and task understanding
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from loguru import logger

import openai
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

# Import Google Generative AI for Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not available. Install with: pip install google-generativeai")


@dataclass
class TaskIntent:
    """Represents a parsed task intent"""
    action: str
    target: str
    parameters: Dict[str, Any]
    confidence: float
    task_type: str  # 'automation', 'information', 'workflow'


class AIEngine(QObject):
    """AI Engine for processing natural language commands"""
    
    # Signals
    response_ready = pyqtSignal(str)
    status_updated = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.ai_config = config.get_ai_config()
        
        # Initialize AI components
        self.setup_ai_models()
        self.setup_intent_classifier()
        
        # Task templates
        self.task_templates = self.load_task_templates()
        
        logger.info("AI Engine initialized")
    
    def setup_ai_models(self):
        """Setup AI models for different tasks"""
        try:
            # Setup OpenAI client if API key is available
            if self.ai_config.api_key:
                openai.api_key = self.ai_config.api_key
                self.use_openai = True
                logger.info("OpenAI API configured")
            else:
                self.use_openai = False
                logger.warning("No OpenAI API key configured")
            
            # Setup Gemini API if available and configured
            if GEMINI_AVAILABLE and self.ai_config.gemini_api_key:
                genai.configure(api_key=self.ai_config.gemini_api_key)
                self.use_gemini = True
                self.gemini_model = genai.GenerativeModel(self.ai_config.gemini_model)
                logger.info("Gemini API configured")
            else:
                self.use_gemini = False
                if not GEMINI_AVAILABLE:
                    logger.warning("Google Generative AI not available. Install with: pip install google-generativeai")
                elif not self.ai_config.gemini_api_key:
                    logger.warning("No Gemini API key configured")
            
            # Setup local models for fallback
            self.setup_local_models()
            
        except Exception as e:
            logger.error(f"Error setting up AI models: {e}")
            self.use_openai = False
            self.use_gemini = False
    
    def setup_local_models(self):
        """Setup local AI models"""
        try:
            # Intent classification model
            self.intent_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                return_all_scores=True
            )
            
            # Text generation model for responses
            self.text_generator = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium",
                max_length=100
            )
            
            logger.info("Local AI models loaded")
            
        except Exception as e:
            logger.error(f"Error loading local models: {e}")
    
    def setup_intent_classifier(self):
        """Setup intent classification"""
        self.intents = {
            'automation': [
                'open', 'close', 'click', 'type', 'navigate', 'search',
                'start', 'stop', 'launch', 'switch', 'minimize', 'maximize'
            ],
            'information': [
                'what', 'how', 'why', 'when', 'where', 'explain', 'tell',
                'show', 'find', 'search', 'lookup'
            ],
            'workflow': [
                'record', 'save', 'create', 'edit', 'run', 'execute',
                'schedule', 'automate', 'workflow'
            ]
        }
    
    def load_task_templates(self) -> Dict[str, Any]:
        """Load task templates for common operations"""
        return {
            'open_application': {
                'patterns': [
                    r'open\s+(\w+)',
                    r'launch\s+(\w+)',
                    r'start\s+(\w+)'
                ],
                'action': 'open_app',
                'parameters': ['app_name']
            },
            'web_search': {
                'patterns': [
                    r'search\s+(?:for\s+)?(.+)',
                    r'google\s+(.+)',
                    r'find\s+(.+)'
                ],
                'action': 'web_search',
                'parameters': ['query']
            },
            'file_operation': {
                'patterns': [
                    r'(?:open|create|save|delete)\s+(?:file|folder)\s+(.+)',
                    r'(?:open|create|save|delete)\s+(.+)'
                ],
                'action': 'file_operation',
                'parameters': ['file_path', 'operation']
            },
            'system_control': {
                'patterns': [
                    r'(?:shutdown|restart|sleep|wake)\s+(?:computer|pc)',
                    r'(?:volume|brightness|wifi|bluetooth)\s+(?:up|down|on|off)'
                ],
                'action': 'system_control',
                'parameters': ['control_type', 'value']
            }
        }
    
    def process_message(self, message: str):
        """Process a natural language message"""
        try:
            logger.info(f"Processing message: {message}")
            self.status_updated.emit("Processing message...")
            
            # Parse intent
            intent = self.parse_intent(message)
            
            # Generate response based on intent
            if intent.task_type == 'automation':
                response = self.handle_automation_intent(message, intent)
            elif intent.task_type == 'information':
                response = self.handle_information_intent(message, intent)
            elif intent.task_type == 'workflow':
                response = self.handle_workflow_intent(message, intent)
            else:
                response = self.generate_chat_response(message)
            
            # Emit response
            self.response_ready.emit(response)
            self.status_updated.emit("Response ready")
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def parse_intent(self, message: str) -> TaskIntent:
        """Parse the intent from a message"""
        message_lower = message.lower()
        
        # Check for automation keywords
        automation_score = sum(1 for word in self.intents['automation'] 
                             if word in message_lower)
        
        # Check for information keywords
        info_score = sum(1 for word in self.intents['information'] 
                        if word in message_lower)
        
        # Check for workflow keywords
        workflow_score = sum(1 for word in self.intents['workflow'] 
                           if word in message_lower)
        
        # Determine task type
        scores = {
            'automation': automation_score,
            'information': info_score,
            'workflow': workflow_score
        }
        
        task_type = max(scores, key=scores.get)
        confidence = scores[task_type] / max(len(message.split()), 1)
        
        # Extract action and target
        action, target, parameters = self.extract_action_target(message)
        
        return TaskIntent(
            action=action,
            target=target,
            parameters=parameters,
            confidence=confidence,
            task_type=task_type
        )
    
    def extract_action_target(self, message: str) -> tuple:
        """Extract action, target, and parameters from message"""
        message_lower = message.lower()
        
        # Check task templates
        for template_name, template in self.task_templates.items():
            for pattern in template['patterns']:
                match = re.search(pattern, message_lower)
                if match:
                    action = template['action']
                    target = match.group(1) if match.groups() else ""
                    parameters = self.extract_parameters(message, template)
                    return action, target, parameters
        
        # Default extraction
        words = message_lower.split()
        if len(words) >= 2:
            action = words[0]
            target = " ".join(words[1:])
        else:
            action = "unknown"
            target = message
        
        return action, target, {}
    
    def extract_parameters(self, message: str, template: Dict) -> Dict[str, Any]:
        """Extract parameters from message based on template"""
        parameters = {}
        
        # Extract common parameters
        if 'app_name' in template.get('parameters', []):
            app_match = re.search(r'(?:open|launch|start)\s+(\w+)', message.lower())
            if app_match:
                parameters['app_name'] = app_match.group(1)
        
        if 'query' in template.get('parameters', []):
            query_match = re.search(r'(?:search|google|find)\s+(?:for\s+)?(.+)', message.lower())
            if query_match:
                parameters['query'] = query_match.group(1)
        
        if 'file_path' in template.get('parameters', []):
            file_match = re.search(r'(?:file|folder)\s+(.+)', message.lower())
            if file_match:
                parameters['file_path'] = file_match.group(1)
        
        return parameters
    
    def handle_automation_intent(self, message: str, intent: TaskIntent) -> str:
        """Handle automation intent"""
        if intent.confidence > 0.3:
            return f"I'll help you with that automation task: {intent.action} {intent.target}. " \
                   f"Processing this request through the automation engine..."
        else:
            return "I'm not sure what automation you'd like me to perform. " \
                   "Could you be more specific about what you want me to do?"
    
    def handle_information_intent(self, message: str, intent: TaskIntent) -> str:
        """Handle information intent"""
        return self.generate_chat_response(message)
    
    def handle_workflow_intent(self, message: str, intent: TaskIntent) -> str:
        """Handle workflow intent"""
        return f"I'll help you with workflow management: {intent.action} {intent.target}. " \
               f"Processing this through the workflow system..."
    
    def generate_chat_response(self, message: str) -> str:
        """Generate a chat response using AI"""
        try:
            # Try Gemini first if configured
            if self.use_gemini and self.ai_config.gemini_api_key:
                return self.generate_gemini_response(message)
            # Try OpenAI if configured
            elif self.use_openai and self.ai_config.api_key:
                return self.generate_openai_response(message)
            else:
                return self.generate_local_response(message)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm having trouble processing your request right now. Please try again."
    
    def generate_gemini_response(self, message: str) -> str:
        """Generate response using Gemini API"""
        try:
            prompt = f"""You are a helpful Windows AI assistant. Provide concise, helpful responses about Windows automation, computer tasks, and general computing questions.

User: {message}

Assistant:"""
            
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self.generate_local_response(message)
    
    def generate_openai_response(self, message: str) -> str:
        """Generate response using OpenAI API"""
        try:
            response = openai.ChatCompletion.create(
                model=self.ai_config.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful Windows AI assistant. "
                                                "Provide concise, helpful responses about Windows automation, "
                                                "computer tasks, and general computing questions."},
                    {"role": "user", "content": message}
                ],
                max_tokens=self.ai_config.max_tokens,
                temperature=self.ai_config.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self.generate_local_response(message)
    
    def generate_local_response(self, message: str) -> str:
        """Generate response using local models"""
        try:
            # Simple response generation based on keywords
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['hello', 'hi', 'hey']):
                return "Hello! I'm your Windows AI Assistant. How can I help you today?"
            
            elif any(word in message_lower for word in ['help', 'what can you do']):
                return "I can help you with:\n" \
                       "• Opening applications and files\n" \
                       "• Web searches and browsing\n" \
                       "• File and folder operations\n" \
                       "• System controls (volume, brightness, etc.)\n" \
                       "• Creating and running workflows\n" \
                       "• Answering questions about Windows\n" \
                       "Just tell me what you'd like to do!"
            
            elif any(word in message_lower for word in ['open', 'launch', 'start']):
                return "I can help you open applications and files. Just tell me what you'd like to open!"
            
            elif any(word in message_lower for word in ['search', 'find', 'google']):
                return "I can help you search the web or find files on your computer. What are you looking for?"
            
            else:
                return "I understand you're asking about that. Let me help you with that task or question!"
                
        except Exception as e:
            logger.error(f"Local response generation error: {e}")
            return "I'm here to help! What would you like me to do?"
    
    def stop(self):
        """Stop the AI engine"""
        logger.info("Stopping AI engine")
        # Cleanup resources if needed 