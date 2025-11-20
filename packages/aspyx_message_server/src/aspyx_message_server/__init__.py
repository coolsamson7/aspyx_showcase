"""
This module provides the core Aspyx service management framework allowing for service discovery and transparent remoting including multiple possible transport protocols.
"""
from aspyx.di import module
from aspyx_event import EventModule

from .message_dispatcher import MessageDispatcher
from .message_sink import MessageSink
from .message_sink_manager import MessageSinkManager, message_sink
from .module import PushInterfaceModule

__all__ = [
    "PushInterfaceModule",

    # message_dispatcher

    "MessageDispatcher",

    # message_sink

    "MessageSink",

    # message_sink_manager

    "MessageSinkManager",
    "message_sink"
]


