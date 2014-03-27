from chameleon.zpt.template import Macro
from pyramid import httpexceptions
from pyramid.testing import DummyRequest

from pyramid_views.utils import ImproperlyConfigured
from pyramid_views.views.base import View

from tests.base import BaseTest
from tests import views
from tests.models import Session, Author, Page


class DetailViewTest(BaseTest):

    def test_simple_object(self):
        view = views.ObjectDetail.as_view()
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], {'foo': 'bar'})
        self.assertIsInstance(res.context['view'], View)
        self.assertIsInstance(res.context['macros']['my_macros']['testmacro'], Macro)
        self.assertTemplateUsed(res, 'tests:templates/detail.html')

    def test_detail_by_pk(self):
        self.author()
        view = views.AuthorDetail.as_view()
        res = view(DummyRequest(), pk=1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Session.query(Author).filter(Author.id==1).one())
        self.assertEqual(res.context['author'], Session.query(Author).filter(Author.id==1).one())
        self.assertTemplateUsed(res, 'tests:templates/author_detail.html')

    def test_detail_missing_object(self):
        view = views.AuthorDetail.as_view()
        self.assertRaises(httpexceptions.HTTPNotFound, view, DummyRequest(), pk=500)

    def test_detail_object_does_not_exist(self):
        self.author()
        # ObjectDoesNotExistDetail uses get_query() to return an empty query
        view = views.ObjectDoesNotExistDetail.as_view()
        self.assertRaises(httpexceptions.HTTPNotFound, view, DummyRequest(), pk=1)

    def test_detail_by_custom_pk(self):
        self.author()
        view = views.AuthorDetail.as_view(pk_url_kwarg='foo')
        res = view(DummyRequest(), foo=1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Session.query(Author).filter(Author.id==1).one())
        self.assertEqual(res.context['author'], Session.query(Author).filter(Author.id==1).one())
        self.assertTemplateUsed(res, 'tests:templates/author_detail.html')

    def test_detail_by_slug(self):
        self.author()
        self.author(name='Scott Rosenberg', slug='scott-rosenberg')
        view = views.AuthorDetail.as_view()
        res = view(DummyRequest(), slug='scott-rosenberg')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Session.query(Author).filter(Author.slug=='scott-rosenberg').one())
        self.assertEqual(res.context['author'], Session.query(Author).filter(Author.slug=='scott-rosenberg').one())
        self.assertTemplateUsed(res, 'tests:templates/author_detail.html')

    def test_detail_by_custom_slug(self):
        self.author()
        self.author(name='Scott Rosenberg', slug='scott-rosenberg')
        view = views.AuthorDetail.as_view(slug_url_kwarg='foo')
        res = view(DummyRequest(), foo='scott-rosenberg')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Session.query(Author).filter(Author.slug=='scott-rosenberg').one())
        self.assertEqual(res.context['author'], Session.query(Author).filter(Author.slug=='scott-rosenberg').one())
        self.assertTemplateUsed(res, 'tests:templates/author_detail.html')

    def test_template_name(self):
        self.author()
        view = views.AuthorDetail.as_view(template_name='tests:templates/about.html')
        res = view(DummyRequest(), pk=1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Session.query(Author).filter(Author.id==1).one())
        self.assertEqual(res.context['author'], Session.query(Author).filter(Author.id==1).one())
        self.assertTemplateUsed(res, 'tests:templates/about.html')

    def test_template_name_suffix(self):
        self.author()
        view = views.AuthorDetail.as_view(template_name_suffix='_view')
        res = view(DummyRequest(), pk=1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Session.query(Author).filter(Author.id==1).one())
        self.assertEqual(res.context['author'], Session.query(Author).filter(Author.id==1).one())
        self.assertTemplateUsed(res, 'tests:templates/author_view.html')

    def test_template_name_field(self):
        self.page()
        view = views.PageDetail.as_view()
        res = view(DummyRequest(), pk=1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Session.query(Page).filter(Page.id==1).one())
        self.assertEqual(res.context['page'], Session.query(Page).filter(Page.id==1).one())
        self.assertTemplateUsed(res, 'tests:templates/page_template.html')

    def test_context_object_name(self):
        self.author()
        view = views.AuthorDetail.as_view(context_object_name='thingy')
        res = view(DummyRequest(), pk=1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Session.query(Author).filter(Author.id==1).one())
        self.assertEqual(res.context['thingy'], Session.query(Author).filter(Author.id==1).one())
        self.assertFalse('author' in res.context)
        self.assertTemplateUsed(res, 'tests:templates/author_detail.html')

    def test_duplicated_context_object_name(self):
        self.author()
        view = views.AuthorDetail.as_view(context_object_name='object')
        res = view(DummyRequest(), pk=1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Session.query(Author).filter(Author.id==1).one())
        self.assertFalse('author' in res.context)
        self.assertTemplateUsed(res, 'tests:templates/author_detail.html')

    def test_invalid_parameters(self):
        self.assertRaises(AttributeError, views.AuthorDetail.as_view(), DummyRequest())

    def test_invalid_query(self):
        self.assertRaises(ImproperlyConfigured, views.AuthorDetail.as_view(query=None), DummyRequest())

    def test_non_model_object_with_meta(self):
        view = views.NonModelDetail.as_view()
        res = view(DummyRequest(), pk=1)
        self.assertEqual(res.context['object'].id, "non_model_1")
