from pyramid.config import Configurator
from pyramid_views.views.base import RedirectView


def main(global_config, **settings):

    # Get the DB engine and configure the global DB session
    # engine = engine_from_config(settings, 'sqlalchemy.')
    # DBSession.configure(bind=engine)

    # Configure the static routing
    config = Configurator(settings=settings)

    config.add_route('artist_detail', 'detail/artist/{id}/', view=RedirectView.as_view())

    app = config.make_wsgi_app()
    return app