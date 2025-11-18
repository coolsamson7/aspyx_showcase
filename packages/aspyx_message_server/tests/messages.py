from dataclasses import dataclass

from aspyx_event import event
from .model import Turnaround

@dataclass
@event(durable=False)
class TurnaroundEvent:
    turnaround: Turnaround