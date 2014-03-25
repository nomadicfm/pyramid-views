#coding=utf-8
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    String,
    Boolean,
    DateTime,
    ColumnDefault,
    Float,
    Enum,
    func,
    UniqueConstraint,
    desc,
    distinct,
    alias,
    select,
    Unicode,
    UnicodeText,
    and_,
    Table)

from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
# Note that at the time of writing the existing production DB did not following
# this naming convention.
Base.metadata = MetaData()



# @python_2_unicode_compatible
# class Artist(models.Model):
#     name = models.CharField(max_length=100)
#
#     class Meta:
#         ordering = ['name']
#         verbose_name = 'professional artist'
#         verbose_name_plural = 'professional artists'
#
#     def __str__(self):
#         return self.name
#
#     def get_absolute_url(self):
#         return reverse('artist_detail', kwargs={'pk': self.id})
#
#

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
        return self.name


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
#
#
# class Page(models.Model):
#     content = models.TextField()
#     template = models.CharField(max_length=300)
#
#
# class BookSigning(models.Model):
#     event_date = models.DateTimeField()
