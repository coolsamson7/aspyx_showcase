from typing import Optional

from aspyx.di import injectable
from aspyx.mapper import Mapper
from aspyx_message_server.persistence import BaseRepository, query
from aspyx_message_server.entity import OnEventEntity, InterfaceHandlerEntity


@injectable()
class OnEventRepository(BaseRepository[OnEventEntity]):
    # constructor

    def __init__(self):
        super().__init__(OnEventEntity)

    # public

    @query()
    def find_by_event(self):
        ...

    def find_by_id(self, id: str, mapper: Optional[Mapper] = None):
        return self.find(id, mapper=mapper)

@injectable()
class OnInterfaceHandlerRepository(BaseRepository[InterfaceHandlerEntity]):
    # constructor

    def __init__(self):
        super().__init__(InterfaceHandlerEntity)

    # public

    @query()
    def find_by_sink(self):
        ...

    def find_by_id(self, id: str, mapper: Optional[Mapper] = None):
        return self.find(id, mapper=mapper)