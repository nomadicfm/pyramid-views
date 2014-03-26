from sqlalchemy.orm import Query
from pyramid_views.paginator import Paginator
from pyramid_views.views.base import TemplateView, View
from pyramid_views.views import detail
from pyramid_views.views.detail import DetailView
from pyramid_views.views.edit import FormView, CreateView, ModelFormMixin, UpdateView, DeleteView
from pyramid_views.views.list import MultipleObjectMixin, ListView

from tests.models import Author, Book, Artist, Page
from tests.base import session
from tests.forms import ContactForm, AuthorForm


class CustomTemplateView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super(CustomTemplateView, self).get_context_data(**kwargs)
        context.update({'key': 'value'})
        return context


class ObjectDetail(DetailView):
    template_name = 'tests:templates/detail.html'

    def get_object(self):
        return {'foo': 'bar'}


class ArtistDetail(DetailView):
    query = Query(Artist)


class AuthorDetail(DetailView):
    query = Query(Author)


class PageDetail(DetailView):
    query = Query(Page)
    template_name_field = 'template'


class DictList(ListView):
    """A ListView that doesn't use a model."""
    query = [
        {'first': 'John', 'last': 'Lennon'},
        {'first': 'Yoko', 'last': 'Ono'}
    ]
    template_name = 'tests:templates/list.html'


class ArtistList(ListView):
    template_name = 'tests:templates/list.html'
    query = Query(Artist)


class AuthorList(ListView):
    query = Query(Author)


class CustomPaginator(Paginator):
    def __init__(self, query, page_size, orphans=0, allow_empty_first_page=True):
        super(CustomPaginator, self).__init__(
            query,
            page_size,
            orphans=2,
            allow_empty_first_page=allow_empty_first_page)


class AuthorListCustomPaginator(AuthorList):
    paginate_by = 5

    def get_paginator(self, query, page_size, orphans=0, allow_empty_first_page=True):
        return super(AuthorListCustomPaginator, self).get_paginator(
            query,
            page_size,
            orphans=2,
            allow_empty_first_page=allow_empty_first_page)


class ContactView(FormView):
    form_class = ContactForm
    success_url = '/list/authors/'
    template_name = 'tests:templates/form.html'


class ArtistCreate(CreateView):
    model = Artist


class NaiveAuthorCreate(CreateView):
    query = Query(Author)


class TemplateResponseWithoutTemplate(detail.SingleObjectTemplateResponseMixin, View):
    # we don't define the usual template_name here

    def __init__(self):
        # Dummy object, but attr is required by get_template_name()
        self.object = None


class AuthorCreate(CreateView):
    model = Author
    success_url = '/list/authors/'


class SpecializedAuthorCreate(CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'tests:templates/form.html'
    context_object_name = 'thingy'

    def get_success_url(self):
        return '/detail/author/%d/' % self.object.id


# class AuthorCreateRestricted(AuthorCreate):
#     post = method_decorator(login_required)(AuthorCreate.post)
#

class ArtistUpdate(UpdateView):
    model = Artist


class NaiveAuthorUpdate(UpdateView):
    query = Query(Author)


class AuthorUpdate(UpdateView):
    model = Author
    success_url = '/list/authors/'


class OneAuthorUpdate(UpdateView):
    success_url = '/list/authors/'

    def get_object(self, query=None):
        return session.query(Author).filter(Author.id==1).one()


class SpecializedAuthorUpdate(UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = 'tests:templates/form.html'
    context_object_name = 'thingy'

    def get_success_url(self):
        return '/detail/author/%d/' % self.object.id


class NaiveAuthorDelete(DeleteView):
    query = Query(Author)


class AuthorDelete(DeleteView):
    model = Author
    success_url = '/list/authors/'


class SpecializedAuthorDelete(DeleteView):
    query = Query(Author)
    template_name = 'tests:templates/confirm_delete.html'
    context_object_name = 'thingy'

    def get_success_url(self):
        return '/list/authors/'


# class BookConfig(object):
#     query = Book.objects.all()
#     date_field = 'pubdate'
#
#
# class BookArchive(BookConfig, generic.ArchiveIndexView):
#     pass
#
#
# class BookYearArchive(BookConfig, generic.YearArchiveView):
#     pass
#
#
# class BookMonthArchive(BookConfig, generic.MonthArchiveView):
#     pass
#
#
# class BookWeekArchive(BookConfig, generic.WeekArchiveView):
#     pass
#
#
# class BookDayArchive(BookConfig, generic.DayArchiveView):
#     pass
#
#
# class BookTodayArchive(BookConfig, generic.TodayArchiveView):
#     pass
#
#
# class BookDetail(BookConfig, generic.DateDetailView):
#     pass
#
#
# class BookDetailGetObjectCustomQueryset(BookDetail):
#     def get_object(self, query=None):
#         return super(BookDetailGetObjectCustomQueryset, self).get_object(
#             query=Book.objects.filter(pk=2))


class AuthorGetQueryFormView(ModelFormMixin):

    def get_query(self):
        return Query(Author)


class CustomMultipleObjectMixinView(MultipleObjectMixin, View):
    query = [
        {'name': 'John'},
        {'name': 'Yoko'},
    ]

    def get(self, request):
        self.object_list = self.get_query()


class CustomContextView(detail.SingleObjectMixin, View):
    model = Book
    object = Book(name='dummy')

    def get_object(self):
        return Book(name="dummy")

    def get_context_data(self, **kwargs):
        context = {'custom_key': 'custom_value'}
        context.update(kwargs)
        return super(CustomContextView, self).get_context_data(**context)

    def get_context_object_name(self, obj):
        return "test_name"


class CustomSingleObjectView(detail.SingleObjectMixin, View):
    model = Book
    object = Book(name="dummy")


# class BookSigningConfig(object):
#     model = BookSigning
#     date_field = 'event_date'
#     # use the same templates as for books
#
#     def get_template_names(self):
#         return ['book%s.html' % self.template_name_suffix]
#
#
# class BookSigningArchive(BookSigningConfig, generic.ArchiveIndexView):
#     pass
#
#
# class BookSigningYearArchive(BookSigningConfig, generic.YearArchiveView):
#     pass
#
#
# class BookSigningMonthArchive(BookSigningConfig, generic.MonthArchiveView):
#     pass
#
#
# class BookSigningWeekArchive(BookSigningConfig, generic.WeekArchiveView):
#     pass
#
#
# class BookSigningDayArchive(BookSigningConfig, generic.DayArchiveView):
#     pass
#
#
# class BookSigningTodayArchive(BookSigningConfig, generic.TodayArchiveView):
#     pass
#
#
# class BookSigningDetail(BookSigningConfig, generic.DateDetailView):
#     context_object_name = 'book'


class NonModel(object):
    id = "non_model_1"

    _meta = None


class NonModelDetail(DetailView):
    template_name = 'tests:templates/detail.html'
    model = NonModel

    def get_object(self, query=None):
        return NonModel()


class ObjectDoesNotExistDetail(DetailView):
    def get_query(self):
        return Query(Book).filter(Book.id==123)