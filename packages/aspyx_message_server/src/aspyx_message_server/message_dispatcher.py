from __future__ import annotations

from abc import abstractmethod
from typing import Type, List, Optional, Dict

from aspyx.di import injectable

from .message_mapper import MessageMapper
from .message_sink_manager import MessageSinkManager
from .compiler import ParseContext, TypedFunction, ExpressionCompiler, ClassContext
from .format import JSONMapper, XMLMapper
from .message_sink import Config, MessageSink

class MessageManagerStorage:
    @abstractmethod
    def load(self, dispatcher):
        pass

@injectable()
class MessageManager:
    # constructor

    def __init__(self, storage: MessageManagerStorage, dispatcher: MessageDispatcher):
        self.storage = storage
        self.dispatcher = dispatcher

        self.storage.load(self.dispatcher)

    # public

    def reload(self):
        self.dispatcher.clear()
        self.storage.load(self.dispatcher)





@injectable()
class MessageDispatcher:
    # local class

    class Listener:
        # local

        class Forward:
            def __init__(self, type: str):
                self.type = type
                self._args = {}
                self._template = {}
                self._format = "json"

            # fluent

            def args(self, args: Config) -> "MessageDispatcher.Listener.Forward":
                self._args = args

                return self

            def format(self, format: str) -> "MessageDispatcher.Listener.Forward":
                self._format = format

                return self

            def template(self, template) -> "MessageDispatcher.Listener.Forward":
                self._template = template

                return self

        # constructor

        def __init__(self, type: Type):
            self.type = type
            self.message_filter : str = ""
            self.sinks : List[MessageDispatcher.Listener.Forward] = []

        # fluent

        def filter(self, message_filter: str) -> "MessageDispatcher.Listener":
            self.message_filter = message_filter

            return self

        def handle(self, sink: Forward) -> "MessageDispatcher.Listener":
            self.sinks.append(sink)

            return self

    class Handler:
        # constructor

        def __init__(self, dispatcher : MessageDispatcher, listener: MessageDispatcher.Listener):
            self.filter : Optional[Filter] = None
            self.mapper : List[MessageMapper] = []
            self.sinks : List[MessageSink] = []

            # parse context

            parse_context = ParseContext(
                listener.type,
                functions=dispatcher.functions
            )

            # filter

            if listener.message_filter != "":
                self.filter : Filter = Filter(listener.message_filter, context=parse_context)

            # sinks

            for sink in listener.sinks:
                self.sinks.append(
                    dispatcher.message_sink_manager.create(sink.type, sink._args)
                )

                if sink._format == "json":
                    self.mapper.append(JSONMapper(sink._template, context=parse_context))
                elif sink._format == "xml":
                    self.mapper.append(XMLMapper(sink._template, context=parse_context))

        # public

        def handle(self, message):
            # check filter

            if self.filter is not None:
                if not self.filter.accepts(message):
                    return

            # forward

            for i in range(len(self.sinks)):
                self.sinks[i].send(self.mapper[i].create(message))

    # constructor

    def __init__(self, message_sink_manager: MessageSinkManager):
        self.message_sink_manager = message_sink_manager
        self.handler : Dict[Type,MessageDispatcher.Handler] = {}
        self.functions : Dict[str,TypedFunction] = {
            "length": TypedFunction(lambda str: len(str), [str], int)
            # TODO more
        }

    # public

    def clear(self):
        self.handler.clear()

    def register_functions(self, functions =  Dict[str,TypedFunction]):
        self.functions.update(functions)

    # fluent

    def listen_to(self, listener: Listener) -> "MessageDispatcher":
        self.handler[listener.type] = MessageDispatcher.Handler(self, listener)

        return self

    # main entry

    def dispatch(self, message):
        handler = next(iter(self.handler.values())) # self.handler.items()[0]#TODO .get(type(message))
        if handler is not None:
            handler.handle(message)
        else:
            print("WHAT")

class Filter:
    def __init__(self, filter: str, context: ParseContext):
        self.compiler = ExpressionCompiler()

        self.eval = self.compiler.parse(filter, context=context)

    def accepts(self, instance) -> bool:
        return self.eval.eval(ClassContext(instance))

def message(type: Type):
    return MessageDispatcher.Listener(type)

def forward(type: str):
    return MessageDispatcher.Listener.Forward(type)
