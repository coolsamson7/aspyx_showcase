from contextvars import ContextVar

from sqlalchemy.orm import Session

from aspyx.di import injectable
from aspyx.di.aop import around, advice, methods, classes, Invocation
from aspyx.reflection import Decorators

from .session_factory import SessionFactory

def transactional():
    def decorator(func):
        Decorators.add(func, transactional)
        return func #

    return decorator


_current_session: ContextVar[Session] = ContextVar("_current_session", default=None)

def get_current_session():
    return _current_session.get()

@advice
@injectable()
class TransactionalAdvice:
    # constructor

    def __init__(self, factory: SessionFactory):
        self.session_factory = factory

    # internal

    # advice

    @around(methods().decorated_with(transactional), classes().decorated_with(transactional))
    def call_transactional1(self, invocation: Invocation):
        outer = _current_session.get()
        if outer:
            return invocation.proceed()

        session = self.session_factory.create_session()
        token = _current_session.set(session)

        try:
            result = invocation.proceed()
            session.flush()
            session.commit()
            return result
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            _current_session.reset(token)