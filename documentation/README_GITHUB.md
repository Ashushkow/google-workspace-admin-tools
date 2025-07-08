# Google Workspace Admin Tools v2.0.3

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Google Admin SDK](https://img.shields.io/badge/Google%20Admin%20SDK-v1-green.svg)](https://developers.google.com/admin-sdk)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive Python application for managing Google Workspace users and groups through the Google Admin SDK Directory API. Features a modern Tkinter GUI with advanced functionality for user management, group operations, and administrative tasks.

## 🚀 Features

### Core Functionality
- **User Management**: Create, update, delete, and list Google Workspace users
- **Group Management**: Manage groups and group memberships
- **Advanced Filtering**: Filter users by organizational units, status, and custom criteria
- **Bulk Operations**: Perform operations on multiple users simultaneously
- **Real-time Updates**: Live data synchronization with Google Workspace

### Technical Features
- **Modular Architecture**: Clean separation of concerns with organized code structure
- **Async Operations**: Non-blocking operations for better performance
- **Comprehensive Logging**: Detailed logging and monitoring system
- **Security Audit**: Built-in security monitoring and audit trails
- **Error Handling**: Robust error handling and recovery mechanisms
- **Data Caching**: Intelligent caching system for improved performance
- **Configuration Management**: Flexible configuration system

### User Interface
- **Modern GUI**: Clean, intuitive Tkinter interface
- **Responsive Design**: Adaptive layout for different screen sizes
- **Theming Support**: Customizable UI themes
- **Progress Indicators**: Visual feedback for long-running operations
- **Context Menus**: Right-click operations for enhanced usability

## 📁 Project Structure

```
google-workspace-admin-tools/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── README.md              # This file
│
├── src/                   # Source code
│   ├── __init__.py
│   ├── auth.py            # Authentication module
│   ├── config.py          # Configuration management
│   │
│   ├── api/               # API modules
│   │   ├── __init__.py
│   │   ├── google_api.py  # Google API client
│   │   ├── users_api.py   # Users API wrapper
│   │   └── groups_api.py  # Groups API wrapper
│   │
│   ├── ui/                # User interface modules
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main application window
│   │   ├── user_windows.py     # User management windows
│   │   ├── additional_windows.py # Additional UI windows
│   │   ├── employee_list_window.py # Employee listing
│   │   ├── group_management.py # Group management UI
│   │   ├── ui_components.py    # UI components
│   │   ├── ui_styles.py        # UI styling
│   │   └── windows.py          # Window management
│   │
│   └── utils/             # Utility modules
│       ├── __init__.py
│       ├── simple_utils.py     # Basic utilities
│       ├── data_cache.py       # Data caching system
│       ├── logger.py           # Logging system
│       ├── error_handling.py   # Error handling
│       ├── monitoring_system.py # System monitoring
│       ├── security_manager.py # Security management
│       ├── async_operations.py # Async operations
│       └── enhanced_config.py  # Enhanced configuration
│
├── config/                # Configuration files
│   ├── credentials.json.template
│   ├── settings.json.template
│   └── app_config.json.template
│
├── docs/                  # Documentation
│   ├── CHANGELOG.md
│   ├── GIT_SETUP_GUIDE.md
│   ├── releases/
│   │   ├── RELEASE_NOTES_v2.0.3.md
│   │   └── version_2.0.3.json
│   └── [other documentation files]
│
├── tests/                 # Test files
│   ├── test_employee_window.py
│   ├── test_filters.py
│   └── test_integration.py
│
├── scripts/               # Utility scripts
│   ├── release_v2.0.3.py
│   ├── release_v2.0.3.ps1
│   └── release_v2.0.3.bat
│
└── backup/               # Backup files
    └── [backup files]
```

## 🔧 Installation

### Prerequisites
- Python 3.12 or higher
- Google Workspace Admin Account
- Google Cloud Console Project with Admin SDK enabled

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/google-workspace-admin-tools.git
   cd google-workspace-admin-tools
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Google API credentials**
   - Follow the guide in `docs/SETUP_CREDENTIALS.md`
   - Copy `config/credentials.json.template` to `config/credentials.json`
   - Add your Google Cloud Console credentials

5. **Configure application settings**
   ```bash
   cp config/settings.json.template config/settings.json
   cp config/app_config.json.template config/app_config.json
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

## 🚀 Usage

### First Launch
1. Run `python main.py`
2. Complete Google OAuth2 authentication
3. The main dashboard will appear

### User Management
- **View Users**: Browse all users with filtering options
- **Add User**: Create new Google Workspace users
- **Edit User**: Modify existing user properties
- **Delete User**: Remove users (with confirmation)
- **Bulk Operations**: Select multiple users for batch operations

### Group Management
- **View Groups**: List all groups and their members
- **Create Group**: Set up new groups with custom settings
- **Manage Members**: Add/remove members from groups
- **Group Settings**: Configure group properties and permissions

### Advanced Features
- **Organizational Units**: Manage user assignments to OUs
- **User Licenses**: View and manage license assignments
- **Audit Logs**: Review user and admin activities
- **Export Data**: Export user and group data to various formats

## 🔐 Security

This application implements several security measures:

- **OAuth2 Authentication**: Secure Google API authentication
- **Token Management**: Automatic token refresh and secure storage
- **Audit Logging**: Complete activity logging
- **Permission Checks**: Validates user permissions before operations
- **Data Encryption**: Sensitive data is encrypted at rest
- **Security Monitoring**: Real-time security event monitoring

## 📊 System Requirements

- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.12+
- **Memory**: 512MB RAM minimum, 1GB recommended
- **Storage**: 100MB free space
- **Network**: Internet connection for Google API access

## 🛠️ Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_integration.py

# Run with coverage
python -m pytest tests/ --cov=src/
```

### Code Quality
```bash
# Format code
black src/

# Check linting
flake8 src/

# Type checking
mypy src/
```

### Building Documentation
```bash
# Generate documentation
sphinx-build -b html docs/ docs/_build/
```

## 📝 Changelog

### v2.0.3 (Latest)
- **Major Refactoring**: Split monolithic main.py into modular architecture
- **New Structure**: Organized code into src/api, src/ui, src/utils directories
- **Import Fixes**: Converted all imports to relative imports
- **Enhanced Documentation**: Comprehensive documentation and setup guides
- **Improved Testing**: Added integration tests and test coverage
- **Security Enhancements**: Enhanced security monitoring and audit trails

See [CHANGELOG.md](docs/CHANGELOG.md) for complete version history.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [Setup Guide](docs/SETUP_CREDENTIALS.md)
- [Git Setup Guide](docs/GIT_SETUP_GUIDE.md)
- [Release Notes](docs/releases/RELEASE_NOTES_v2.0.3.md)

### Issues
If you encounter any problems, please check:
1. [Common Issues](docs/TROUBLESHOOTING.md)
2. [GitHub Issues](https://github.com/YOUR_USERNAME/google-workspace-admin-tools/issues)
3. [Google Admin SDK Documentation](https://developers.google.com/admin-sdk)

### Contact
- Create an issue for bugs or feature requests
- Check the documentation for setup and usage questions
- Review the changelog for recent updates

---

**⚠️ Important Notice**: This application requires Google Workspace Admin privileges and should be used responsibly. Always test in a development environment before using in production.

**📧 Google API Compliance**: This application complies with Google API Terms of Service and implements security best practices for API usage.

Built with ❤️ for Google Workspace administrators worldwide.
