
import uuid
import threading

from typing import List, Optional

from aspyx.mapper import Mapper, MappingDefinition, matching_properties
from aspyx.reflection import TypeDescriptor
from aspyx_event import EventManager
from aspyx_service import implementation
from aspyx_message_server.push_interfaces.message_event import UpdateMessagesEvent
from aspyx_message_server.push_interfaces.persistence import transactional, RelationSynchronizer, get_current_session
from aspyx_message_server.push_interfaces.entity import OnEventEntity, InterfaceHandlerEntity
from aspyx_message_server.push_interfaces.model.interface_dto import OnEventDTO, InterfaceHandlerDTO
from aspyx_message_server.push_interfaces.service import InterfaceService
from aspyx_message_server.push_interfaces.service.impl import OnEventRepository

@implementation()
class InterfaceServiceImpl(InterfaceService):
    # constructor

    def __init__(self, repository: OnEventRepository, event_manager: EventManager):
        self.repository = repository
        self.dto_to_entity_mapper : Optional[Mapper] = None
        self.entity_to_dto_mapper : Optional[Mapper] = None
        self.event_manager = event_manager

    # internal

    def schedule_later(self, func):
        threading.Timer(0, func).start()

    def get_dto_to_entity_mapper(self):
        desc = TypeDescriptor.for_type(OnEventEntity)
        desc1 = TypeDescriptor.for_type(InterfaceHandlerEntity)

        if self.dto_to_entity_mapper is None:
            self.dto_to_entity_mapper = Mapper(
    MappingDefinition(source=OnEventDTO, target=OnEventEntity)
                    .map(all=matching_properties().except_properties(["handlers"]))
                    .map(from_="handlers", to="handlers", deep=True),

                MappingDefinition(source=InterfaceHandlerDTO, target=InterfaceHandlerEntity)
                    .map(all=matching_properties())
            )

        return self.dto_to_entity_mapper

    def get_entity_to_dto_mapper(self):
        if self.entity_to_dto_mapper is None:
            self.entity_to_dto_mapper = Mapper(
                MappingDefinition(source=OnEventEntity, target=OnEventDTO)
                    .map(all=matching_properties().except_properties(["handlers"]))
                    .map(from_="handlers", to="handlers", deep=True),

                MappingDefinition(source=InterfaceHandlerEntity, target=InterfaceHandlerDTO)
                    .map(all=matching_properties())
            )

        return self.entity_to_dto_mapper

    # implement

    @transactional()
    def create_on_event(self, on_event: OnEventDTO) -> OnEventDTO:
        entity = self.repository.save(self.get_dto_to_entity_mapper().map(on_event))

        # make the dispatcher reload...

        self.schedule_later(lambda: self.event_manager.send_event(UpdateMessagesEvent()))

        # flush session

        get_current_session().flush()

        # return new dto

        return self.get_entity_to_dto_mapper().map(entity)

    @transactional()
    def read_on_event(self, id: uuid.UUID) -> OnEventDTO:
       return self.repository.find(id, mapper=self.get_entity_to_dto_mapper())

    @transactional()
    def read_on_events(self) -> List[OnEventDTO]:
        return self.repository.find_all(id, mapper=self.get_entity_to_dto_mapper())

    @transactional()
    def update_on_event(self, on_event: OnEventDTO) -> OnEventDTO:
        entity = self.repository.find(on_event.id)

        # TEST

        if on_event.version_id != entity.version_id:
            raise ValueError("version mismatch")

        # the mapper should handle that

        # as long as the mapper is not clever enough

        entity.event = on_event.event
        entity.filter = on_event.filter

        class HandlerSynchronizer(RelationSynchronizer[InterfaceHandlerDTO, InterfaceHandlerEntity, uuid.UUID]):
            def __init__(self, mapper):
                super().__init__(to_pk=lambda s: s.id, pk=lambda t: t.id)
                self.mapper = mapper

            def provide(self, source, context):
                return self.mapper.map(source, context=context)

            def update(self, target, source, context):
                self.mapper.map(source, target=target, context=context)

            def delete(self, entity: InterfaceHandlerEntity):
                """Called for deleted target entities."""
                pass

        HandlerSynchronizer(mapper=self.get_dto_to_entity_mapper()).synchronize(on_event.handlers, entity.handlers, None)

        # make the dispatcher reload...

        self.schedule_later(lambda: self.event_manager.send_event(UpdateMessagesEvent()))

        # make sure, the entities are flushed

        get_current_session().flush()

        # return new version counters

        return self.get_entity_to_dto_mapper().map(entity)

    @transactional()
    def delete_on_event(self, id: uuid.UUID):
        pass #TODO

    @transactional()
    def read_on_events(self) -> List[OnEventDTO]:
        return self.repository.find_all(mapper=self.get_entity_to_dto_mapper())
