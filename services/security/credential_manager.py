"""
Secure credential management for sensitive data like OAuth tokens.

This module provides encryption at rest for sensitive credentials using
the cryptography library with Fernet symmetric encryption.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import logging

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)


class CredentialManager:
    """Manages encrypted storage of sensitive credentials."""
    
    def __init__(self, key_file: Optional[str] = None):
        """
        Initialize the credential manager.
        
        Args:
            key_file: Path to store the encryption key. If not provided,
                     uses ~/.bluelabel/master.key
        """
        if key_file is None:
            key_file = os.path.join(Path.home(), ".bluelabel", "master.key")
        
        self.key_file = key_file
        self._ensure_key_directory()
        self._cipher = self._get_or_create_cipher()
    
    def _ensure_key_directory(self):
        """Ensure the directory for the key file exists."""
        key_path = Path(self.key_file)
        key_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    
    def _derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Derive an encryption key from a password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # Recommended minimum in 2024
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _get_or_create_cipher(self) -> Fernet:
        """Get existing cipher or create a new one."""
        try:
            # Try to load existing key
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                return Fernet(key)
        except Exception as e:
            logger.warning(f"Could not load existing key: {e}")
        
        # Generate new key
        key = Fernet.generate_key()
        
        # Save key with restricted permissions
        with open(self.key_file, 'wb') as f:
            f.write(key)
        
        # Set restrictive permissions (owner read/write only)
        os.chmod(self.key_file, 0o600)
        
        logger.info("Generated new encryption key")
        return Fernet(key)
    
    def store_credential(self, name: str, credential_data: Dict[str, Any]) -> None:
        """
        Store encrypted credentials.
        
        Args:
            name: Name/identifier for the credential
            credential_data: Dictionary containing the credential data
        """
        # Convert to JSON
        json_data = json.dumps(credential_data)
        
        # Encrypt
        encrypted_data = self._cipher.encrypt(json_data.encode())
        
        # Store in secure location
        cred_file = self._get_credential_path(name)
        cred_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        with open(cred_file, 'wb') as f:
            f.write(encrypted_data)
        
        # Set restrictive permissions
        os.chmod(cred_file, 0o600)
        
        logger.info(f"Stored encrypted credential: {name}")
    
    def retrieve_credential(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve and decrypt credentials.
        
        Args:
            name: Name/identifier for the credential
            
        Returns:
            Decrypted credential data or None if not found
        """
        cred_file = self._get_credential_path(name)
        
        if not cred_file.exists():
            logger.warning(f"Credential not found: {name}")
            return None
        
        try:
            with open(cred_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted_data = self._cipher.decrypt(encrypted_data)
            
            # Parse JSON
            credential_data = json.loads(decrypted_data.decode())
            
            logger.info(f"Retrieved credential: {name}")
            return credential_data
            
        except Exception as e:
            logger.error(f"Error retrieving credential {name}: {e}")
            return None
    
    def delete_credential(self, name: str) -> bool:
        """
        Delete stored credentials.
        
        Args:
            name: Name/identifier for the credential
            
        Returns:
            True if deleted, False if not found
        """
        cred_file = self._get_credential_path(name)
        
        if cred_file.exists():
            cred_file.unlink()
            logger.info(f"Deleted credential: {name}")
            return True
        
        return False
    
    def _get_credential_path(self, name: str) -> Path:
        """Get the path for a credential file."""
        base_dir = Path.home() / ".bluelabel" / "credentials"
        # Sanitize name to prevent directory traversal
        safe_name = "".join(c for c in name if c.isalnum() or c in ('_', '-'))
        return base_dir / f"{safe_name}.enc"
    
    def list_credentials(self) -> list[str]:
        """List all stored credential names."""
        base_dir = Path.home() / ".bluelabel" / "credentials"
        if not base_dir.exists():
            return []
        
        credentials = []
        for file in base_dir.glob("*.enc"):
            credentials.append(file.stem)
        
        return credentials


# Convenience functions
_default_manager = None

def get_credential_manager() -> CredentialManager:
    """Get the default credential manager instance."""
    global _default_manager
    if _default_manager is None:
        _default_manager = CredentialManager()
    return _default_manager


def store_oauth_token(service: str, token_data: Dict[str, Any]) -> None:
    """
    Store OAuth token securely.
    
    Args:
        service: Service name (e.g., 'gmail')
        token_data: OAuth token data to store
    """
    manager = get_credential_manager()
    manager.store_credential(f"oauth_{service}", token_data)


def retrieve_oauth_token(service: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve OAuth token.
    
    Args:
        service: Service name (e.g., 'gmail')
        
    Returns:
        OAuth token data or None if not found
    """
    manager = get_credential_manager()
    return manager.retrieve_credential(f"oauth_{service}")