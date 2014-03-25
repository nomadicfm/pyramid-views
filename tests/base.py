# coding=utf-8
import unittest
from pyramid import testing
from pyramid.config import Configurator
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from webtest import TestApp

Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
engine = create_engine('sqlite://')
Session.configure(bind=engine)
session = Session()

def app_main(global_config, **settings):
    config = Configurator(settings=settings)
    app = config.make_wsgi_app()
    return app

# Initialise the app globally to speed up testing
app = app_main({}, **{})


class BaseTest(unittest.TestCase):
    def setUp(self):
        super(BaseTest, self).setUp()
        from .models import Base
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        self.app = TestApp(app)
        self.config = testing.setUp()
        self.config.include('pyramid_jinja2')
        self.config.add_renderer('.html', 'pyramid_jinja2.renderer_factory')

    def tearDown(self):
        super(BaseTest, self).tearDown()
        testing.tearDown()

    def assertTemplateUsed(self, res, template_name):
        self.assertIn(template_name, res.template_names)

    def artist(self, name='Rene Magritte'):
        from .models import Artist
        session.add(Artist(name=name))

    def author(self, name=u'Roberto Bolaño', slug='roberto-bolano'):
        from .models import Author
        session.add(Author(name=name, slug=slug))

    def page(self, template=u'tests:templates/page_template.html', content='I was once bitten by a moose'):
        from .models import Page
        session.add(Page(template=template, content=content))