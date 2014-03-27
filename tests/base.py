# coding=utf-8
from contextlib import contextmanager
import unittest
from pyramid import testing
from pyramid.config import Configurator
import six
from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from webtest import TestApp
from pyramid_views.views import MultipleObjectTemplateResponseMixin, SingleObjectTemplateResponseMixin
from pyramid_views import configure_views

Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
engine = create_engine('sqlite://')
Session.configure(bind=engine)
configure_views(Session)


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
        Session.expire_all()
        Session.flush()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        self.app = TestApp(app)
        self.config = testing.setUp()
        self.config.include('pyramid_jinja2')
        self.config.add_renderer('.html', 'pyramid_jinja2.renderer_factory')
        MultipleObjectTemplateResponseMixin.template_extension = '.html'
        SingleObjectTemplateResponseMixin.template_extension = '.html'

    def tearDown(self):
        super(BaseTest, self).tearDown()
        testing.tearDown()

    @contextmanager
    def assertNumQueries(self, num_queries):
        # Note that there is a bug with ``assertNumQueries()``
        # that requires the first query in a test to be wrapped
        # in a `assertNumQueries()`` context.

        statements = []
        def handle_query(conn, cursor, statement, parameters, *args, **kwargs):
            print statement + "\n"
            statements.append(statement)
        Session.flush()
        event.listen(engine, "before_cursor_execute", handle_query)
        yield
        Session.flush()
        event.remove(engine, "before_cursor_execute", handle_query)
        self.assertEqual(len(statements), num_queries, "Ran %s queries, expected %s" % (len(statements), num_queries))

    def assertTemplateUsed(self, res, template_name):
        self.assertIn(template_name, res.template_names)

    def assertRedirects(self, res, url, status_code=302):
        self.assertEqual(res.status_code, status_code,
                         "Invalid redirect status code %s, expected %s" % (res.status_code, status_code))
        self.assertEqual(res.headers['Location'], url)

    def assertQuerysetEqual(self, qs, values, transform=str, ordered=True):
        items = six.moves.map(transform, qs)
        if not ordered:
            return self.assertEqual(set(items), set(values))
        values = list(values)
        # For example qs.iterator() could be passed as qs, but it does not
        # have 'ordered' attribute.
        if len(values) > 1 and hasattr(qs, 'ordered') and not qs.ordered:
            raise ValueError("Trying to compare non-ordered query "
                             "against more than one ordered values")
        return self.assertEqual(list(items), values)

    def artist(self, name='Rene Magritte'):
        from .models import Artist
        artist = Artist(name=name)
        Session.add(artist)
        Session.flush()
        return artist

    def author(self, name=u'Roberto Bolaño', slug='roberto-bolano'):
        from .models import Author
        author = Author(name=name, slug=slug)
        Session.add(author)
        Session.flush()
        return author

    def page(self, template=u'tests:templates/page_template.html', content='I was once bitten by a moose'):
        from .models import Page
        page = Page(template=template, content=content)
        Session.add(page)
        Session.flush()
        return page