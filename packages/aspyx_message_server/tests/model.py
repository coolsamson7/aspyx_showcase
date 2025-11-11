from dataclasses import dataclass

@dataclass()
class Money:
    currency : str
    value: int

@dataclass
class Turnaround:
    id : str
    flight_id : str
    num : int
    price: Money

@dataclass
class Flight:
    id : str
    iata : str