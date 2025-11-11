from typing import Optional

from aspyx.di import on_running
from aspyx.di.aop import advice, error, Invocation
from aspyx.exception import ExceptionManager, catch
from aspyx_service import implementation, AbstractComponent, HealthCheckManager, health, ChannelAddress, Server, \
    component_services
from aspyx_message_server.service import InterfaceComponent


@implementation()
@health("/health")
@advice
class InterfaceComponentImpl(AbstractComponent, InterfaceComponent):
    # constructor

    def __init__(self):
        super().__init__()

        self.health_check_manager : Optional[HealthCheckManager] = None
        self.exception_manager = ExceptionManager()

    # exception handler

    @catch()
    def catch_exception(self, exception: Exception):
        print("caught exception!")
        return exception

    # aspects

    @error(component_services(InterfaceComponent))
    def catch(self, invocation: Invocation):
        return self.exception_manager.handle(invocation.exception)

    # lifecycle

    @on_running()
    def setup_exception_handlers(self):
        self.exception_manager.collect_handlers(self)

    # implement

    async def get_health(self) -> HealthCheckManager.Health:
        return HealthCheckManager.Health()

    def get_addresses(self, port: int) -> list[ChannelAddress]:
        return [
            ChannelAddress("rest", f"http://{Server.get_local_ip()}:{port}"),
            ChannelAddress("dispatch-json", f"http://{Server.get_local_ip()}:{port}"),
        ]

    def startup(self) -> None:
        print("### startup")

    def shutdown(self) -> None:
        print("### shutdown")