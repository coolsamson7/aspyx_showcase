from dataclasses import dataclass

from aspyx_event import event, event_listener, EventListener

from .message_dispatcher import MessageManager


@dataclass
@event(durable=False)
class UpdateMessagesEvent:
    pass

@event_listener(UpdateMessagesEvent, per_process=True)
class UpdateMessagesEventListener(EventListener[UpdateMessagesEvent]):
    # constructor

    def __init__(self, manager: MessageManager):
        self.manager = manager

    # implement

    def on(self, event: UpdateMessagesEvent):
        self.manager.reload()