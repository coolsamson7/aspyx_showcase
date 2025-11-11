
from sqlalchemy import create_engine

#@injectable()
class EngineFactory:
    def __init__(self, url: str):
        self.engine = create_engine(url, echo=False, future=True)

    def get_engine(self):
        return self.engine