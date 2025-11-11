from typing import Dict, Union

Config = Dict[str, Union[int, str, 'Config']]

class MessageSink:
    # constructor

    def __init__(self, name: str):
        self.name = name

    # abstract

    def set_config(self, config: Config):
        pass

    def send(self, message: str):
        pass