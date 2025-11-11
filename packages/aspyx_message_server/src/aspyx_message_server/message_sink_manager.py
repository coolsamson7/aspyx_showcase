from typing import Dict, Type

from aspyx.di import Environment, Providers, ClassInstanceProvider, injectable, inject_environment
from aspyx.reflection import Decorators

from .message_sink import Config, MessageSink


@injectable()
class MessageSinkManager:
    # static

    sinks : Dict[str,Type] = {}

    @classmethod
    def register(cls, type: Type, name: str):
        MessageSinkManager.sinks[name] = type

    # constructor

    def __init__(self):
        self.environment = None

    @inject_environment()
    def init_environment(self, environment: Environment):
        self.environment = environment

    # create

    def create(self, sink: str, config: Config):
        sink : MessageSink = self.environment.get(self.sinks.get(sink))

        sink.set_config(config)

        return sink

def message_sink(name: str):
    # local func

    def decorator(cls):
        Providers.register(ClassInstanceProvider(cls, False, scope="request"))

        Decorators.add(cls, message_sink, name)
        Decorators.add(cls, injectable) # do we need that?

        MessageSinkManager.register(cls, name)

        return cls

    return decorator