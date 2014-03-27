from __future__ import unicode_literals

from unittest import skip
from chameleon.zpt.template import Macro
from pyramid import httpexceptions
from pyramid.testing import DummyRequest

from pyramid_views.utils import ImproperlyConfigured
from pyramid_views.views.base import View

from tests.models import Author, Artist
from tests import views
from tests.base import BaseTest, Session


class ListViewTests(BaseTest):

    def test_items(self):
        # res = self.client.get('/list/dict/')
        view = views.DictList.as_view()
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'tests:templates/list.html')
        self.assertEqual(res.context['object_list'][0]['first'], 'John')

    def test_query(self):
        view = views.AuthorList.as_view()
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'tests:templates/author_list.html')
        self.assertEqual(list(res.context['object_list']), list(Session.query(Author).all()))
        self.assertIsInstance(res.context['view'], View)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertIsNone(res.context['paginator'])
        self.assertIsNone(res.context['page_obj'])
        self.assertFalse(res.context['is_paginated'])
        self.assertIsInstance(res.context['macros']['my_macros']['testmacro'], Macro)

    def test_paginated_query(self):
        self._make_authors(100)
        view = views.AuthorList.as_view(paginate_by=30)
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'tests:templates/author_list.html')
        self.assertEqual(len(res.context['object_list']), 30)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertTrue(res.context['is_paginated'])
        self.assertEqual(res.context['page_obj'].number, 1)
        self.assertEqual(res.context['paginator'].num_pages, 4)
        self.assertEqual(res.context['author_list'][0].name, 'Author 00')
        self.assertEqual(list(res.context['author_list'])[-1].name, 'Author 29')

    def test_paginated_query_shortdata(self):
        # Test that short datasets ALSO result in a paginated view.
        self.author()
        view = views.AuthorList.as_view(paginate_by=30)
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'tests:templates/author_list.html')
        self.assertEqual(list(res.context['object_list']), list(Session.query(Author).all()))
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['page_obj'].number, 1)
        self.assertEqual(res.context['paginator'].num_pages, 1)
        self.assertFalse(res.context['is_paginated'])

    def test_paginated_get_page_by_query_string(self):
        self._make_authors(100)
        view = views.AuthorList.as_view(paginate_by=30)
        res = view(DummyRequest(params={'page': '2'}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'tests:templates/author_list.html')
        self.assertEqual(len(res.context['object_list']), 30)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['author_list'][0].name, 'Author 30')
        self.assertEqual(res.context['page_obj'].number, 2)

    def test_paginated_get_last_page_by_query_string(self):
        self._make_authors(100)
        view = views.AuthorList.as_view(paginate_by=30)
        res = view(DummyRequest(params={'page': 'last'}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['object_list']), 10)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['author_list'][0].name, 'Author 90')
        self.assertEqual(res.context['page_obj'].number, 4)

    def test_paginated_get_page_by_urlvar(self):
        self._make_authors(100)
        view = views.AuthorList.as_view(paginate_by=30)
        res = view(DummyRequest(), page=3)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'tests:templates/author_list.html')
        self.assertEqual(len(res.context['object_list']), 30)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['author_list'][0].name, 'Author 60')
        self.assertEqual(res.context['page_obj'].number, 3)

    def test_paginated_page_out_of_range(self):
        self._make_authors(100)
        view = views.AuthorList.as_view(paginate_by=30)
        self.assertRaises(httpexceptions.HTTPNotFound, view, DummyRequest(), page=42)

    def test_paginated_invalid_page(self):
        self._make_authors(100)
        view = views.AuthorList.as_view(paginate_by=30)
        self.assertRaises(httpexceptions.HTTPNotFound, view, DummyRequest(params={'page': 'frog'}))

    def test_paginated_custom_paginator_class(self):
        self._make_authors(7)
        view = views.AuthorList.as_view(paginate_by=5, paginator_class=views.CustomPaginator)
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['paginator'].num_pages, 1)
        # Custom pagination allows for 2 orphans on a page size of 5
        self.assertEqual(len(res.context['object_list']), 7)

    def test_paginated_custom_page_kwarg(self):
        self._make_authors(100)
        view = views.AuthorList.as_view(paginate_by=30, page_kwarg='pagina')
        res = view(DummyRequest(params={'pagina': '2'}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'tests:templates/author_list.html')
        self.assertEqual(len(res.context['object_list']), 30)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['author_list'][0].name, 'Author 30')
        self.assertEqual(res.context['page_obj'].number, 2)

    def test_paginated_custom_paginator_constructor(self):
        self._make_authors(7)
        view = views.AuthorListCustomPaginator.as_view()
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        # Custom pagination allows for 2 orphans on a page size of 5
        self.assertEqual(len(res.context['object_list']), 7)

    def test_paginated_orphaned_query(self):
        self.assertEqual(Session.query(Author).count(), 0)
        self._make_authors(92)
        view = views.AuthorList.as_view(paginate_by=30, paginate_orphans=2)
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['page_obj'].number, 1)
        res = view(DummyRequest(params={'page': 'last'}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['page_obj'].number, 3)
        res = view(DummyRequest(params={'page': '3'}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['page_obj'].number, 3)
        self.assertRaises(httpexceptions.HTTPNotFound, view, DummyRequest(params={'page': '4'}))

    def test_paginated_non_query(self):
        view = views.DictList.as_view(paginate_by=1)
        res = view(DummyRequest())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['object_list']), 1)

    def test_verbose_name(self):
        self.author()
        view = views.ArtistList.as_view()
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'tests:templates/list.html')
        self.assertEqual(list(res.context['object_list']), list(Session.query(Artist).all()))
        self.assertIs(res.context['artist_list'], res.context['object_list'])
        self.assertIsNone(res.context['paginator'])
        self.assertIsNone(res.context['page_obj'])
        self.assertFalse(res.context['is_paginated'])

    def test_allow_empty_false(self):
        self.artist()
        view = views.ArtistList.as_view(allow_empty=False)
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        Session.query(Artist).delete()
        self.assertRaises(httpexceptions.HTTPNotFound, view, DummyRequest())

    def test_template_name(self):
        view = views.AuthorList.as_view(template_name='tests:templates/list.html')
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context['object_list']), list(Session.query(Author).all()))
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertTemplateUsed(res, 'tests:templates/list.html')

    def test_template_name_suffix(self):
        view = views.AuthorList.as_view(template_name_suffix='_objects')
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context['object_list']), list(Session.query(Author).all()))
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertTemplateUsed(res, 'tests:templates/author_objects.html')

    def test_context_object_name(self):
        view = views.AuthorList.as_view(context_object_name='author_list')
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context['object_list']), list(Session.query(Author).all()))
        self.assertNotIn('authors', res.context)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertTemplateUsed(res, 'tests:templates/author_list.html')

    def test_duplicate_context_object_name(self):
        view = views.AuthorList.as_view(context_object_name='object_list')
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context['object_list']), list(Session.query(Author).all()))
        self.assertNotIn('authors', res.context)
        self.assertNotIn('author_list', res.context)
        self.assertTemplateUsed(res, 'tests:templates/author_list.html')

    def test_missing_items(self):
        view = views.AuthorList.as_view(query=None)
        self.assertRaises(ImproperlyConfigured, view, DummyRequest())

    def test_paginate_by_no_allow_empty(self):
        self.author()
        view = views.AuthorList.as_view(allow_empty=False, paginate_by=2)
        res = view(DummyRequest())
        self.assertEqual(list(res.context['object_list']), list(Session.query(Author).all()))
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertTemplateUsed(res, 'tests:templates/author_list.html')

    @skip("SQLAlchemy lacks Django's ORM's implemention of exists().")
    def test_paginated_list_view_does_not_load_entire_table(self):
        # Regression test for #17535

        # Note that there is a bug with ``assertNumQueries()``
        # that requires the first query in a test to be wrapped
        # in a `assertNumQueries()`` context.

        with self.assertNumQueries(1):
            self._make_authors(1)
        # 1 query for authors
        # with self.assertNumQueries(1):
        #     view = views.AuthorList.as_view(allow_empty=False)
        #     view(DummyRequest())
        # same as above + 1 query to test if authors exist + 1 query for pagination
        with self.assertNumQueries(3):
            view = views.AuthorList.as_view(allow_empty=False, paginate_by=2)
            view(DummyRequest())

    def _make_authors(self, n):
        for i in range(n):
            self.author(name='Author %02i' % i, slug='a%s' % i)