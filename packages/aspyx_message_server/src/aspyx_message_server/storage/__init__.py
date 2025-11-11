"""
This module provides the core Aspyx service management framework allowing for service discovery and transparent remoting including multiple possible transport protocols.
"""

from .persistent_message_storage import PersistentMessageManagerStorage

__all__ = [
    # persistent_message_storage

    "PersistentMessageManagerStorage"
]
