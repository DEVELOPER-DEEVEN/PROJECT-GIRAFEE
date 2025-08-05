# Windows AI Assistant - Setup Guide

This guide will help you set up and run the Windows AI Assistant on your Windows machine.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10 or later
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Display**: 1024x768 minimum resolution

### Required Software
1. **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/)
2. **Git**: Download from [git-scm.com](https://git-scm.com/download/win)

## Installation Methods

### Method 1: Automatic Installation (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd windows-ai-assistant
   ```

2. **Run the installation script**:
   ```bash
   python install.py
   ```

3. **Start the application**:
   ```bash
   run_assistant.bat
   ```

### Method 2: Manual Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd windows-ai-assistant
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python src/main.py
   ```

## Configuration

### Initial Setup

1. **Launch the application** for the first time
2. **Configure AI Settings**:
   - Go to Settings → AI Settings
   - Enter your OpenAI API key (optional)
   - Choose your preferred AI model
   - Adjust temperature and max tokens as needed

3. **Configure Automation Settings**:
   - Go to Settings → Automation Settings
   - Adjust timing delays for your system
   - Configure screenshot quality settings

4. **Test Basic Functionality**:
   - Try: "Open notepad"
   - Try: "Search for Python tutorials"
   - Try: "What can you do?"

### API Key Setup (Optional)

For enhanced AI capabilities, you can configure an OpenAI API key:

1. **Get an API key** from [OpenAI](https://platform.openai.com/api-keys)
2. **Enter the key** in Settings → AI Settings
3. **Test the connection** using the "Test" button

## Usage Guide

### Basic Commands

#### Application Control
```
"Open Chrome"
"Launch notepad"
"Start calculator"
"Open file explorer"
```

#### Web Search
```
"Search for Python tutorials"
"Google Windows automation"
"Find information about AI"
```

#### File Operations
```
"Open the Downloads folder"
"Create a new text file"
"Save this document"
```

#### System Controls
```
"Turn up the volume"
"Lower the brightness"
"Enable WiFi"
```

### Advanced Features

#### Workflow Creation
1. **Click "Record Workflow"** in the chat interface
2. **Perform your task** while narrating your actions
3. **Click "Stop"** when finished
4. **Review and save** the workflow

#### Scheduled Tasks
1. **Go to Workflows tab**
2. **Create a new workflow**
3. **Set trigger to "Scheduled"**
4. **Configure time and frequency**
5. **Save the workflow**

#### Background Mode
- **Enable "Background Mode"** before sending commands
- Tasks will run without taking over your screen
- Perfect for long-running operations

## Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### PyQt6 installation issues
```bash
# Install PyQt6 separately
pip install PyQt6==6.6.1
```

#### Permission errors
- Run as Administrator
- Check Windows Defender settings
- Ensure Python has necessary permissions

#### Application won't start
```bash
# Check Python version
python --version

# Verify virtual environment
venv\Scripts\activate

# Check dependencies
pip list
```

### Performance Issues

#### Slow response times
1. **Reduce AI model complexity** in settings
2. **Use local models** instead of API calls
3. **Adjust automation delays** in settings

#### High memory usage
1. **Close unnecessary applications**
2. **Restart the assistant**
3. **Check for memory leaks** in task manager

### Debug Mode

Enable debug logging:
```python
# In src/utils/logger.py, change level to "DEBUG"
logger.add(sys.stdout, level="DEBUG")
```

## Development

### Project Structure
```
windows-ai-assistant/
├── src/
│   ├── core/           # Core AI and automation engines
│   ├── ui/             # User interface components
│   ├── automation/     # Windows automation layer
│   ├── vision/         # Screen capture and analysis
│   ├── nlp/            # Natural language processing
│   ├── workflows/      # Workflow management
│   ├── scheduler/      # Task scheduling
│   └── utils/          # Utility functions
├── requirements.txt    # Python dependencies
├── install.py         # Installation script
├── demo.py            # Demo application
└── README.md          # Project documentation
```

### Adding New Features

1. **Create feature branch**:
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement changes** in appropriate modules

3. **Test thoroughly**:
   ```bash
   python demo.py
   ```

4. **Submit pull request**

### Contributing

1. **Fork the repository**
2. **Create feature branch**
3. **Make changes**
4. **Add tests** (if applicable)
5. **Submit pull request**

## Support

### Getting Help

- **Check the logs**: `~/.windows_ai_assistant/logs/`
- **Review settings**: Application → Settings
- **Test basic functionality**: Try simple commands first

### Reporting Issues

When reporting issues, please include:
- Windows version
- Python version
- Error messages
- Steps to reproduce
- Log files (if available)

### Feature Requests

Submit feature requests with:
- Detailed description
- Use case examples
- Priority level
- Implementation suggestions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with PyQt6 for the user interface
- Uses OpenAI API for advanced AI capabilities
- Leverages PyAutoGUI for Windows automation
- Inspired by modern AI assistants like Vy

---

**Happy automating! 🚀** 