"""
This module provides the core Aspyx service management framework allowing for service discovery and transparent remoting including multiple possible transport protocols.
"""
from .interface_dto import InterfaceHandlerDTO, OnEventDTO

__all__ = [
    # console_sink

    "InterfaceHandlerDTO",
    "OnEventDTO"
]
