from dataclasses import dataclass
from typing import List

import uuid


@dataclass()
class InterfaceHandlerDTO:
    id : uuid.UUID
    version_id : int
    sink: str
    format: str
    args: str
    template: str

@dataclass()
class OnEventDTO:
    id : uuid.UUID
    version_id : int
    event: str
    filter: str
    handlers : List[InterfaceHandlerDTO]

