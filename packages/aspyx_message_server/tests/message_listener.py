from aspyx_event import EventListener, event_listener
from packages.aspyx_message_server.tests.messages import TurnaroundEvent


@event_listener(TurnaroundEvent, per_process=True)
class AsyncListener(EventListener[TurnaroundEvent]):
    # constructor

    def __init__(self):
        pass

    # implement

    async def on(self, event: TurnaroundEvent):
        print(event)
        pass # TODO