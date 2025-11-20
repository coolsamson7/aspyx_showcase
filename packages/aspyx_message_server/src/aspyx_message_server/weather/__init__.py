"""
This module provides the core Aspyx service management framework allowing for service discovery and transparent remoting including multiple possible transport protocols.
"""

from .weather_manager import WeatherManager

__all__ = [
    # weather_manager

    "WeatherManager",
]


