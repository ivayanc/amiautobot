from typing import ContextManager

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session

from configuration import DB_URL

Session = sessionmaker(expire_on_commit=False)
engine = create_engine(DB_URL, pool_size=15, max_overflow=30)
Session.configure(bind=engine)
current_session = scoped_session(Session)


@contextmanager
def session(**kwargs) -> ContextManager[Session]:
    """Provide a transactional scope around a series of operations."""
    new_session = Session(**kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception as e:
        print(str(e))
        new_session.rollback()
        raise
    finally:
        new_session.close()


class Base(DeclarativeBase):
    pass
