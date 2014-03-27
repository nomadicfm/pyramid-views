from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    Session,
    Base,
    )

from . import views
from pyramid_views.views import TemplateView
from pyramid_views import configure_views
from pyramid_views.views.base import RedirectView


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    configure_views(Session)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/', views.HomeView.as_view())
    config.add_route('about', '/about', TemplateView.as_view(template_name='example_project:templates/about.pt'))
    config.add_route('book_list_redirect', '/book', RedirectView.as_view(url='/book/list', permanent=True))
    config.add_route('book_list', '/book/list', views.BookListView.as_view())
    config.add_route('book_update', '/book/update/{pk}', views.BookUpdateView.as_view())
    config.add_route('book_delete', '/book/delete/{pk}', views.BookDeleteView.as_view())
    config.add_route('book_create', '/book/create', views.BookCreateView.as_view())

    return config.make_wsgi_app()
