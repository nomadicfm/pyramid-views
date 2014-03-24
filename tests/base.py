import unittest
from pyramid import testing
from pyramid.config import Configurator
from webtest import TestApp


def app_main(global_config, **settings):
    config = Configurator(settings=settings)
    app = config.make_wsgi_app()
    return app

# Initialise the app globally to speed up testing
app = app_main({}, **{})

class BaseTest(unittest.TestCase):
    def setUp(self):
        super(BaseTest, self).setUp()
        self.app = TestApp(app)
        self.config = testing.setUp()
        self.config.include('pyramid_jinja2')
        self.config.add_renderer('.html', 'pyramid_jinja2.renderer_factory')

    def tearDown(self):
        super(BaseTest, self).tearDown()
        testing.tearDown()
