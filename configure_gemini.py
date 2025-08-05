#!/usr/bin/env python3
"""
Script to configure Gemini API key for Windows AI Assistant
"""

import json
import os
from pathlib import Path
from loguru import logger


def configure_gemini_api_key(api_key: str):
    """Configure Gemini API key in the application"""
    
    # Get the config file path
    config_dir = Path.home() / ".windows_ai_assistant"
    config_file = config_dir / "config.json"
    
    try:
        # Create config directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing config or create new one
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {
                'ai': {
                    'model_name': 'gpt-3.5-turbo',
                    'max_tokens': 2048,
                    'temperature': 0.7,
                    'api_key': None,
                    'use_local_models': False,
                    'local_model_path': None,
                    'gemini_api_key': None,
                    'gemini_model': 'gemini-pro',
                    'use_gemini': False
                },
                'ui': {
                    'window_width': 800,
                    'window_height': 600,
                    'theme': 'light',
                    'language': 'en',
                    'auto_hide': True,
                    'transparency': 0.9
                },
                'automation': {
                    'default_delay': 0.1,
                    'click_delay': 0.05,
                    'type_delay': 0.01,
                    'screenshot_quality': 90,
                    'max_screenshot_size': 1920,
                    'enable_visual_feedback': True
                },
                'workflow': {
                    'max_workflows': 100,
                    'auto_save': True,
                    'backup_enabled': True,
                    'max_backup_count': 10
                }
            }
        
        # Update Gemini configuration
        if 'ai' not in config:
            config['ai'] = {}
        
        config['ai']['gemini_api_key'] = api_key
        config['ai']['use_gemini'] = True
        config['ai']['gemini_model'] = 'gemini-pro'
        
        # Save the configuration
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ Gemini API key configured successfully!")
        print(f"Configuration saved to: {config_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configuring Gemini API key: {e}")
        return False


def main():
    """Main function to configure Gemini API key"""
    print("🔧 Windows AI Assistant - Gemini API Configuration")
    print("=" * 50)
    
    # Your provided API key
    api_key = "AIzaSyA8XM56HBBQoVjO_XlCwOKyxeEFRMfomC8"
    
    print(f"Configuring Gemini API key: {api_key[:10]}...")
    
    if configure_gemini_api_key(api_key):
        print("\n🎉 Configuration complete!")
        print("\nYou can now run the Windows AI Assistant with Gemini support:")
        print("1. python demo.py")
        print("2. Or run: python src/main.py")
        print("\nThe application will now use Gemini for AI responses.")
    else:
        print("\n❌ Configuration failed. Please check the error message above.")


if __name__ == "__main__":
    main() 