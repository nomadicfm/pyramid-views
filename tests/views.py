from __future__ import unicode_literals

# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
# from django.core.urlresolvers import reverse, reverse_lazy
# from django.utils.decorators import method_decorator
# from django.views import generic

# from .test_forms import AuthorForm, ContactForm
from sqlalchemy.orm import Query
from .models import Author, Book, Artist, Page
from pyramid_views.paginator import Paginator
from pyramid_views.views.base import TemplateView, View
from pyramid_views.views import detail
from pyramid_views.views.detail import DetailView
from pyramid_views.views.edit import FormView, CreateView, ModelFormMixin
from pyramid_views.views.list import MultipleObjectMixin, ListView
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
    queryset = [
        {'first': 'John', 'last': 'Lennon'},
        {'first': 'Yoko', 'last': 'Ono'}
    ]
    template_name = 'tests:templates/list.html'


class ArtistList(ListView):
    template_name = 'tests:templates/list.html'
    queryset = Query(Artist)


class AuthorList(ListView):
    queryset = Query(Author)


class CustomPaginator(Paginator):
    def __init__(self, queryset, page_size, orphans=0, allow_empty_first_page=True):
        super(CustomPaginator, self).__init__(
            queryset,
            page_size,
            orphans=2,
            allow_empty_first_page=allow_empty_first_page)


class AuthorListCustomPaginator(AuthorList):
    paginate_by = 5

    def get_paginator(self, queryset, page_size, orphans=0, allow_empty_first_page=True):
        return super(AuthorListCustomPaginator, self).get_paginator(
            queryset,
            page_size,
            orphans=2,
            allow_empty_first_page=allow_empty_first_page)


class ContactView(FormView):
    form_class = ContactForm
    success_url = '/list/authors/'
    template_name = 'tests:templates/form.html'


class ArtistCreate(CreateView):
    model = Artist
    fields = '__all__'


class NaiveAuthorCreate(CreateView):
    query = Query(Author)
    fields = '__all__'


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
#
# class ArtistUpdate(generic.UpdateView):
#     model = Artist
#     fields = '__all__'
#
#
# class NaiveAuthorUpdate(generic.UpdateView):
#     queryset = Author.objects.all()
#     fields = '__all__'
#
#
# class AuthorUpdate(generic.UpdateView):
#     model = Author
#     success_url = '/list/authors/'
#     fields = '__all__'
#
#
# class OneAuthorUpdate(generic.UpdateView):
#     success_url = '/list/authors/'
#     fields = '__all__'
#
#     def get_object(self):
#         return Author.objects.get(pk=1)
#
#
# class SpecializedAuthorUpdate(generic.UpdateView):
#     model = Author
#     form_class = AuthorForm
#     template_name = 'form.html'
#     context_object_name = 'thingy'
#
#     def get_success_url(self):
#         return reverse('author_detail', args=[self.object.id])
#
#
# class NaiveAuthorDelete(generic.DeleteView):
#     queryset = Author.objects.all()
#
#
# class AuthorDelete(generic.DeleteView):
#     model = Author
#     success_url = '/list/authors/'
#
#
# class SpecializedAuthorDelete(generic.DeleteView):
#     queryset = Author.objects.all()
#     template_name = 'confirm_delete.html'
#     context_object_name = 'thingy'
#
#     def get_success_url(self):
#         return reverse('authors_list')
#
#
# class BookConfig(object):
#     queryset = Book.objects.all()
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
class AuthorGetQuerySetFormView(ModelFormMixin):
    fields = '__all__'

    def get_query(self):
        return Query(Author)

#
# class BookDetailGetObjectCustomQueryset(BookDetail):
#     def get_object(self, queryset=None):
#         return super(BookDetailGetObjectCustomQueryset, self).get_object(
#             queryset=Book.objects.filter(pk=2))
#
#
class CustomMultipleObjectMixinView(MultipleObjectMixin, View):
    queryset = [
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

#
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
#
#
class NonModel(object):
    id = "non_model_1"

    _meta = None


class NonModelDetail(DetailView):
    template_name = 'tests:templates/detail.html'
    model = NonModel

    def get_object(self, queryset=None):
        return NonModel()


class ObjectDoesNotExistDetail(DetailView):
    def get_query(self):
        return Query(Book).filter(Book.id==123)