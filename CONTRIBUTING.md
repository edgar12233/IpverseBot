# Contributing to IpverseBot

Thank you for your interest in contributing to IpverseBot! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Issues
- Use the GitHub issue tracker to report bugs
- Provide detailed information about the issue
- Include steps to reproduce the problem
- Specify your environment (OS, Python version, etc.)

### Suggesting Features
- Open an issue with the "enhancement" label
- Clearly describe the proposed feature
- Explain why it would be useful
- Consider backward compatibility

### Code Contributions

#### Prerequisites
- Python 3.8+
- Familiarity with aiogram framework
- Understanding of Telegram Bot API

#### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/Matrix-Community-ORG/IpverseBot.git`
3. Create a virtual environment: `python3 -m venv venv`
4. Activate it: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Copy `.env.example` to `.env` and configure

#### Making Changes
1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Add appropriate documentation
4. Test your changes thoroughly
5. Commit with clear messages
6. Push to your fork
7. Create a pull request

## 📋 Code Standards

### Python Style
- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Keep functions focused and small

### Documentation
- Update README.md if needed
- Add inline comments for complex logic
- Include docstrings for all public functions
- Update this CONTRIBUTING.md if process changes

### Commit Messages
- Use present tense: "Add feature" not "Added feature"
- Keep first line under 50 characters
- Reference issues when applicable: "Fix #123"

## 🧪 Testing

- Test all new features manually
- Ensure existing functionality isn't broken
- Test with different user scenarios
- Verify admin panel functionality

## 🌐 Internationalization

- All user-facing text should support both English and Persian
- Add translations to both language dictionaries in `config/settings.py`
- Consider cultural differences in messaging

## 🔒 Security Considerations

- Never commit sensitive data (tokens, passwords)
- Use environment variables for configuration
- Validate all user inputs
- Follow principle of least privilege

## 📞 Contact

- **English Community**: [@MatrixORG](https://t.me/MatrixORG)
- **Persian Community**: [@MatrixFa](https://t.me/MatrixFa)
- **Chat Group**: [@DD0SChat](https://t.me/DD0SChat)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to IpverseBot! 🚀
