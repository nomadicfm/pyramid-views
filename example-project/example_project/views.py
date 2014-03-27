from pyramid.renderers import get_renderer
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError
from example_project.models import Book

from .models import (
    Session,
    Book,
    )
from pyramid_views import views


class HomeView(views.TemplateView):
    template_name = 'example_project:templates/home.pt'

    def get(self, request, *args, **kwargs):
        # Check the DB has been initialised
        try:
            Session.query(Book).count()
            return super(HomeView, self).get(request, *args, **kwargs)
        except DBAPIError:
            return Response(conn_err_msg, content_type='text/plain', status_int=500)

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update(
            book_count=Session.query(Book).count(),
        )
        return context


class BookListView(views.ListView):
    model = Book


class BookUpdateView(views.UpdateView):
    model = Book
    success_url = '/book/list'
    macro_names = {
        'forms': 'pyramid_views:macros/forms.pt',
    }


class BookDeleteView(views.DeleteView):
    model = Book
    success_url = '/book/list'
    macro_names = {
        'forms': 'pyramid_views:macros/forms.pt',
    }


class BookCreateView(views.CreateView):
    model = Book
    success_url = '/book/list'
    macro_names = {
        'forms': 'pyramid_views:macros/forms.pt',
    }


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_example_project_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

