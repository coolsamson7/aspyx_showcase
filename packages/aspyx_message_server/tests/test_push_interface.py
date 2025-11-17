"""
test for events
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path

import pytest

from aspyx.di.configuration import YamlConfigurationSource
from aspyx.exception import ExceptionManager, catch
from aspyx.util import Logger
from aspyx_event import EventManager, event_listener, EventListener  # , StompProvider, AMQPProvider

from aspyx.di import module, Environment, create
from aspyx_service import ServiceModule, SessionManager
from aspyx_service.service import LocalComponentRegistry, ServiceManager

from aspyx_message_server.entity.base import BasePersistentUnit
from aspyx_message_server import MessageDispatcher, PushInterfaceModule
from aspyx_message_server.compiler.compiler import TypedFunction
from aspyx_message_server.message_dispatcher import message, forward
from aspyx_message_server.model import OnEventDTO, InterfaceHandlerDTO
from aspyx_message_server.service import InterfaceService

from .messages import TurnaroundEvent
from .model import Turnaround, Money, Flight
from .setup import LocalProvider

# setup logger

Logger.configure(default_level=logging.INFO, levels={
    "httpx": logging.ERROR,
    "aspyx.di": logging.INFO,
    "aspyx.event": logging.INFO,
    "aspyx.di.aop": logging.INFO,
    "aspyx.service": logging.INFO
})

logger = logging.getLogger("test")

logger.setLevel(logging.INFO)

# listener

loops = 1000

@event_listener(TurnaroundEvent, per_process=True)
class AsyncListener(EventListener[TurnaroundEvent]):
    messages = 0
    done_event = asyncio.Event()

    # constructor

    def __init__(self, dispatcher: MessageDispatcher):
        self.dispatcher = dispatcher

    # implement

    async def on(self, event: TurnaroundEvent):
        AsyncListener.messages +=  1

        self.dispatcher.dispatch(event.turnaround)

        if AsyncListener.messages >= loops:
            AsyncListener.done_event.set()

# test module

@module(imports=[PushInterfaceModule, ServiceModule])
class Module:
    # constructor

    def __init__(self, message_dispatcher: MessageDispatcher):
        self.message_dispatcher = message_dispatcher

        # register some functions

        message_dispatcher.register_functions({
            "flight": TypedFunction(lambda id: Flight(id=id, iata=id+"iata"), [str], Flight)
        })

        # listen to messages

        message_dispatcher.listen_to(
            # turnaround event

            message(Turnaround)
                .filter("num < 1000")
                # test json
                .handle(
                    forward("console")
                        .format("json")
                        .args({"foo": "bar"}) # {"url": "http://..."}
                        .template({
                            "turnaround": {
                                "id": "id",
                                "currency": "price.currency",
                                "flight": {
                                    "iata": "flight(flight_id).iata",
                                    "blu": "length(flight(flight_id).iata)",
                                    "num": "2 * num"
                                }
                            }
                        }
                        )
                )
                # test xml
                .handle(
                    forward("console")
                        .format("xml")
                        .args({"foo": "bar"}) # {"url": "http://..."}
                        .template({
                            "turnaround": {
                                "id": "id",
                                "currency": "price.currency",
                                "flight": {
                                    "_attributes": {
                                        "iata": "flight(flight_id).iata",
                                        "blu": "length(flight(flight_id).iata)",
                                        "num": "2 * num"
                                    }
                                }
                            }
                        }
                    )
                )
        )

    # handlers

    @catch()
    def handle_exception(self, exception: Exception):
        print(exception)

    # internal

    @create()
    def create_session_storage(self) -> SessionManager.Storage:
        return SessionManager.InMemoryStorage(max_size=1000, ttl=3600)

    @create()
    def create_yaml_source(self) -> YamlConfigurationSource:
        return YamlConfigurationSource(f"{Path(__file__).parent}/config.yaml")

    @create()
    def create_component_registry(self) -> LocalComponentRegistry:
        return LocalComponentRegistry()

    @create()
    def create_persistent_unit(self) -> BasePersistentUnit:
        return BasePersistentUnit(url="postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")

    #@create()
    #def create_engine(self, engine_factory: EngineFactory) -> SessionFactory:
    #    return SessionFactory(engine_factory)

    def create_exception_manager(self):
        exception_manager = ExceptionManager()

        exception_manager.collect_handlers(self)

        return exception_manager

    @create()
    def create_event_manager(self) -> EventManager:
        return EventManager(LocalProvider(), exception_manager=self.create_exception_manager())
        # EventManager(StompProvider(host="localhost", port=61616, user="artemis", password="artemis"))
        # EventManager(AMQPProvider("server-id", host="localhost", port=5672, user="artemis", password="artemis"))

@pytest.fixture(scope="session")
def environment():
    environment = Environment(Module)  # start server

    yield environment

    environment.destroy()

from aspyx_message_server.entity import Base, OnEventEntity, InterfaceHandlerEntity


@pytest.mark.asyncio(scope="function")
class TestPushInterface:
    async def test_events(self, environment):
        event_manager = environment.get(EventManager)

        all_entities = [mapper.class_ for mapper in Base.registry.mappers]

        for entity in all_entities:
            print(entity.__name__)

        # create schema

        #PersistentUnit.get_persistent_unit(BasePersistentUnit).create_all()

        # create entities

        service_manager = environment.get(ServiceManager)

        interface_service = service_manager.get_service(InterfaceService, preferred_channel="local")

        if False:
            on_event = interface_service.create_on_event(OnEventDTO(
                id = uuid.uuid4(),
                version_id=1,
                event = "Turnaround",
                filter="num > 5",
                handlers=[
                    InterfaceHandlerDTO(
                        id=uuid.uuid4(),
                        version_id=1,
                        sink="console",
                        format="json",
                        args="{}",
                        template='{\
                            "turnaround": {\
                                "id": "id",\
                                "currency": "price.currency",\
                                "flight": {\
                                    "iata": "flight(flight_id).iata",\
                                    "blu": "length(flight(flight_id).iata)",\
                                    "num": "2 * num"\
                                }\
                            }\
                        }'
                    )
                ]
            ))

        # reread

        result = interface_service.read_on_events()[0]

        result.handlers.append( InterfaceHandlerDTO(
            id=uuid.uuid4(),
            version_id=1,
            sink="console",
            format="json",
            args="{}",
            template='{\
                            "turnaround": {\
                                "id": "id",\
                                "currency": "price.currency",\
                                "flight": {\
                                    "iata": "flight(flight_id).iata",\
                                    "blu": "length(flight(flight_id).iata)",\
                                    "num": "2 * num"\
                                }\
                            }\
                        }'
        ))

        #interface_service.update_on_event(result)

        # send some events

        # Record start time using asyncio event loop’s monotonic clock
        start_time = asyncio.get_running_loop().time()

        AsyncListener.done_event = asyncio.Event()

        for i in range(loops):
            event = TurnaroundEvent(turnaround=Turnaround(id="1", num=0, flight_id="1", price=Money(currency="EUR", value=1)))

            event_manager.send_event(event) # should filter

        await AsyncListener.done_event.wait()

        # Record end time

        end_time = asyncio.get_running_loop().time()

        total_time = end_time - start_time
        avg_time = total_time / loops if loops else 0

        print(f"Total time for {loops} messages: {total_time:.4f} seconds")
        print(f"Average time per message: {avg_time:.6f} seconds")


