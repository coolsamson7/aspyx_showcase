from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from aspyx.di import injectable, inject


@dataclass()
class Weather:
    degree : int

class WeatherProvider(ABC):
    @abstractmethod
    def get_weather(self) -> Weather:
        pass



@injectable()
class WeatherManager:
    # properties

    weather : Weather = Weather(degree=0)
    providers: List[WeatherProvider] = []

    # constructor

    def __init__(self):
        pass

    # public

    def register(self, provider: WeatherProvider):
        self.providers.append(provider)

    def get_weather(self):
        return self.weather

    # job

    @scheduled(trigger=cron(second="0-59"), group="group", max=1)
    def poll_providers(self):
        for provider in self.providers:
            self.weather = provider.get_weather()


class AbstractWeatherProvider(WeatherProvider):
    @inject()
    def inject_manager(self, manager: WeatherManager):
        manager.register(self)

@injectable()
class SampleWeatherProvider(AbstractWeatherProvider):
    # implement

    def get_weather(self) -> Weather:
        return Weather(degree=0)