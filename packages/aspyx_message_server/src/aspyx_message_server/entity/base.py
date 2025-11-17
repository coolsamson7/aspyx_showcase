from sqlalchemy.orm import DeclarativeBase

from aspyx_message_server.persistence import PersistentUnit


class Base(DeclarativeBase):
    pass

#@injectable()
class BasePersistentUnit(PersistentUnit):
    def __init__(self, url: str):
        super().__init__(url=url, declarative_base=Base)