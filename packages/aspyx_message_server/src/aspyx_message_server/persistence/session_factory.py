from sqlalchemy.orm import sessionmaker

from aspyx.di import injectable
from .engine_factory import EngineFactory

@injectable()
class SessionFactory:
    def __init__(self, engine: EngineFactory):
        self._maker = sessionmaker(bind=engine.get_engine(), autoflush=False, autocommit=False)

    def create_session(self):
        return self._maker()