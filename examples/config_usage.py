#!/usr/bin/env python3
"""
Example demonstrating the usage of the configuration loader.

This script shows how to use the Config class with different scenarios:
1. Using environment variables
2. Using fallback values
3. Integration with email services
"""

import asyncio
from services.config import Config, get_config
from services.email import GmailInboxWatcher, EmailOutAdapter


def example_basic_usage():
    """Basic usage of the configuration loader."""
    print("=== Basic Configuration Usage ===")
    
    # Get singleton config instance
    config = get_config()
    
    print(f"Environment: {config.environment}")
    print(f"Is Development: {config.is_development()}")
    print(f"Gmail User: {config.gmail_user or 'Not Set'}")
    print(f"SMTP Server: {config.smtp_server}")
    print()


def example_with_fallback():
    """Using configuration with fallback values."""
    print("=== Configuration with Fallback ===")
    
    # Create config with fallback values
    fallback = {
        'gmail_user': 'fallback@example.com',
        'smtp_server': 'fallback.smtp.com'
    }
    
    config = Config(fallback=fallback)
    print(f"Gmail User: {config.gmail_user}")
    print(f"SMTP Server: {config.smtp_server}")
    print()


def example_gmail_integration():
    """Integration with Gmail watcher."""
    print("=== Gmail Integration ===")
    
    # GmailInboxWatcher automatically uses config
    watcher = GmailInboxWatcher()
    print(f"Token file: {watcher.token_file}")
    print(f"Credentials file: {watcher.credentials_file}")
    print()


async def example_email_output():
    """Integration with email output adapter."""
    print("=== Email Output Integration ===")
    
    # EmailOutAdapter automatically uses config when no config provided
    adapter = EmailOutAdapter()
    print(f"SMTP Server: {adapter.smtp_server}:{adapter.smtp_port}")
    print(f"From Email: {adapter.from_email}")
    print()


def example_config_methods():
    """Demonstrate config helper methods."""
    print("=== Config Helper Methods ===")
    
    config = get_config()
    
    # Get grouped configurations
    gmail_config = config.get_gmail_config()
    print(f"Gmail Config: {gmail_config}")
    
    smtp_config = config.get_smtp_config()
    print(f"SMTP Config: {smtp_config}")
    
    llm_keys = config.get_llm_keys()
    print(f"LLM Keys Available: {[k for k, v in llm_keys.items() if v]}")
    print()


if __name__ == "__main__":
    print("Configuration Loader Examples\n")
    
    # Run examples
    example_basic_usage()
    example_with_fallback()
    example_gmail_integration()
    asyncio.run(example_email_output())
    example_config_methods()
    
    print("\nTo set environment variables:")
    print("1. Copy config/.env.sample to .env")
    print("2. Fill in your actual values")
    print("3. Run this script again to see the loaded values")