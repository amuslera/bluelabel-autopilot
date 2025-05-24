# Configuration Management

The configuration module provides centralized management of runtime configuration values with support for environment variables, `.env` files, and fallback defaults.

## Quick Start

1. Copy the sample environment file:
```bash
cp config/.env.sample .env
```

2. Edit `.env` with your actual values:
```env
GMAIL_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
OPENAI_API_KEY=sk-your-key
```

3. Use in your code:
```python
from services.config import get_config

config = get_config()
print(config.gmail_user)
```

## Features

- **Environment Variable Priority**: System environment variables override all other sources
- **`.env` File Support**: Automatically loads from project root
- **Fallback Values**: Supports default values and custom fallback dictionaries
- **Singleton Pattern**: Single configuration instance across the application
- **Development/Production Modes**: Environment-aware configuration
- **Grouped Configurations**: Helper methods for related config values

## Configuration Values

### Gmail OAuth
- `GMAIL_CLIENT_ID`: OAuth 2.0 client ID
- `GMAIL_CLIENT_SECRET`: OAuth 2.0 client secret
- `GMAIL_USER`: Gmail account for authentication
- `GMAIL_CREDENTIALS_PATH`: Token storage path

### SMTP
- `SMTP_SERVER`: SMTP server hostname
- `SMTP_PORT`: SMTP server port
- `SMTP_USERNAME`: SMTP authentication username
- `SMTP_PASSWORD`: SMTP authentication password
- `SMTP_USE_TLS`: Enable TLS (true/false)

### Email Defaults
- `DEFAULT_SENDER_EMAIL`: Default from address
- `DEFAULT_RECIPIENT_EMAIL`: Default recipient

### LLM API Keys
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic Claude API key
- `GOOGLE_API_KEY`: Google Gemini API key

### Other
- `RESEND_API_KEY`: Resend.com API key
- `ENVIRONMENT`: development/production
- `LOG_LEVEL`: Logging level

## Usage Examples

### Basic Usage
```python
from services.config import get_config

config = get_config()
if config.is_development():
    print("Running in development mode")
```

### With Fallback Values
```python
from services.config import Config

fallback = {
    'smtp_server': 'fallback.smtp.com',
    'smtp_port': 25
}
config = Config(fallback=fallback)
```

### Integration with Services
```python
# GmailInboxWatcher automatically uses config
from services.email import GmailInboxWatcher

watcher = GmailInboxWatcher()  # Uses config automatically

# EmailOutAdapter also uses config
from services.email import EmailOutAdapter

adapter = EmailOutAdapter()  # Uses SMTP config automatically
```

### Getting Grouped Configurations
```python
config = get_config()

# Get all Gmail settings
gmail_config = config.get_gmail_config()

# Get all SMTP settings
smtp_config = config.get_smtp_config()

# Get all LLM API keys
llm_keys = config.get_llm_keys()
```

## Security Notes

- Never commit `.env` files to version control
- Use `.env.sample` as a template without sensitive values
- In production, use proper secret management systems
- The config loader logs warnings for missing required values in production