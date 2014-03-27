from sqlalchemy import (
    Column,
    Index,
    Integer,
    UnicodeText,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    title = Column(UnicodeText)
    author_name = Column(UnicodeText)
