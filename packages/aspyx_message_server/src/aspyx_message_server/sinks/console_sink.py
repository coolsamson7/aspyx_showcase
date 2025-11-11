from aspyx_message_server import MessageSink, message_sink


@message_sink(name="console")
class MessageConsoleSink(MessageSink):
    # constructor

    def __init__(self):
        super().__init__(name="console")

    # implement

    def set_config(self, config: str):
        pass

    def send(self, message: str):
        pass #print(f"{self.name} received message: {message}")