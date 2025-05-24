"""
Central configuration manager for secure runtime values.

This module provides a unified interface for loading configuration from environment
variables with fallback to static defaults. It supports development/production
environments and handles sensitive credentials securely.

Usage:
    from services.config import Config
    
    config = Config()
    gmail_user = config.gmail_user
    
    # With custom fallback
    config = Config(fallback={'gmail_user': 'default@example.com'})
"""

import os
import logging
from typing import Dict, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """
    Central configuration manager with environment variable priority.
    
    Loads configuration from:
    1. System environment variables (highest priority)
    2. .env file (if present)
    3. Fallback dictionary (lowest priority)
    
    Attributes:
        # Gmail OAuth Configuration
        gmail_client_id: OAuth 2.0 client ID for Gmail API
        gmail_client_secret: OAuth 2.0 client secret
        gmail_user: Gmail account username for authentication
        gmail_credentials_path: Path to store OAuth tokens
        
        # SMTP Configuration
        smtp_server: SMTP server hostname
        smtp_port: SMTP server port
        smtp_username: SMTP authentication username
        smtp_password: SMTP authentication password
        smtp_use_tls: Whether to use TLS (string 'true'/'false')
        
        # Email Defaults
        default_sender_email: Default from address
        default_recipient_email: Default recipient for testing
        
        # LLM API Keys
        openai_api_key: OpenAI API key
        anthropic_api_key: Anthropic Claude API key
        google_api_key: Google Gemini API key
        
        # Resend Configuration
        resend_api_key: Resend.com API key for email delivery
        
        # Environment Settings
        environment: Current environment (development/production)
        log_level: Logging level (DEBUG/INFO/WARNING/ERROR)
        
        # Paths
        data_dir: Base directory for data storage
        workflow_dir: Directory for workflow definitions
        knowledge_dir: Directory for knowledge base
    """
    
    def __init__(self, fallback: Optional[Dict[str, Any]] = None, env_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            fallback: Dictionary of default values
            env_file: Path to .env file (defaults to project root)
        """
        self.fallback = fallback or {}
        
        # Load .env file if it exists
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to find .env in project root
            project_root = Path(__file__).parent.parent.parent
            default_env = project_root / '.env'
            if default_env.exists():
                load_dotenv(default_env)
                logger.info(f"Loaded environment from {default_env}")
        
        # Gmail OAuth Configuration
        self.gmail_client_id = self._get('GMAIL_CLIENT_ID', 'gmail_client_id')
        self.gmail_client_secret = self._get('GMAIL_CLIENT_SECRET', 'gmail_client_secret')
        self.gmail_user = self._get('GMAIL_USER', 'gmail_user')
        self.gmail_credentials_path = self._get('GMAIL_CREDENTIALS_PATH', 'gmail_credentials_path', 
                                                default='data/gmail_token.json')
        
        # SMTP Configuration
        self.smtp_server = self._get('SMTP_SERVER', 'smtp_server', default='smtp.gmail.com')
        self.smtp_port = int(self._get('SMTP_PORT', 'smtp_port', default='587'))
        self.smtp_username = self._get('SMTP_USERNAME', 'smtp_username')
        self.smtp_password = self._get('SMTP_PASSWORD', 'smtp_password')
        self.smtp_use_tls = self._get('SMTP_USE_TLS', 'smtp_use_tls', default='true').lower() == 'true'
        
        # Email Defaults
        self.default_sender_email = self._get('DEFAULT_SENDER_EMAIL', 'default_sender_email')
        self.default_recipient_email = self._get('DEFAULT_RECIPIENT_EMAIL', 'default_recipient_email')
        
        # LLM API Keys
        self.openai_api_key = self._get('OPENAI_API_KEY', 'openai_api_key')
        self.anthropic_api_key = self._get('ANTHROPIC_API_KEY', 'anthropic_api_key')
        self.google_api_key = self._get('GOOGLE_API_KEY', 'google_api_key')
        
        # Resend Configuration
        self.resend_api_key = self._get('RESEND_API_KEY', 'resend_api_key')
        
        # Environment Settings
        self.environment = self._get('ENVIRONMENT', 'environment', default='development')
        self.log_level = self._get('LOG_LEVEL', 'log_level', default='INFO')
        
        # Paths
        self.data_dir = self._get('DATA_DIR', 'data_dir', default='data')
        self.workflow_dir = self._get('WORKFLOW_DIR', 'workflow_dir', default='workflows')
        self.knowledge_dir = self._get('KNOWLEDGE_DIR', 'knowledge_dir', default='data/knowledge')
        
        # Log missing required values in production
        if self.environment == 'production':
            self._check_required_values()
    
    def _get(self, env_key: str, fallback_key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get configuration value with priority: env var > fallback dict > default.
        
        Args:
            env_key: Environment variable name
            fallback_key: Key in fallback dictionary
            default: Default value if not found
            
        Returns:
            Configuration value or None
        """
        return os.getenv(env_key, self.fallback.get(fallback_key, default))
    
    def _check_required_values(self):
        """Log warnings for missing required values in production."""
        required_prod = {
            'gmail_client_id': self.gmail_client_id,
            'gmail_client_secret': self.gmail_client_secret,
            'smtp_password': self.smtp_password,
        }
        
        missing = [key for key, value in required_prod.items() if not value]
        if missing:
            logger.warning(f"Missing required configuration for production: {missing}")
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() in ('development', 'dev')
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() in ('production', 'prod')
    
    def get_gmail_config(self) -> Dict[str, Any]:
        """Get Gmail-specific configuration as a dictionary."""
        return {
            'client_id': self.gmail_client_id,
            'client_secret': self.gmail_client_secret,
            'user': self.gmail_user,
            'credentials_path': self.gmail_credentials_path
        }
    
    def get_smtp_config(self) -> Dict[str, Any]:
        """Get SMTP-specific configuration as a dictionary."""
        return {
            'server': self.smtp_server,
            'port': self.smtp_port,
            'username': self.smtp_username,
            'password': self.smtp_password,
            'use_tls': self.smtp_use_tls
        }
    
    def get_llm_keys(self) -> Dict[str, Optional[str]]:
        """Get all LLM API keys as a dictionary."""
        return {
            'openai': self.openai_api_key,
            'anthropic': self.anthropic_api_key,
            'google': self.google_api_key
        }
    
    def __repr__(self) -> str:
        """String representation showing non-sensitive configuration."""
        return (f"Config(environment={self.environment}, "
                f"gmail_user={self.gmail_user or 'Not Set'}, "
                f"smtp_server={self.smtp_server})")


# Singleton instance for easy import
_config_instance = None

def get_config(fallback: Optional[Dict[str, Any]] = None, reload: bool = False) -> Config:
    """
    Get or create the singleton configuration instance.
    
    Args:
        fallback: Fallback configuration dictionary
        reload: Force reload of configuration
        
    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None or reload:
        _config_instance = Config(fallback=fallback)
    return _config_instance