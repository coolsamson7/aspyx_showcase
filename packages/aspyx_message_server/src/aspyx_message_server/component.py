from abc import abstractmethod
from dataclasses import dataclass

from aspyx_service import component, Component, get, Service

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