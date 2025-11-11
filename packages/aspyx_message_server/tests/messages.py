from dataclasses import dataclass

from aspyx_event import event
from packages.aspyx_message_server.tests.model import Turnaround

@dataclass
@event(durable=False)
class TurnaroundEvent:
    turnaround: Turnaround