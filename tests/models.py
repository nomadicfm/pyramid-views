#coding=utf-8
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    DateTime,
    Unicode,
    UnicodeText,
    Table)
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from tests.base import Session

Base = declarative_base()
Base.metadata = MetaData()


class Artist(Base):
    __tablename__ = 'artist'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100))

    class Meta:
        ordering = ['name']
        verbose_name = 'professional artist'
        verbose_name_plural = 'professional artists'

    def __str__(self):
        return u'<Artist: %s>' % self.name

    def get_absolute_url(self):
        return '/detail/artist/%d/' % self.id

book_authors_table = Table('book_authors', Base.metadata,
    Column('book_id', Integer, ForeignKey('book.id')),
    Column('author_id', Integer, ForeignKey('author.id')),
)

class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100))
    slug = Column(Unicode(50))

    def __str__(self):
        return u'<Author: %s>' % self.name


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(300))
    slug = Column(Unicode(50))
    pages = Column(Unicode(100))

    authors = relationship('Author',
                           secondary=book_authors_table,
                           backref='books')
    pubdate = Column(DateTime)

    # does_not_exist = DoesNotExistBookManager()

    def __str__(self):
        return self.name


class Page(Base):
    __tablename__ = 'page'
    id = Column(Integer, primary_key=True)
    content = Column(UnicodeText())
    template = Column(Unicode(300))


class BookSigning(Base):
    __tablename__ = 'book_signing'
    id = Column(Integer, primary_key=True)
    event_date = Column(DateTime())
