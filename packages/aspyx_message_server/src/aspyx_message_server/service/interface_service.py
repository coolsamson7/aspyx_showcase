from abc import abstractmethod, ABC

import uuid
from typing import List

from aspyx_service import service, Service
from aspyx_message_server.model.interface_dto import OnEventDTO


@service(name="interface-service", description="crud service for interfaces")
class InterfaceService(Service):
    # methods

    @abstractmethod
    def create_on_event(self, on_event: OnEventDTO) -> OnEventDTO:
        pass

    @abstractmethod
    def read_on_event(self, id: uuid.UUID) -> OnEventDTO:
        pass

    @abstractmethod
    def read_on_events(self) -> List[OnEventDTO]:
        pass

    @abstractmethod
    def update_on_event(self, on_event: OnEventDTO) -> OnEventDTO:
        pass

    @abstractmethod
    def delete_on_event(self, id: uuid.UUID):
        pass

    @abstractmethod
    def read_on_events(self) -> List[OnEventDTO]:
        pass