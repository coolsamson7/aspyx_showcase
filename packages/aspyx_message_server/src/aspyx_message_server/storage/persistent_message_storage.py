import json
from typing import List, Optional

from aspyx.di import injectable, inject_environment, Environment
from aspyx_message_server.entity import InterfaceHandlerEntity
from aspyx_message_server.message_dispatcher import MessageManagerStorage, MessageDispatcher
from aspyx_message_server.persistence import transactional
from aspyx_message_server.service.impl import OnEventRepository
from packages.aspyx_message_server.tests.model import Turnaround # TODO WTF


@injectable() # TODO for now
class PersistentMessageManagerStorage(MessageManagerStorage):
    # constructor

    def __init__(self, repository: OnEventRepository):
        self.repository = repository
        self.environment : Optional[Environment] = None

    # lifecycle

    @inject_environment()
    def init_environment(self, environment: Environment):
        self.environment = environment

    # internal

    def find_event_class(self, event: str):
        return Turnaround # TODO

    # implement

    @transactional()
    def load(self, dispatcher):
        on_events = self.repository.find_all()

        for on_event in on_events:
            listener = MessageDispatcher.Listener(self.find_event_class(on_event.event))

            listener.filter(on_event.filter)

            # attach handlers

            handlers : List[InterfaceHandlerEntity] = on_event.handlers

            for handler in handlers:
                sink = MessageDispatcher.Listener.Forward(handler.sink)

                sink.args( json.loads(handler.args))
                sink.format(handler.format)
                sink.template(json.loads(handler.template))

                listener.handle(sink)

            # done

            dispatcher.listener = dispatcher.listen_to(listener)
