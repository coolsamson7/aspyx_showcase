from abc import abstractmethod

from aspyx_service import component, Component, get, Service

from .weather.weather_manager import Weather


class  WeatherService(Service):
    @abstractmethod
    @get("weather")
    def get_weather(self) -> Weather:
        pass

@component(services =[
    WeatherService,
])
class WeatherComponent(Component): # pylint: disable=abstract-method
    pass