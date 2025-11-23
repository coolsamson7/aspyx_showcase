
from typing import Optional

from aspyx.di import on_running
from aspyx.di.aop import advice, error, Invocation
from aspyx.exception import ExceptionManager, catch
from aspyx_service import  health, AbstractComponent, \
    HealthCheckManager, component_services, ChannelAddress, Server

from aspyx_service import  implementation
from aspyx_message_server.component import WeatherComponent, WeatherService
from aspyx_message_server.weather import WeatherManager
from aspyx_message_server.weather.weather_manager import Weather


@implementation()
class WeatherServiceServiceImpl(WeatherService):
    # constructor

    def __init__(self, weather_manager: WeatherManager):
        self.weather_manager = weather_manager

    # implement WeatherService

    def get_weather(self) -> Weather:
        return self.weather_manager.get_weather()

@implementation()
@health("/weather/health")
@advice
class WeatherComponentImpl(AbstractComponent, WeatherComponent):
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

    @error(component_services(WeatherComponent))
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